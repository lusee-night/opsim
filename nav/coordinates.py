import lusee
import numpy as np
from lusee import Observation as O


### Keep these simple defaults for now:
horizon = 0.0
to_rad  = np.pi/180
sun_rad = 0.265*to_rad

############################################################################
class Sun:
    def __init__(self, mjd=None, alt=None, az=None):
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az
    ###
    def calculate(self, interval):
        o = O(interval)
        (alt, az) = o.get_track_solar('sun')
        mjd = [timepoint.mjd for timepoint in o.times]
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az


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