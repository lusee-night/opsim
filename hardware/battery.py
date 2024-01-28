
from scipy.interpolate import RegularGridInterpolator
import numpy as np


class Battery:
    def __init__(self, env, config):
        self.verbose = True
        self.temperature = None 
        self.level = float(config['initial'])*3600 # to As
        self.capacity = float(config['capacity'])*(1-float(config['capacity_fade']))*3600
        self.R_internal = float(config['R_internal'])
        self_discharge = float(config['self_discharge'])
        self.discharge_tau = -28*24*3600/np.log(1-self_discharge)
        table_fn = config['VOC_table']
        VOC_table_cols = config['VOC_table_cols']
        self.read_VOC_table(table_fn, VOC_table_cols)
        

    def read_VOC_table(self, table_fn, VOC_table_cols):
        if self.verbose: print ('Reading VOC table from %s' % table_fn)
        VOC_table = np.genfromtxt(table_fn, delimiter=' ', comments='#')
        charge_cols = []
        discharge_cols = []
        charge_temps = []
        discharge_temps = []
        soc_col = None
        err = False
        for i, el in enumerate(VOC_table_cols.split()):
            if el == 'SOC':
                soc_col = i
            else:
                try:
                    C, T = el.split('@')
                    if C == 'C':
                        charge_cols.append(i)
                        charge_temps.append(float(T))
                    elif C == 'D':
                        discharge_cols.append(i)
                        discharge_temps.append(float(T))
                except:
                    print('Cannot parse VOC table. Column %d has value %s' % (col, val))
                    sys.exit(1)
        if soc_col is None:
            print('Cannot parse VOC table. No SOC column')
            sys.exit(1)
        SOC = VOC_table[:, soc_col]/100.0 # convert from percent to fraction
        charge_table = VOC_table[:, charge_cols]
        discharge_table = VOC_table[:, discharge_cols]
        self.charge_VOC = RegularGridInterpolator((SOC, charge_temps), charge_table)
        self.discharge_VOC = RegularGridInterpolator((SOC, discharge_temps), discharge_table)



    def Voltage(self):
        SOC = self.level/self.capacity
        return self.discharge_VOC((SOC,self.temperature))

    def set_temperature(self, temperature):
        self.temperature = temperature

    def apply_power (self, power, deltaT):
        # Applies power to the battery for deltaT seconds
        # if power (in W) is positive, we charge the battery
        # if power (in W) is negative, we discharge the battery
        SOC = self.level/self.capacity
        if (power>0):
            V = self.charge_VOC((SOC, self.temperature))
            I = power/V
            self.level += I*deltaT
            self.level = min(self.level, self.capacity)
        else:
            V = self.discharge_VOC((SOC, self.temperature))
            power = np.abs(power)
            I = (V - np.sqrt(V**2 - 4*self.R_internal*power))/(2*self.R_internal)
            self.level -= I*deltaT
            self.level = max(self.level, 0)
    
    def age (self, deltaT):
        loss = np.exp(-deltaT/self.discharge_tau)
        self.capacity *= loss
        self.level *= loss
        

