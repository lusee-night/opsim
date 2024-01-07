import  numpy as np
from    enum import Enum

#################################################################################
class Device():
    def __init__(self, name=None, profile = None, state='OFF'):
        self.name       = name
        self.state      = state
        self.currents   = profile

    def current(self):
        return self.currents[self.state]

    def info(self):
        name = self.name + ','
        return f'''Device:{name:16}\tstate:{self.state},\tcurrent:{self.current()}'''

#################################################################################
class Monitor():
    def __init__(self, size=0):
        self.current    = np.zeros(size, dtype=float)
        self.battery    = np.zeros(size, dtype=float)

