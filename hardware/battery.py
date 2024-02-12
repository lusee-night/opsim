
from scipy.interpolate import RegularGridInterpolator
import numpy as np
import sys


class Battery:
    def __init__(self, env, config, verbose = False):
        self.verbose = verbose
        self.temperature = None 
        self.level = float(config['initial'])*3600 # to As
        self.capacity = float(config['capacity'])*(1-float(config['capacity_fade']))*3600
        self_discharge = float(config['self_discharge'])
        self.discharge_tau = -28*24*3600/np.log(1-self_discharge)
        table_fn = config['VOC_table']
        VOC_table_cols = config['VOC_table_cols']
        self.read_VOC_table(table_fn, VOC_table_cols)
        

    def read_VOC_table(self, table_fn, VOC_table_cols):
        if self.verbose: print ('Reading VOC table from %s' % table_fn)
        table = np.genfromtxt(table_fn, delimiter=' ', comments='#')
        VOC_cols = []
        RI_cols = []
        VOC_temps = []
        RI_temps = []
        soc_col = None
        err = False
        for i, el in enumerate(VOC_table_cols.split()):
            if el == 'SOC':
                soc_col = i
            else:
                try:
                    C, T = el.split('@')
                    if C == 'VOC':
                        VOC_cols.append(i)
                        VOC_temps.append(float(T))
                    elif C == 'R':
                        RI_cols.append(i)
                        RI_temps.append(float(T))
                    else:
                        raise NotImplementedError   
                except:
                    print('Cannot parse VOC table. Column %d has value %s' % (i, el))
                    sys.exit(1)
        if soc_col is None:
            print('Cannot parse VOC table. No SOC column')
            sys.exit(1)
        SOC = table[:, soc_col]/100.0 # convert from percent to fraction
        if self.verbose: 
                print ('   SOC lookup:', SOC[0],'..' , SOC[-1])
                print ('   Temperature lookup:', VOC_temps[0],'..' , VOC_temps[-1])
        VOC_table = table[:, VOC_cols]
        RI_table = table[:, RI_cols]
        self.VOC = RegularGridInterpolator((SOC, VOC_temps), VOC_table)
        self.R_internal = RegularGridInterpolator((SOC, RI_temps), RI_table)



    def Voltage(self):
        SOC = self.level/self.capacity
        return self.VOC((SOC,self.temperature))
    
    def SOC(self):
        return self.level/self.capacity

    def set_temperature(self, temperature):
        self.temperature = temperature



    def apply_power (self, power, deltaT):
        # Applies power to the battery for deltaT seconds
        # if power (in W) is positive, we charge the battery
        # if power (in W) is negative, we discharge the battery
        SOC = self.level/self.capacity

        if (power>0):
            VOC = self.VOC((SOC, self.temperature))
            R_internal = self.R_internal((SOC, self.temperature))
            if R_internal == 0:
                R_internal = 1e-10 ## avoid division by zero
            I = (-VOC + np.sqrt(VOC**2 + 4*R_internal*power))/(2*R_internal) 
            self.level += I*deltaT
            self.level = min(self.level, self.capacity)
        else:
            VOC = self.VOC((SOC, self.temperature))
            R_internal = self.R_internal((SOC, self.temperature))
            if R_internal == 0:
                R_internal = 1e-10 ## avoid division by zero
            power = np.abs(power)
            I = (VOC - np.sqrt(VOC**2 - 4*R_internal*power))/(2*R_internal)
            self.level -= I*deltaT
            self.level = max(self.level, 0)
    
    def apply_age (self, deltaT):
        loss = np.exp(-deltaT/self.discharge_tau)
        self.capacity *= loss
        self.level *= loss
        

