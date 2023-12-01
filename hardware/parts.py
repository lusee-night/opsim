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

#################################################################################
class Monitor():
    def __init__(self, size=0):
        self.buffer = np.empty(size)
        self.battery= np.empty(size)
        self.charge = 0


# ----------------
# Profiles are now read from YAML and kept here for reference only (i.e. deprecated for use):
DeviceProfiles = {"ControllerHardware": dict(ON=0.1, OFF=0.0)}

### Deprectated for now, used in the first cut:
# class ControllerHardware(Device):
#     def __init__(self, name=None, state=None):
#         Device.__init__(self, name, state)
#         self.currents = dict(ON=0.1, OFF=0.0)