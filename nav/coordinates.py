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
            0.5014003646378833, 0.761531479110904, 1.009156290003491,  1.177991388339346, 1.718263703014081,
            2.6187175608053064, 2.911365064587454, 3.603588967764459,  3.800563249156289, 4.17200046549517,
            4.86985220528337,   5.455147212847667, 5.972908181077622,  6.468157802862795, 6.558203188641918,
            7.9342092400791335, 8.10023042010939,  8.76431514023042,   8.854360526009543, 9.912393808914231,
            10.126251600139646, 10.46392179681136, 11.46567671360409, 12.073483067613171, 13.964436168974746,
            15.180048876992903, 16.17054812056325, 16.73333178168276, 17.723831025253112, 19.018233445828,
            19.259426443450646, 19.71608518561619, 20.38016990573722, 20.914814383800767, 21.10053299197021,
            21.52824857442104,  22.18107762131967, 22.98023042010939, 23.858172931455837
        ],

        [
            97.46353373349797,  96.7148466393648,  95.94648831312088, 96.20850912483542,   95.07119716912325,
            93.91830559757949,  93.98062406090611, 93.36522923555503, 91.79947784447188,   92.07991092944201,
            92.07991092944201,  91.30093013785836, 93.11855198488689,186.85590723878695, 206.84974755610082,
            304.43007471514693,307.64986198702604,327.6437023043399, 341.30183218344,    359.5507555276065,
            365.65998826035377,371.5559623556129, 378.4851819683666, 381.65303718747344, 368.3064996250068,
            342.28854118611264,309.83100820346027,288.4364862342322, 208.39732272871368, 113.19737202491899,
            110.35257464059009,109.09001876020517,105.01099206973072,104.93309399057233, 104.15411319898868,
            102.86100508495986,101.68734069230715, 99.4023303703284,  98.82365892515196
        ]])
    

    ### ---
    def __init__(self, mjd=None, alt=None, az=None):
        """ Without valid arguments in the contructor, it constructor only creates a stub, and the object will
            be completed later based on how the data are obtained (e.g. calculated, read from file etc).

            An object that's missing data can't be finalized.

            If the data (mjd, alt, az) is supplied in the constructor, it will be finalized.

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
        self.clocks     = None
    
        if mjd is not None and alt is not None and az is not None: self.finalize()

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
            # Work in progress, may choose to remove since progress with the lunar clock
            # 
            # self.iMidnight  = np.argmin(self.alt)
            # self.iSunrise   = np.argmin(np.abs(self.alt[self.iMidnight:])) + self.iMidnight            
            # self.hrsFromSunrise = (self.mjd - self.mjd[self.iSunrise])*24
            # self.sunrise    = self.mjd[self.iSunrise]

            detect          = np.signbit(self.alt)
            self.crossings  = np.where(np.diff(detect))[0]
            self.day        = ~detect


        self.mjd_crossings = np.fromiter(self.precise_crossings(), float)
        self.clocks = np.array([self.clock(x) for x in self.mjd])
        self.set_temperature()

    ### ---
    def clock(self, mjd):
        """ This method calculates the "lunar clock" e.g. the time according
            to 24-hour subdividion of the Lunar day.
        """

        if mjd>self.mjd[self.N-1] or mjd<self.mjd[0]: raise ValueError

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


        # Main use case -- we have sunrise/sunset points on either side of the point of interest
        indices = list(range(len(self.mjd_crossings)))
        _ = indices.reverse()
    
        for i in indices:
            if mjd>self.mjd_crossings[i]:
                estimate = self.mjd_crossings[i+1] - self.mjd_crossings[i]
                if (~self.day[self.crossings[i]]): # day, since crossing is one off by design
                    return 6.0+12.0*(mjd-self.mjd_crossings[i])/estimate
                else:
                    result = 18.0 + 12.0*(mjd-self.mjd_crossings[i])/estimate
                    if result >24.0: result-=24.0
                    return result


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
            to be implemented later, since it can be panel-specific.
            It is based on the numerical data incorporated in this class.
        """

        self.temperature = np.interp(self.clocks, self.temperature_data[0], self.temperature_data[1]) -273.


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
