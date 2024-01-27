import numpy as np

import lusee
from lusee import Observation as O
from lusee import Satellite, ObservedSatellite

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
    

    ### ---
    def __init__(self, mjd=None, alt=None, az=None):
        """ This constructor only creates a stub, and the object will
            be finalized later based on how the data are obtained.

            Keyword arguments:
            alt -- altitude (array)
            az  -- azimuth  (array)
        """        
        self.mjd        = mjd
        self.alt        = alt
        self.az         = az
        self.N          = 0
        self.verbose    = False
        self.temperature= None
        self.crossings  = None
        self.day        = None
        self.finalize()

    ### ---
    def finalize(self):
        """ That's a method that finishes the creation of the object.
            It is called from the constructor (assuming the input data are given are arguments),
            or alternatively from either the "calculate" or "read_trajectory" methods (below).

            The crossings are first calculated as indices in the "alt" array where the alt value
            changes its sign, and then more precisely using linear interpolation between
            two adjacent points, before and after the crossing.
        """
                
        if self.az is not None and self.alt is not None and self.mjd is not None:
            self.N = self.az.size
            self.alt_top = np.asarray(self.alt) + self.radius
            sun = np.zeros((len(self.alt),3))
            sun[:,0] = np.cos(self.alt) * np.sin(self.az)
            sun[:,1] = np.cos(self.alt) * np.cos(self.az)
            sun[:,2] = np.sin(self.alt)
            self.xyz = sun
            self.condition =  [self.alt>horizon+self.radius, self.alt>horizon, self.alt>horizon-self.radius, self.alt<=horizon-self.radius]

            # Sunrise calculations -- FIXME -- working on multiple sinrises
            self.iMidnight  = np.argmin(self.alt)
            self.iSunrise   = np.argmin(np.abs(self.alt[self.iMidnight:])) + self.iMidnight            
            self.hrsFromSunrise = (self.mjd - self.mjd[self.iSunrise])*24
            self.sunrise    = self.mjd[self.iSunrise]

            detect          = np.signbit(self.alt)
            self.crossings  = np.where(np.diff(detect))[0]
            self.day        = ~detect


        self.mjd_crossings = np.fromiter(self.precise_crossings(), float)
        self.set_temperature()


    ### ---
    def clock(self, mjd):
        """ This method calculates the "lunar clock" e.g. the time according
            to 24-hour subdividion of the Lunar day.
        """
        
        if mjd>self.mjd[self.N-1] or mjd<self.mjd[0]: return None

        if mjd<self.mjd_crossings[0]: # only one endpoint at the start, use the next cycle as estimate
            estimate = self.mjd_crossings[1] - self.mjd_crossings[0]
            if self.day[self.crossings[0]]:
                return 6.0 + 12.0*(1.0-(self.mjd_crossings[0] - mjd)/estimate)
            else:
                return 6.0*(1.0-(self.mjd_crossings[0] - mjd)/estimate)

        if mjd>self.mjd_crossings[-1]: # only one endpoint at the end, use the previous cycle as estimate
            estimate = self.mjd_crossings[-1] - self.mjd_crossings[-2] # print(estimate)
            if self.day[~self.crossings[-1]]: # print('day')
                return 6.0 + 12.0*(1.0-(mjd - self.mjd_crossings[-1])/estimate)
            else: # print('night')
                return 6.0*(1.0-(mjd - self.mjd_crossings[0])/estimate)


        indices = list(range(len(self.mjd_crossings)))
        _ = indices.reverse()
    
        for i in indices:
            if mjd>self.mjd_crossings[i]:
                estimate = self.mjd_crossings[i+1] - self.mjd_crossings[i] #  print(estimate)
                if (~self.day[self.crossings[i]]): # day, since crossing is one off by design
                    return 6.0+12.0*(mjd-self.mjd_crossings[i])/estimate
                else:
                    result = 18.0 + 12.0*(mjd-self.mjd_crossings[i])/estimate
                    if result >24.0: result-=24.0
                    return result

        return None

    ### ---
    def precise_crossings(self):
        """ A more precise calculation of crossings based on linear interpolation of alt sign switches.
            Linear interpolation is used to find the intercept of "alt".
        """

        for crs in self.crossings:
            (x1, x2) = (self.mjd[crs], self.mjd[crs+1])
            (y1, y2) = (self.alt[crs], self.alt[crs+1])
            a = (y2-y1)/(x2-x1)
            b = y2 -((y2-y1)/(x2-x1))*x2
            yield (-b)/a

    ### ---
    def calculate(self, interval):
        """ Calculate the (alt, az) of the Sun, based on the time interval defined,
            utilizing the "Observation" class from the luseepy package.

            Arguments:
            interval -- the time interval on one of the formats understood by Observation.
            For example, this can be a string like "2025-02-04 00:00:00 to 2025-03-07 23:45:00", or a tuple of two strings.
        """
       
        o = O(interval)
        (alt, az)   = o.get_track_solar('sun')
        mjd         = [timepoint.mjd for timepoint in o.times]
        self.mjd    = mjd
        self.alt    = alt
        self.az     = az
        self.finalize()

    ###
    def read_trajectory(self, filename):
        """ Read precalculated data (mjd, alt, az) from a numpy-formatted file.
            This is largely superceded by feeding the data to the constructor directly,
            from an application that's capable of parsing HDF5-formatted files.

            Arguments:
            filename -- the name of the numpy-formatted file to be read.
        """
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
        """ Simple interpolation of the tabulated data. Used mainly as a placeholder for a better calculation
            to be implemented later. It is based on the numerical data incorporated in this class.
        """
        self.temperature = np.interp(self.mjd, self.temperature_data[0] + self.sunrise, self.temperature_data[1]) -273.


# ---
class Sat:
    """ A simple container for the "orbitals" type of data for satellites.
        Adds the crossings and "up" condition calculation, quntized to the deltaT time step.
    """
    def __init__(self, mjd=None, alt=None, az=None):
        self.mjd        = mjd
        self.alt        = alt
        self.az         = az
        self.N          = self.az.size

        detect          = np.signbit(self.alt)
        self.crossings  = np.where(np.diff(detect))[0]
        self.up         = ~detect


########################################################################################################################
########################################################################################################################
########################################################################################################################
### Non-class functions (standalone):

def track(interval):
    """ Calculate the (alt, az) of the Sun, based on the time interval defined,
        utilizing the "Observation" class from the luseepy package.

        Arguments:
        interval -- the time interval on one of the formats understood by Observation.
        For example, this can be a string like "2025-02-04 00:00:00 to 2025-03-07 23:45:00", or a tuple of two strings.
    """

    o           = O(interval)
    length      = len(o.times)
    (alt, az)   = o.get_track_solar('sun')
    return (o.times, alt, az)

def track_from_observation(observation):
    length      = len(observation.times)
    (alt, az)   = observation.get_track_solar('sun')
    return (observation.times, alt, az)

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


### ATTIC
# def hrsFromSunrise(self):
#     iMidnight = np.argmin(self.alt)
#     iSunrise = np.argmin(np.abs(self.alt[iMidnight:])) + iMidnight
#     return (self.mjd - self.mjd[iSunrise])*24
###