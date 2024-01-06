import  simpy
import  yaml
import  h5py

# local packages
import  hardware     # hardware modules
from    hardware import *
from    utils.timeconv import *

import  nav          # Astro/observation wrapper classes
from    nav import *

class Simulator:
    def __init__(self, orbitals_f=None, modes_f=None, devices_f=None, comtable_f=None, initial_time=None, until=None):
    
        # Filenames
        self.orbitals_f   = orbitals_f
        self.modes_f      = modes_f
        self.devices_f    = devices_f
        self.comtable_f   = comtable_f

        # Stubs for the Orbitals
        self.sun        = None
        self.esa        = None
        
        # Stubs for other stuff
        self.modes      = None
        self.comtable   = None
        self.schedule   = {}
        self.devices    = {}

        # Read all inputs
        self.read_orbitals()
        self.read_devices()
        self.read_modes()
        self.read_combtable()


        self.initial_time   = initial_time
        self.until          = until

        if initial_time is not None:
            self.env = simpy.Environment(initial_time=initial_time)
        else:
            self.env = simpy.Environment()

        self.populate() # -FIXME- Needs work

        self.env.process(self.run()) # Set the callback to this class, for simpy

    # ---
    def populate(self): # Add hardware and the monitor to keep track of the sim
        initial_charge, capacity = 100., 1200. # battery
        self.battery = Battery(self.env, initial_charge, capacity)

        print(f'''Created a Battery with initial charge: {self.battery.level}, capacity: {self.battery.capacity}''')

        self.monitor    = Monitor(self.sun.N) # to define the discrete time axis
        self.controller = Controller(self.env, self.sun, self.battery, self.monitor)

        Controller.verbose = True

        self.controller.add_all_panels()
        self.controller.calculate_power()

    # ---
    def read_orbitals(self):
        f = h5py.File(self.orbitals_f, "r")
        ds_data = f["/data/orbitals"]
        da = np.array(ds_data[:]) # data array
        print(f'''Shape of the data payload: {da.shape}''')
        self.sun = Sun(da[:,0], da[:,1] , da[:,2])
        self.esa = Sat(da[:,0], da[:,3] , da[:,4])

    # ---
    def read_modes(self):
        f = open(self.modes_f, 'r')
        self.modes = yaml.safe_load(f)

    # ---
    def read_devices(self):
        f = open(self.devices_f, 'r')
        profiles = yaml.safe_load(f)  # ingest the configuration data
        for device_name in profiles.keys():
            device = Device(device_name, profiles[device_name])
            self.devices[device.name]=device
    
    # ---
    def read_combtable(self):
        f = open(self.comtable_f, 'r')
        self.comtable = yaml.safe_load(f)

        for k in self.comtable.keys():
            self.schedule[self.comtable[k]['start']] = k
 
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
    def info(self):
        print(f'''Orbitals file: {self.orbitals_f}''')

        print('------------------')
        print(f'''Modes file: {self.modes_f}''')
        print(pretty(self.modes))

        print('------------------')
        print(f'''Devices file: {self.devices_f}''')

        for dk in self.devices.keys():
            print(self.devices[dk])


        print('------------------')
        print(f'''Comtable file: {self.comtable_f}''')
        print(pretty(self.comtable))

        print('------------------')
        print(f'''Day condition at start and end of the simulation: {self.sun.day[self.initial_time]}, {self.sun.day[self.until]}''')

    ############################## Simulation code #############################
    
    def simulate(self):
        if self.until is not None:
            self.env.run(until=self.until) # 17760
        else:
            self.env.run()
    
    def run(self): # SimPy machinery: print(f'''Clock: {self.sun.mjd[myT]}, power: {Panel.profile[myT]}''')
    
        mode = None

        while True:
            myT     = int(self.env.now) # print(myT)

            myPwr   = self.controller.power[myT]
            clock   = self.sun.mjd[myT]

            sched   = self.find_schedule(clock)
            md = sched['mode']

            if md!=mode:
                mode = md
                print(clock, md)
                print(self.modes[mode])

            bms = (self.modes[mode]['bms'] == 'ON')

            # See if the battery is charging:
            try:
                if bms:
                    self.battery.put(myPwr)
            except:
                pass

            for k in self.devices.keys():
                the_device = self.devices[k]
                if clock >60720.0: the_device.state = 'OFF'
                cur = the_device.current()
                if cur>0.0: self.battery.get(cur)

            self.monitor.charge+=myPwr
            self.monitor.battery[myT] = self.battery.level
            
            yield self.env.timeout(1)
