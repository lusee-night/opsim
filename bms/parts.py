import  numpy as np
from    enum import Enum

from    bms.panels import * # EPanel, TPanel, WPanel

#################################################################################
# class Battery:
#     def __init__(self, voltage=0.0, charge=0.0, temperature=0.0):
#         self.voltage    = voltage
#         self.charge     = charge
 
#         self.temperature= temperature
#         self.verbose    = True

#     def set_voltage(self, voltage):
#         self.voltage = voltage

#     def set_temperature(self, temperature):
#         self.temperature = temperature



#################################################################################
class Device():
    def __init__(self, name=None, state=None):
        self.name   = name
        self.state  = state

class ControllerHardware(Device):
    def __init__(self, name=None, state=None):
        Device.__init__(self, name, state)
        self.current = 0.1


#################################################################################
class Monitor():
    def __init__(self, size=0):
        self.buffer = np.empty(size)
        self.battery= np.empty(size)
        self.charge = 0
