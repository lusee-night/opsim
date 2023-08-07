
import numpy as np
from    scipy.spatial.transform import Rotation as R

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

    def add_panel(self, panel):
        self.panels.append(panel)

    

class Device:
    def __init__(self, name='', voltage=0.0):
        self.name = name
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage

###

class Panel:
    ### Assume that the pivot angle is zero for now, easy to add later:
    name =''
    lander_pitch, lander_roll, lander_yaw = 0., 0., 0.

    ### Define lander rotations
    r1 = R.from_euler('x', lander_pitch,    degrees=True) # + is nose down,     - is nose up
    r2 = R.from_euler('y', lander_roll,     degrees=True) # + is top left,      - is top right
    r3 = R.from_euler('z', lander_yaw,      degrees=True) # + is nose right,    - is nose left
    r_tot = r1*r2*r3

    def __init__(self, name=''):
        self.name = name
        self.normal = (None, None, None)
        self.normal_rot = (None, None, None)

class EPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (1., 0., 0.)
        self.normal_rot = self.r_tot.apply(self.normal)

class WPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (-1., 0., 0.)
        self.normal_rot = self.r_tot.apply(self.normal)

class TPanel(Panel):
    def __init__(self, name=''):
        Panel.__init__(self, name)
        self.normal = (0., 0., 1.)
        self.normal_rot = self.r_tot.apply(self.normal)