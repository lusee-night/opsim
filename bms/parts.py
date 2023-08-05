
import numpy as np

class Battery:
    def __init__(self, voltage=0.0):
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage


class Controller:
    def __init__(self, battery):
        self.panels     = []
        self.devices    = []
        self.battery    = battery

#    def set_voltage(self, voltage):
#        self.voltage = voltage

class Device:
    def __init__(self, name='', voltage=0.0):
        self.name = name
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage

###

class Panel:
    # Assume that the pivot angle is zero for now, easy to add later:
    name =''
    def __init__(self, name=''):
        self.name = name
        self.normal = (None, None, None)

class EPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (1., 0., 0.)

class WPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (-1., 0., 0.)

class TPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (0., 0., 1.)