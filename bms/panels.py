import  numpy as np
from    scipy.spatial.transform import Rotation as R
##################### PANELS ###########################

class Panel:
    ### Assume that the pivot angle is zero for now, easy to add later:
    name =''
    lander_pitch, lander_roll, lander_yaw = 0., 0., 0.

    ### Define lander rotations
    r1 = R.from_euler('x', lander_pitch,    degrees=True) # + is nose down,     - is nose up
    r2 = R.from_euler('y', lander_roll,     degrees=True) # + is top left,      - is top right
    r3 = R.from_euler('z', lander_yaw,      degrees=True) # + is nose right,    - is nose left
    r_tot = r1*r2*r3

    def __init__(self, sun, name = '', normal=(None, None, None), area=1.0):
        self.name       = name
        self.area       = area
        self.normal     = normal
        self.normal_rot = self.r_tot.apply(self.normal)
        self.dot_sun    = self.dot(sun)

        self.choice_list = [self.dot_sun, self.dot_sun, 0, 0]


    def dot(self, sun):
        buffer = self.area*np.dot(sun, self.normal_rot)
        buffer[buffer<0] = 0.0
        return buffer
    
    def set_condition(self, condition_list):
        self.condition_list = condition_list
    
    def power(self):
        return np.select(self.condition_list, self.choice_list)

    def info(self):
        return f'''Panel {self.name}'''

class EPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun,  name, (1., 0., 0.))

class WPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun, name, (-1., 0., 0.))

class TPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun, name, (0., 0., 1.))
