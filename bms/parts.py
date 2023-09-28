import  numpy as np
from    enum import Enum

# At present, this is the device description, current drawn from
# the PSU, depending on the state:

DeviceProfiles = {
    "ControllerHardware": dict(ON=0.1, OFF=0.0)
    }

#################################################################################
class Device():
    def __init__(self, name=None, state=None, profile = None):
        self.name   = name
        self.state  = state
        self.currents = profile

    def current(self):
        return self.currents[self.state]

### Deprectated for now --
class ControllerHardware(Device):
    def __init__(self, name=None, state=None):
        Device.__init__(self, name, state)
        self.currents = dict(ON=0.1, OFF=0.0)


#################################################################################
class Monitor():
    def __init__(self, size=0):
        self.buffer = np.empty(size)
        self.battery= np.empty(size)
        self.charge = 0
