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


    def populate(self):
        env = simpy.Environment()
        initial_charge, capacity = 100., 1200. # battery
        self.battery = Battery(env, initial_charge, capacity)
        print(f'''Created a Battery with initial charge: {self.battery.level}, capacity: {self.battery.capacity}''')

        self.monitor    = Monitor(self.sun.N) # to define the discrete time axis
        self.controller = Controller(env, self.sun, self.battery, self.monitor)

        Controller.verbose = True

        self.controller.add_all_panels()

        # ctr.calculate_power()   


    def read_orbitals(self):
        f = h5py.File(self.orbitals, "r")
        ds_data = f["/data/orbitals"]
        da = np.array(ds_data[:]) # data array
        print(f'''Shape of the data payload: {da.shape}''')
        self.sun = Sun(da[:,0], da[:,1] , da[:,2])
        self.esa = Sat(da[:,0], da[:,3] , da[:,4])


    def info(self):
        print(self.orbitals)
        print(self.modes)
        print(self.devices)


