from simpy import Container as C
#################################################################################
class Battery(C):
    def __init__(self, env, initial_Wh, capacity_Wh, fiducial_voltage, 
                 charge_efficiency = 0.95, discharge_efficiency = 0.95
                 Vfunc=None):
        
        self.fiducial_voltage = fiducial_voltage
        self.voltage    = fiducial_voltage
        self.charge     = charge
        self.temperature = 0.0
        Wh2As = 1/fiducial_voltage*3600 # /28V * 3600s/h
        C.__init__(self, env, init=initial_Wh*Wh2As, capacity=capacity_Wh*Wh2As)
        self.Vfunc = Vfunc if Vfunc is not None else lambda f,T:fiducial_voltage
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        self.verbose    = True

    def Voltage(self):
        fill = self.level/self.capacity
        T = self_temperature
        return self.Vfunc(fill,T)

    def set_temperature(self, temperature):
        self.temperature = temperature

    def charge (self, power, deltaT):
        self.put (power*deltaT/self.Volrage()*self.charge_efficiency)
        
    def discharge (self, power, deltaT):
        self.get (power*deltaT/self.Voltage()/self.discharge_efficiency)