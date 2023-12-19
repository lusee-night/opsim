import simpy
import h5py

# local packages
import hardware     # hardware modules
from hardware import *

import nav          # Astro/observation wrapper classes
from   nav import *

class Simulator:
    def __init__(self, orbitals=None, modes=None, devices=None):
        self.orbitals   = orbitals
        self.modes      = modes
        self.devices    = devices

        self.sun        = None
        self.esa        = None

        self.read_orbitals()
        self.env = simpy.Environment()

    # ---
    def populate(self):
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
        f = h5py.File(self.orbitals, "r")
        ds_data = f["/data/orbitals"]
        da = np.array(ds_data[:]) # data array
        print(f'''Shape of the data payload: {da.shape}''')
        self.sun = Sun(da[:,0], da[:,1] , da[:,2])
        self.esa = Sat(da[:,0], da[:,3] , da[:,4])

    # ---
    def info(self):
        print(self.orbitals)
        print(self.modes)
        print(self.devices)

    ######### Simulation code
    def run(self):
    
        ### SimPy machinery: print(f'''Clock: {self.sun.mjd[myT]}, power: {Panel.profile[myT]}''')
    
        while True:
            myT     = int(self.env.now)
            myPwr   = self.controller.power[myT]
            clock   = self.sun.mjd[myT]

            self.monitor.buffer[myT] = myPwr
            # try:
            #     self.battery.put(myPwr)
            # except:
            #     pass

            # for k in self.devices.keys():
            #     the_device = self.devices[k]
            #     if clock >60720.0: the_device.state = 'OFF'
            #     cur = the_device.current()
            #     if cur>0.0: self.battery.get(cur)

            # self.monitor.charge+=myPwr
            # self.monitor.battery[myT] = self.battery.level
            
            yield self.env.timeout(1)
