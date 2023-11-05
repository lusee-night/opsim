import numpy as np
import simpy # placeholder for now, FIXME

from   scipy.spatial.transform import Rotation as R

##################### PANELS ###########################

class Panel: # base, "abstract"

    name ='Base Panel Class.' # will be overwritten in the derived classes

    ### Assume that the panel pivot angle is zero for now, easy to add later:
    lander_pitch, lander_roll, lander_yaw = 0., 0., 0.

    ### Define lander rotations
    r1 = R.from_euler('x', lander_pitch,    degrees=True) # + is nose down,     - is nose up
    r2 = R.from_euler('y', lander_roll,     degrees=True) # + is top left,      - is top right
    r3 = R.from_euler('z', lander_yaw,      degrees=True) # + is nose right,    - is nose left
    r_tot = r1*r2*r3

    # If set, represents the time series for the generated power
    profile    = None
    verbose    = True


    ###
    def __init__(self, sun, name = '', normal=(None, None, None), env=None, area=1.0):
        self.sun        = sun
        self.name       = name
        self.area       = area
        self.env        = env
        
        # The "normal" is specific to each of the three (or more) subclassed panels
        self.normal     = normal
        self.normal_rot = self.r_tot.apply(self.normal)
        self.dot_sun    = self.dot(sun.xyz)

        self.choice_list = [self.dot_sun, self.dot_sun, 0, 0]
        self.temperature = sun.temperature
    
    ###
    def dot(self, sun):
        buffer = self.area*np.dot(sun, self.normal_rot)
        buffer[buffer<0] = 0.0
        return buffer
    ###
    def set_condition(self, condition_list):
        self.condition_list = condition_list
    ###
    def exposure(self):
        pwr = np.select(self.condition_list, self.choice_list)
        # pwr*=2.0
        return pwr
    
    ###
    def power(self):
        eff = 1.0 # default to 1.o if the temperature curve is not set for the sun
        if self.sun.temperature is not None: eff = Panel.pvEfficiency(self.sun.temperature)
        return eff*np.select(self.condition_list, self.choice_list)
    ###
    def info(self):
        return f'''Panel {self.name}'''
    
    ### Static method for the PV efficiency calculation (just convenient)
    @staticmethod
    def pvEfficiency(T):
        pvTemp = np.array([-173.15, 20, 126.85])
        pvPwr = np.array([152, 130, 110]) / 426.47  # Stated AM0 normal incidence power output of top panel
        p = np.poly1d(np.polyfit(pvTemp, pvPwr, 2))
        return p(T)

    ### Static method to read the panel exposure profile
    @staticmethod
    def read_profile(filename):
        try:
            with open(filename, 'rb') as f: Panel.profile = np.load(f)
            if Panel.verbose: print(f'''Loaded data from file "{filename}", number of points: {Panel.profile.size}''')
        except:
            if Panel.verbose: print(f'''ERROR using file {filename} as the data source for the power profile''')


# ------------------------------------------------------------
class EPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun,  name, (1., 0., 0.))

class WPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun, name, (-1., 0., 0.))

class TPanel(Panel):
    def __init__(self, sun, name):
        Panel.__init__(self, sun, name, (0., 0., 1.))
