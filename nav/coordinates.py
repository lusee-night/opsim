import numpy as np

import lusee
from lusee import Observation as O


### Keep these simple defaults for now:
horizon = 0.0
to_rad  = np.pi/180
sun_rad = 0.265*to_rad

# This was borrowed from the temperature-related cell in Ben's notebook
hrs_per_lunar_day = 2551443/3600
t_inc = 0.25

############################################################################
class Sun:
    # Class variables defined here:
    radius = 0.265*to_rad

    temperature_data = np.array([
        [
        0.97142587, 1.25497185, 1.49126017, 1.57396107, 1.71573406,  1.96383679,
        2.35371251, 2.92080447, 3.29295856, 3.77853105, 4.3030911,   5.05626011,
        5.99649069, 6.92589139, 7.85754246, 8.68792711, 9.32590556,  10.04489714,
        10.925915,  11.39174053,11.60440001,12.02971898,12.3487082,  12.50229561,
        12.73858392,13.07529477,13.58922185,14.0347941],
        [
        127.7813564,  159.18763879, 188.01454941, 202.60166081, 224.71386936,
        251.48469189, 269.86445226, 298.62190044, 311.88922557, 329.55583827,
        341.68861029, 356.46095485, 367.52349083, 372.14788814, 368.93111584,
        360.06638601, 351.03626943, 335.19773162, 310.1725111,  297.92727609,
        287.92468542, 254.72164138, 225.35060835, 206.19055329, 187.24274457,
        154.12266955, 133.7180792,  117.42748427]])
    
    def __init__(self, mjd=None, alt=None, az=None):
        self.mjd        = mjd
        self.alt        = alt
        self.az         = az
        self.N          = 0
        self.verbose    = False
        self.temperature= None
        # self.finalize()

    ###
    def finalize(self):
        if self.az is not None:
            self.N = self.az.size
            self.alt_top = np.asarray(self.alt) + self.radius
            sun = np.zeros((len(self.alt),3))
            sun[:,0] = np.cos(self.alt) * np.sin(self.az)
            sun[:,1] = np.cos(self.alt) * np.cos(self.az)
            sun[:,2] = np.sin(self.alt)
            self.xyz = sun
            self.condition =  [self.alt>horizon+self.radius, self.alt>horizon, self.alt>horizon-self.radius, self.alt<=horizon-self.radius]

            # Sunrise calculations
            self.iMidnight = np.argmin(self.alt)
            self.iSunrise = np.argmin(np.abs(self.alt[self.iMidnight:])) + self.iMidnight            
            self.hrsFromSunrise = (self.mjd - self.mjd[self.iSunrise])*24
            self.sunrise = self.mjd[self.iSunrise]

        self.set_temperature()

    ###
    def calculate(self, interval):
        # Note the crafty logic in the Observation class constructor - it's hand-made polymorphism.
        # When a string is supplied, it defaults to 15 min time steps.
        # And in this case, the interval is a string. Need to improve the logic, later.
        
        o = O(interval)
        (alt, az) = o.get_track_solar('sun')
        mjd = [timepoint.mjd for timepoint in o.times]
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az
        self.finalize()

    ###
    def read_trajectory(self, filename):
        try:
            with open(filename, 'rb') as f: mjd_alt_az = np.load(f)
            if self.verbose: print(f'''Loaded data from file "{filename}", number of points for the three components: {mjd_alt_az.size}''')

            self.mjd = mjd_alt_az[:,0]
            self.alt = mjd_alt_az[:,1]
            self.az  = mjd_alt_az[:,2]
            self.finalize()
        except:
            if self.verbose: print(f'''ERROR using file {filename} as the data source for the Sun trajectory''')
            self.N = 0

    ###
    def read_temperature(self, filename):
        # FIXME: transforms of the temp curve are hacky, will need to revisit.
        try:
            temp_data = np.loadtxt(filename, delimiter=',')
            if self.verbose: print(f'''Loaded data from file "{filename}", number of points: {temp_data.size}''')
            x = temp_data[7:35,0]-5+self.sunrise # 60726.14583333333
            y = temp_data[7:35,1]
            self.temperature = np.interp(self.mjd, x, y) -273.
        except:
            if self.verbose: print(f'''ERROR using file {filename} as the data source for the power profile''')

    ###
    def set_temperature(self):
        self.temperature = np.interp(self.mjd, self.temperature_data[0] + self.sunrise, self.temperature_data[1]) -273.


    ###
    # def hrsFromSunrise(self):
    #     iMidnight = np.argmin(self.alt)
    #     iSunrise = np.argmin(np.abs(self.alt[iMidnight:])) + iMidnight
    #     return (self.mjd - self.mjd[iSunrise])*24

########################################################################################################################
### -- non-class functions:
def track(interval): # "2025-02-04 00:00:00 to 2025-03-07 23:45:00", or a tuple of two strings.
    o = O(interval)
    length = len(o.times)
    (alt, az) = o.get_track_solar('sun')

    return (o.times, alt, az)

###
def altaz2xyz(alt,az):   
    sun = np.zeros((len(alt),3))
    sun[:,0] = np.cos(alt) * np.sin(az)
    sun[:,1] = np.cos(alt) * np.cos(az)
    sun[:,2] = np.sin(alt)
              
    return sun

###
def hrsFromSunrise(alt, mjd):
    iMidnight = np.argmin(alt)
    iSunrise = np.argmin(np.abs(alt[iMidnight:])) + iMidnight
    return (mjd - mjd[iSunrise])*24

###
def sun_condition(alt):
    return [alt>horizon+sun_rad, alt>horizon, alt>horizon-sun_rad, alt<=horizon-sun_rad]



##############################################
# sun = np.zeros((length,3))

# sinalt      = np.sin(alt*to_rad)
# cosalt      = np.cos(alt*to_rad)
# sinaz       = np.sin(az*to_rad)
# cosaz       = np.cos(az*to_rad)

# sun[:,0]    = cosalt * sinaz
# sun[:,1]    = cosalt * cosaz
# sun[:,2]    = sinalt