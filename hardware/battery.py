from simpy import Container as C
#################################################################################
class Battery(C):
    def __init__(self, env, config):
        
        
        self.capacity_Wh = float(config['capacity'])
        self.initial_Wh = float(config['initial'])
        self.fiducial_voltage = float(config['fiducial_voltage'])
        self.charge_efficiency = float(config['charge_efficiency'])
        self.discharge_efficiency = float(config['discharge_efficiency'])
        self.fiducial_voltage = float(config['fiducial_voltage'])
        self.temperature = 0.0
        Wh2As = 1/self.fiducial_voltage*3600 # /28V * 3600s/h
        C.__init__(self, env, init=self.initial_Wh*Wh2As, capacity=self.capacity_Wh*Wh2As)
        self.Vfunc = lambda f,T:self.fiducial_voltage # placeholder
        self.verbose    = True

    def Voltage(self):
        fill = self.level/self.capacity
        T = self.temperature
        return self.Vfunc(fill,T)

    def set_temperature(self, temperature):
        self.temperature = temperature

    def charge (self, power, deltaT):
        self.put (power*deltaT/self.Voltage()*self.charge_efficiency)
        
    def discharge (self, power, deltaT):
        self.get (power*deltaT/self.Voltage()/self.discharge_efficiency)