import numpy as np
from   scipy.spatial.transform import Rotation as R

##################### PANELS ###########################
class Panel: # base, "abstract"

    name            ='Base Panel Class' # will be overwritten in the derived classes
    verbose         = True
    solarConstant   = 1361   # W/m^2 at Moon 

    ###
    def __init__(self, sun, name = '', lander=(0.0 , 0.0, 0.0), normal=(None, None, None), env=None, area=1.0, pvEFF_T=None, pvEFF_P=None):

        lander_pitch, lander_roll, lander_yaw = lander

        r1 = R.from_euler('x', lander_pitch,    degrees=True) # + is nose down,     - is nose up
        r2 = R.from_euler('y', lander_roll,     degrees=True) # + is top left,      - is top right
        r3 = R.from_euler('z', lander_yaw,      degrees=True) # + is nose right,    - is nose left
        self.r_tot = r1*r2*r3

        self.sun        = sun
        self.name       = name
        self.area       = area
        self.env        = env

        if pvEFF_T is not None: 
            self.pvEfficiency = Panel.pvEfficiency
        else:
            self.pvEfficiency = np.polyfit(pvEFF_T, pvEFF_P, 2)
        
        # The "normal" is specific to each of the three (or more) subclassed panels
        self.normal     = normal
        self.normal_rot = self.r_tot.apply(self.normal)
        self.dot_sun    = self.dot(sun.xyz)

        self.choice_list = [self.dot_sun, self.dot_sun, 0, 0]
        self.temperature = sun.temperature
    
    ### ---
    def dot(self, sun_xyz):
        buffer = self.area*np.dot(sun_xyz, self.normal_rot)
        buffer[buffer<0] = 0.0
        return buffer
    
    ### ---
    def set_condition(self, condition_list):
        self.condition_list = condition_list

    ### ---
    def exposure(self):
        pwr = np.select(self.condition_list, self.choice_list)
        return pwr
    
    ### ---
    def power(self):
        eff = 0.3 # default, if the temperature curve is not set for the sun
        if self.sun.temperature is not None: eff = self.pvEfficiency(self.sun.temperature)
        power =  Panel.solarConstant*eff*np.select(self.condition_list, self.choice_list)
        return power 
    
    ### ---
    def info(self):
        return f'''Panel {self.name}'''
    
    ### Static method for the PV efficiency calculation (just convenient)
    @staticmethod
    def pvEfficiency(T):
        pvTemp = np.array([-173.15, 20, 126.85])
        pvPwr = np.array([152, 130, 110]) / 426.47  # Stated AM0 normal incidence power output of top panel
        p = np.poly1d(np.polyfit(pvTemp, pvPwr, 2))
        return p(T)

# ------------------------------------------------------------
