import lusee
import numpy as np
from lusee import Observation as O

horizon = 0.0

to_rad  = np.pi/180
sun_rad = 0.265*to_rad

def track(interval): # "2025-02-04 00:00:00 to 2025-03-07 23:45:00"
    o = O(interval)
    length = len(o.times)
    (alt, az) = o.get_track_solar('sun')

    return (o.times, alt, az) #alt, az

def altaz2xyz(alt,az):   
    sun = np.zeros((len(alt),3))
    sun[:,0] = np.cos(alt) * np.sin(az)
    sun[:,1] = np.cos(alt) * np.cos(az)
    sun[:,2] = np.sin(alt)
              
    return sun


    # sun = np.zeros((length,3))

    # sinalt      = np.sin(alt*to_rad)
    # cosalt      = np.cos(alt*to_rad)
    # sinaz       = np.sin(az*to_rad)
    # cosaz       = np.cos(az*to_rad)

    # sun[:,0]    = cosalt * sinaz
    # sun[:,1]    = cosalt * cosaz
    # sun[:,2]    = sinalt