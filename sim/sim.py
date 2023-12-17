import simpy
import hardware     # hardware modules
from hardware import *

class Simulator:
    def __init__(self, orbitals=None, modes=None, devices=None):
        self.orbitals   = orbitals
        self.modules    = modes
        self.devices    = devices


    def populate(self):
        env = simpy.Environment()
        initial_charge, capacity = 100., 1200. # battery
        battery = Battery(env, initial_charge, capacity)

