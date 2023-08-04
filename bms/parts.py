class Battery:
    def __init__(self, voltage=0.0):
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage


class Controller:
    def __init__(self, battery):
        self.consumers = []
        self.battery = battery

#    def set_voltage(self, voltage):
#        self.voltage = voltage

class Device:
    def __init__(self, name='', voltage=0.0):
        self.name = name
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage
