import numpy as np

import lusee
from lusee import Observation as O


### Keep these simple defaults for now:
horizon = 0.0
to_rad  = np.pi/180
sun_rad = 0.265*to_rad

############################################################################
class Sun:
    radius = 0.265*to_rad
    def __init__(self, mjd=None, alt=None, az=None):
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az
        self.N      = 0
        self.finalize()

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

    ###
    def calculate(self, interval):
        # Note the crafty logic in the Observation class constructor -
        # it's hand-made polymorphism.
        # When a string is supplied, it defaults to 15 min time steps.
        # And in this case, the interval is a string.
        # Need to improve the logic, later.
        
        o = O(interval)
        (alt, az) = o.get_track_solar('sun')
        mjd = [timepoint.mjd for timepoint in o.times]
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az
        self.finalize()

    ###
    def read(self, filename):
        try:
            with open(filename, 'rb') as f: mjd_alt_az = np.load(f)
            print(f'''Loaded data from file "{filename}", number of points for the three components: {mjd_alt_az.size}''')

            self.mjd = mjd_alt_az[:,0]
            self.alt = mjd_alt_az[:,1]
            self.az  = mjd_alt_az[:,2]
            self.finalize()
        except:
            print(f'''ERROR using file {filename} as the data source''')
            self.N = 0


    ###
    def hrsFromSunrise(self):
        iMidnight = np.argmin(self.alt)
        iSunrise = np.argmin(np.abs(self.alt[iMidnight:])) + iMidnight
        return (self.mjd - self.mjd[iSunrise])*24

########################################################################################################################
### -- non-class functions:
def track(interval): # "2025-02-04 00:00:00 to 2025-03-07 23:45:00"
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