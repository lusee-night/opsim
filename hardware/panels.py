import numpy as np
from   scipy.spatial.transform import Rotation as R

##################### PANELS ###########################
class Panel: # base, "abstract"

    name            ='Base Panel Class' # will be overwritten in the derived classes
    verbose         = True
    solarConstant   = 1361   # W/m^2 at Moon 

    ###
    def __init__(self, sun, name = '', lander=(0.0 , 0.0, 0.0), normal=(None, None, None), env=None, area=1.0, pvEFF_T=None, pvEFF_P=None, efficiency_mult=1.0):

        lander_pitch, lander_roll, lander_yaw = lander
        

        r1 = R.from_euler('x', lander_pitch,    degrees=True) # + is nose down,     - is nose up
        r2 = R.from_euler('y', lander_roll,     degrees=True) # + is top left,      - is top right
        r3 = R.from_euler('z', lander_yaw,      degrees=True) # + is nose right,    - is nose left
        self.r_tot = r1*r2*r3

        self.sun        = sun
        self.name       = name
        self.area       = area
        self.env        = env
        self.efficiency_mult = efficiency_mult

        if pvEFF_T is not None: 
            self.pvEfficiency = Panel.pvEfficiency
        else:
            self.pvEfficiency = np.polyfit(pvEFF_T, pvEFF_P, 2)
        
        # The "normal" is specific to each of the three (or more) subclassed panels
        self.normal     = normal
        self.normal_rot = self.r_tot.apply(self.normal)
        self.dot_sun    = self.dot(sun.xyz)
        self.pv_angle_corr = self.pv_angle_corr(sun.xyz)

        self.choice_list = [self.dot_sun, self.dot_sun, 0, 0]
        self.temperature = sun.regolith_temperature
    
    ### ---
    def dot(self, sun_xyz):
        buffer = self.area*np.dot(sun_xyz, self.normal_rot)
        buffer[buffer<0] = 0.0
        return buffer

    ### ---
    def pv_angle_corr(self, sun_xyz):
        #Correction factor for measured divergence of PV power as a function of solar angle from expected cosine/dot-product dependence 
        
        sun_unit = sun_xyz / np.linalg.norm(sun_xyz, axis=1)[:, np.newaxis] #Unit vector for direction of sun
        pv_unit = self.normal_rot / np.linalg.norm(self.normal_rot) #PV normal_rot should already be a unit vector, but hey, safety first!
        sun_angle = np.abs(np.degrees(np.arccos(np.dot(sun_unit, pv_unit))))
        
        poly_coeffs = [1.0004983419956408e+000, -3.8502838956781440e-003, 1.7502375769223580e-003, -3.5217013489873119e-004, 3.5446614736203286e-005, -2.0316555216327750e-006, \
                   7.1799275885981016e-008, -1.6233764365292121e-009, 2.3567637664937247e-011, -2.1265570389995531e-013, 1.0858756530544471e-015, -2.3977629606594377e-018]
        poly_fit = np.polynomial.Polynomial(poly_coeffs)

        return poly_fit(sun_angle)  
    
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
        if self.sun.regolith_temperature is not None: eff = self.pvEfficiency(self.sun.regolith_temperature)
        power =  Panel.solarConstant*eff*np.select(self.condition_list, self.choice_list)*self.pv_angle_corr * self.efficiency_mult
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
