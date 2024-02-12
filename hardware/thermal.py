from scipy.interpolate import RegularGridInterpolator
import numpy as np
import sys

class Thermal:
    def __init__ (self, env, config, verbose = False, ):
        self.verbose = verbose  
        self.temperature = config['Tstart']
        self.tau = config['tau']
        # look up table
        power_list = np.array([float(x) for x in config['power'].split()])
        alt_list = np.array([float(x) for x in config['altitude'].split()])
        temp_list = np.array([[float(x) for x in l.split()] for l in config['temperature']])
        try:
            assert(temp_list.shape[0] == len(alt_list))
            assert(temp_list.shape[1] == len(power_list))
        except:
            print ("Arrays in thermal sections do not match in size.")
            print (len(alt_list),'x',len(power_list),'!=',temp_list.shape)
            sys.exit(1)
        
        self.Teq = RegularGridInterpolator((alt_list, power_list), temp_list)

    def evolve(self, heat, alt_deg, dt):
        if (alt_deg<0):
            alt_deg = 0
        Teq = self.Teq((alt_deg, heat))
        # exponential decay towards Teq over timescales tau
        self.temperature = Teq + (self.temperature-Teq)*np.exp(-dt/self.tau)
        return self.temperature