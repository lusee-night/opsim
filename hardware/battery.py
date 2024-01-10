from simpy import Container as C
#################################################################################
class Battery(C):
    def __init__(self, env, charge=0.0, capacity = 0., voltage=0.0, temperature=0.0):
        C.__init__(self, env, init=charge, capacity=capacity)
        self.voltage    = voltage
        self.charge     = charge
 
        self.temperature= temperature
        self.verbose    = True

    def set_voltage(self, voltage):
        self.voltage = voltage

    def set_temperature(self, temperature):
        self.temperature = temperature
