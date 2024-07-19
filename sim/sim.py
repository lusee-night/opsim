# foundation packages
import  simpy
import  yaml
import  h5py

# local packages
from    hardware        import *
from    utils.timeconv  import *
from    nav             import *  # Astro/observation wrapper classes

#################################################################################
class Monitor():
    ''' The Monitor class is used to record the time series of the parameters of choice,
        as the simulation is progressing through time steps.
    '''

    def __init__(self, size=0):
        ''' Initialize arrays for time series type of data
        '''

        self.power      = np.zeros(size, dtype=float) # Total power drawn by the electronics
        self.battery_SOC= np.zeros(size, dtype=float) # Battery charge
        self.battery_V  = np.zeros(size, dtype=float) # Battery voltage
        self.data_rate  = np.zeros(size, dtype=float) # data rate in/out of the system
        self.ssd        = np.zeros(size, dtype=float) # Amount of data in the storage device
        self.boxtemp    = np.zeros(size, dtype=float) # temperature from thermal 

# ---
class Simulator:
    def __init__(self, orbitals_f=None, modes_f=None, devices_f=None, comtable_f=None, initial_time=None, until=None, verbose=False):
    
        # Will be read from the "devices" file later, create placeholders:
        self.battery_config = None
        self.ssd_config     = None
        self.thermal_config = None
        self.panel_config   = None

        self.verbose    = verbose
        self.record     = {} # stub for the record of state transitions

        # Filenames, to access the input data
        self.orbitals_f = orbitals_f
        self.modes_f    = modes_f
        self.devices_f  = devices_f
        self.comtable_f = comtable_f

        # Stubs for the Orbitals data
        self.sun        = None
        self.lpf        = None
        self.bge        = None
        
        # Stubs for other stuff
        self.modes      = None
        self.comtable   = None
        self.schedule   = {}
        self.devices    = {}

        # Metadata to be read with orbitals; can add more if needed
        self.deltaT     = None

        # ---
        # Read all inputs
        self.read_orbitals()
        self.read_devices()
        self.read_modes()

        if comtable_f is not None: self.read_comtable()

        self.initial_time   = initial_time
        self.until          = until

        if initial_time is not None:
            self.env = simpy.Environment(initial_time=initial_time)
        else:
            self.env = simpy.Environment()

        self.populate()

        self.create_command_table = False

        self.env.process(self.run()) # Set the callback to this class, for simpy

    # ---
    def populate(self): # Add hardware and the monitor to keep track of the sim
        self.monitor    = Monitor(self.sun.N) # 'sun' is used to define the discrete time axis

        self.battery    = Battery(self.battery_config)
        if self.verbose: print(f'''Created a Battery with initial charge: {self.battery.level}, capacity: {self.battery.capacity}''')
        self.ssd        = SSD(self.env, self.ssd_config)
        if self.verbose: print(f'''Created a SSD with initial fill: {self.ssd.level}, capacity: {self.ssd.capacity}''')
        self.thermal    = Thermal (self.env, self.thermal_config)


        self.controller = Controller(self.env, self.sun, self.verbose)
        self.controller.add_panels_from_config(self.panel_config)
        self.controller.calculate_power()

    # ---
    def read_orbitals(self):
        """ Read previously calculated data on the coordinates of the Sun and the Satellites.
            The file name is expected to be provides in the attribute orbitals_f.
            The format is HDF5, and it contains two section, metadata and payload (orbitals).
        """        

        f = h5py.File(self.orbitals_f, "r")

        ds_meta = f["/meta/configuration"] # Expect YAML payload, saved in the configuraiton section
        conf    = yaml.safe_load(ds_meta[0,])
        self.deltaT  = conf['period']['deltaT']

        ds_data = f["/data/orbitals"]
        da = np.array(ds_data[:]) # data array
        if self.verbose: print(f'''Shape of the data payload: {da.shape}''')

        # Inflate objects based on this array data:
        self.sun = Sun(da[:,0], da[:,1] , da[:,2])
        
        self.lpf = Sat(da[:,0], da[:,3] , da[:,4],da[:,5])
        self.bge = Sat(da[:,0], da[:,6] , da[:,7],da[:,8])

    # ---
    def read_modes(self):
        f = open(self.modes_f, 'r')
        modes = yaml.safe_load(f)
        self.modes = modes['modes']
        self.comgen = modes['command_generation']

    # ---
    def read_devices(self):
        """ Initialize devices using data read from the 'devices file' (YAML)
        """
        f                       = open(self.devices_f, 'r')
        profiles                = yaml.safe_load(f)  # "hold all" dictionary



        if 'comm' not in profiles: 
            print('Comm not found in configuration profile')
            raise NotImplementedError
        
        comm_config = profiles['comm']  
        self.comm = Comm(max_rate_kbps=comm_config.get('if_adaptable', {}).get('max_rate_kbps'),
                         link_margin_dB=comm_config.get('if_adaptable', {}).get('link_margin_dB'),
                         fixed_rate=comm_config.get('if_fixed', {}).get('fixed_rate'))  
        
        self.scheduling = profiles.get('scheduling', {})
        power_consumer_devices  = profiles['power_consumers'].keys()
        ssd_consumer_devices    = profiles['ssd_consumers'].keys()
        device_names            = power_consumer_devices | ssd_consumer_devices



        if 'PCDU' not in device_names:
            print('PCDU not found in the device list')
            raise NotImplementedError

        if 'UT' not in device_names:
            print('UT not found in the device list')
            raise NotImplementedError
            

        for device_name in device_names:
            power_profile               = profiles['power_consumers'].get(device_name, None)
            outside_heat_profile        = profiles['outside_heat'].get(device_name, None)
            data_profile                = profiles['ssd_consumers'].get(device_name, None)
            self.devices[device_name]   = Device(device_name, power_profile = power_profile, outside_heat_profile = outside_heat_profile,
                                                 data_profile = data_profile)
     
        # Component data, read from the "devices" file
        self.battery_config = profiles['battery']
        self.ssd_config     = profiles['ssd']
        self.thermal_config = profiles['thermal']
        self.panel_config   = profiles['solar_panels']

    
    # ---
    def read_comtable(self):
        f = open(self.comtable_f, 'r')
        self.comtable = yaml.safe_load(f)

        for k in self.comtable.keys(): self.schedule[self.comtable[k]['start']] = k
        self.times = list(self.schedule.keys())

    # ---
    def find_schedule(self, clock):
        l = len(self.times) - 1 
        tmax = self.times[l]
        if clock>=tmax:
            return self.comtable[self.schedule[tmax]]

        ndx = 0
        for t in self.times:
            if clock>=t:
                ndx+=1
            else:
                theTime = self.times[ndx-1]
                return self.comtable[self.schedule[theTime]]
   
        return None

    # ---
    def init_generate_schedule(self, myT):
        day = self.sun.alt[myT] > 0
        self.last_day_state = day
        if day:
            self.last_sunrise_mjd = self.sun.mjd[myT]
        else:
            self.last_sunset_mjd = self.sun.mjd[myT]
        self.last_comm = self.sun.mjd[myT]

    # --
    

    # --        
    def generate_schedule(self, myT):
        """ All of this is purely placeholder now
            don't take it too seriously."""

        cfg = self.comgen
        elap_time_overhead = 0
        alt_overhead = self.scheduling['alt_overhead']
        time_overhead_cond = self.scheduling['time_overhead']
        
        # first check some sanity
        assert (cfg['algorithm'] == 'simple') ## if not simple than raises assertion error
        day_modes = cfg['day']['modes'].split() ## splits the science and main into sep lists
        day_duty = np.array([float(x) for x in cfg['day']['duty'].split()]) ## splits same as above for duty cycle
        day_cycle = cfg['day']['cycle_hours'] ## sets the day cycle length
        assert(len(day_modes)==len(day_duty)) 
        assert(day_duty.sum()==1.0) ## sets so that percent of cycle toward a given mode is 100%
        assert(day_cycle>0)

        night_modes = cfg['night']['modes'].split() ## does the same thing as above but for night
        night_duty = np.array([float(x) for x in cfg['night']['duty'].split()])
        night_cycle = cfg['night']['cycle_hours']
        assert(len(night_modes)==len(night_duty))
        assert(night_duty.sum()==1.0)
        assert(night_cycle>0)
        
        sched = {}
        day = self.sun.alt[myT] > 0 ## day is when alt at time t is >0
        mjd_now = self.sun.mjd[myT]  ## gets current mjd 
        if 'last_state_day' not in self.__dict__:
            self.last_state_day = not day # let's force it to switch ## already not in so this statement is always true?
        if not day: ## which again is always true?
            if self.last_state_day:
                # day to night transition
                self.last_sunset_mjd = self.sun.mjd[myT] ## set mjd for sunset/beginning of night
                
            # let's switch between science and powersave every 12 hours
            cycle_frac = (mjd_now - self.last_sunset_mjd) / (night_cycle/24) ## time steps fraction of a day
            assert(cycle_frac>=0) ## beginning of night
            cycle_frac -= int(cycle_frac) ## subtracts integer number of cycles
            cp = 0
            for p, m in zip (night_duty,night_modes):
                cp+=p 
                if cp>cycle_frac: ## guarantees mode is spending the appropriate fractional time in a specific spot
                    sched['mode'] = m
                    break
        else:
            if not self.last_state_day:
                # night to day transition
                self.last_sunrise_mjd = self.sun.mjd[myT]
            # let's switch between science and powersave every 12 hours
            cycle_frac = (mjd_now - self.last_sunrise_mjd) / (day_cycle/24)
            assert(cycle_frac>=0)
            cycle_frac -= int(cycle_frac)

        
            if self.lpf.alt[myT] > alt_overhead:  ## opportunisticall change to maint when sat is overhead
                if 'init_cycle_frac_overhead' not in self.__dict__ or self.init_cycle_frac_overhead == 0: ##initialization
                    self.init_cycle_frac_overhead = cycle_frac
                    elap_time_overhead = 0
                    print(f"Initializing overhead time tracking. Initial cycle_frac where tracking begins: {cycle_frac:.4f}")
                else:
                    elap_time_overhead = cycle_frac - self.init_cycle_frac_overhead
                               
                    
                elap_time_overhead += cycle_frac - self.init_cycle_frac_overhead
                print(f"Current altitude: {self.lpf.alt[myT]:.2f}, where min altitude is: {alt_overhead:.2f}")
                print(f"Current cycle_frac (outside of alt loop): {cycle_frac:.4f}, Initial cycle_frac: {self.init_cycle_frac_overhead:.4f}")
                print(f"Elapsed time overhead: {elap_time_overhead:.4f}, Elapsed time condition: {time_overhead_cond:.4f}")
            
                    

                if elap_time_overhead >= time_overhead_cond:
                    print('-------------')
                    print(f"Elapsed time condition met: Daytime, altitude > {alt_overhead:.2f}, elapsed time {elap_time_overhead:.4f} >= {time_overhead_cond:.4f}")
                    sched['mode'] = day_modes[1]
                    print(f"Switching to mode: {day_modes[1]}")
                    print('-------------')
                        
                else:
                    print('xxxxxxxx')
                    print(f"Condition not met: Daytime, altitude > {alt_overhead:.2f}, but elapsed time {elap_time_overhead:.4f} < {time_overhead_cond:.4f}")
                    sched['mode'] = day_modes[0]
                    print(f"Maintaining mode: {day_modes[0]}")
                    print('xxxxxxxx')

            
            else:
                self.init_cycle_frac_overhead = 0
                cp = 0
                for p, m in zip(day_duty, day_modes):
                    cp += p
                    if cp >= cycle_frac:
                        sched['mode'] = m
                        break
        assert('mode' in sched)
        self.last_state_day = day
        return sched

     # ---
    def PFPS_custom(self, pwr):
        Pq = float(pwr[0])
        fact = float(pwr[1])
        pow = sum([self.devices[k].power() for k in pwr[2].strip().split('+')])
        return Pq + fact*pow
    
    
    # ---
    def power_out(self, verbose = False, conditions = [], mode = None, return_dict = False, get_heat = False):
        pwr = 0.0
        dct = {}
        mode_save = self.current_mode

        if mode is not None:
            # temporarily change mode
            self.set_mode(mode)

        if verbose: print ("Mode: ", self.current_mode)
        for dk in self.devices.keys():
            # handle special cases first:
            # #1 If PFPS is under load and has custom mode
            if dk=='PFPS':
                pwr_str = self.devices[dk].power()
                if type(pwr_str)==float:
                    cpower = pwr_str
                else:
                    pwr_str = pwr_str.split(',')
                    assert(pwr_str[0].strip()=='CUSTOM')
                    cpower = self.PFPS_custom(pwr_str[1:])
            # #2 If UT is transmitting....
            elif (dk=='UT') and ('TX' in conditions):
                cpower = self.devices[dk].power_tx(get_heat = get_heat)
            # the actual default case 
            else: 
                cpower = self.devices[dk].power(get_heat = get_heat)
            if verbose: print (f'     Device: {dk:12} : {cpower:4.2f} W')
            if return_dict:
                dct[dk] = cpower
            else:
                pwr += cpower
        if verbose: print (f'   Total power: {pwr:4.1f} W\n')
        
        self.set_mode(mode_save)
        return dct if return_dict else pwr
    
    # ---
    def power_info(self, conditions = [], get_heat = False):
        for mode in self.modes:
            self.set_mode(mode)
            self.power_out(verbose=True, conditions = conditions, get_heat = get_heat)


    # ---
    def power_in(self):
        return self.controller.power[self.myT]
    
     # ---
    def data_rate(self,time_index,conditions=[]):
        """ Calculate the total data rate, traversing over the device collection. """
        dr = 0.0
        for dk in self.devices.keys():
            if dk=='UT' and 'TX' in conditions:
                if not self.comm.adaptable_rate: 
                    dr += self.comm.fixed_rate
                else:                     
                    zero_ext_gain = False
                    
                    adapt_rate, demo,pw = self.comm.get_rate(self.lpf.dist[time_index],(180/np.pi)*self.lpf.alt[time_index],max_rate_kbps= 
                                                             self.comm.max_rate_kbps, demod_marg= self.comm.link_margin_dB, 
                                                             zero_ext_gain=False)

                    dr += adapt_rate 
            else:
                dr+=self.devices[dk].data_rate()
        
        return dr

    # ---
    def set_mode (self,mode):
        self.current_mode = mode
        self.set_state(self.modes[mode])

    def set_state(self, mode_info):
        for dk in self.devices.keys():
            self.devices[dk].state = mode_info[dk]

    def device_report(self):
        if self.verbose:        
            for dk in self.devices.keys(): print(self.devices[dk].info())
            print('*** Total power:', self.power_out(),'W')

    # ---
    def info(self):
        """ General info on the input files with brief bits of content for sanity check. """
        print(f'''Orbitals file: {self.orbitals_f}''')

        print('------------------')
        print(f'''Modes file: {self.modes_f}''')
        print(pretty(self.modes))

        print('------------------')
        print(f'''Devices file: {self.devices_f}''')

        self.device_report()



        if self.comtable is not None:
            print('------------------')
            print(f'''Comtable file: {self.comtable_f}''')
            print(pretty(self.comtable))

        print('------------------')
        print(f'''Day condition at start and end of the simulation: {self.sun.day[self.initial_time]}, {self.sun.day[self.until]}''')

    def save_record(self, filename='simulator_log.yml'):
        """ Capture the generated state transition record.
            It's in the same format as the main command table.
        """
        with open(filename, 'w') as file:
            yaml.dump(self.record, file)


    # --
    def get_conditions(self, myT):
        conditions = []
        mode = self.current_mode
        if (self.lpf.alt[myT]>0.1) and (self.modes[mode]['UT'] == 'ON'):
            conditions.append('TX')

        if (self.sun.alt[myT]>=0.0):
            conditions.append('day')
            if self.modes[mode]['PCDU'] == 'ON':
                conditions.append('charging')
        else:
            conditions.append('night')
        return conditions

    ############################## Simulation code #############################
    # ---
    def simulate(self, create_command_table = False):
        """ Steeting of the SimPy simulation process, relying on
            the 'run' method previous set in the SimPy environment"""
        
        self.create_command_table = create_command_table
        if create_command_table:
            myT     = int(self.env.now)
            self.init_generate_schedule(myT)

        if self.until is not None:
            self.env.run(until=self.until) # 17760
        else:
            self.env.run()
    # ---
    def run(self): # SimPy machinery: print(f'''Clock: {self.sun.mjd[myT]}, power: {Panel.profile[myT]}''')
        mode = None
        cnt = 0

        while True:
            myT     = int(self.env.now)
            clock   = self.sun.mjd[myT]
            self.myT = myT

            if self.create_command_table:
                sched = self.generate_schedule(myT)
            else:
                sched  = self.find_schedule(clock)
            
            md = sched['mode']

            if md!=mode:
                mode = md
                self.set_mode(mode)

                if self.verbose:
                    print(f'''Clock:{clock}, mode: {mode}''')
                    print('Device states:', self.modes[mode])
                    self.device_report()

                cnt+=1
                
                battery_fill = float(self.battery.level/self.battery.capacity)
                ssd_fill = self.ssd.level/self.ssd.capacity
                self.record[cnt] = {'start': float(clock), 
                                    'mode': mode,
                                    'battery_expected_fill': battery_fill,
                                    'ssd_expected_fill': ssd_fill}

            conditions = self.get_conditions(myT)                

            # Electrical section:
            self.monitor.power[myT] = self.power_out(conditions=conditions)

            # put charge into battery if BMS is enabled
            if ('charging' in conditions): 
                power_in = self.power_in()
            else:
                power_in = 0.0
            # Draw charge from battery
            power_out = self.power_out()
            self.battery.set_temperature(20) ## fix once we have thermal
            self.battery.apply_power(power_in - power_out, self.deltaT)
            self.battery.apply_age(self.deltaT)
            self.monitor.battery_SOC[myT]   = self.battery.level/self.battery.capacity
            self.monitor.battery_V[myT]     = self.battery.Voltage()

            # Data section
            ## first are we communicating:
            data_rate = self.data_rate(conditions=conditions, time_index=myT)    
            self.monitor.data_rate[myT] = data_rate
            self.ssd.change(data_rate*self.deltaT)
            self.monitor.ssd[myT]       = self.ssd.level/self.ssd.capacity

            # Thermal section
            heat = self.power_out(get_heat=True)
            self.thermal.evolve (heat, self.sun.alt[myT]/np.pi*180.0, self.deltaT)
            self.monitor.boxtemp[myT]   = self.thermal.temperature

            yield self.env.timeout(1)

