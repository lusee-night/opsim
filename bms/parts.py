
from bms.panels import EPanel, TPanel, WPanel
import numpy as np

class Battery:
    def __init__(self, voltage=0.0, charge=0.0):
        self.voltage    = voltage
        self.charge     = charge

    def set_voltage(self, voltage):
        self.voltage = voltage


class Controller:
    def __init__(self, battery):
        self.panels     = []
        self.devices    = []
        self.battery    = battery
    ###
    def add_panel(self, panel):
        self.panels.append(panel)
    ###
    def add_all_panels(self, sun):
        self.add_panel(EPanel(sun, 'E'))
        self.add_panel(WPanel(sun, 'W'))
        self.add_panel(TPanel(sun, 'T'))
    ###
    def get_panel(self, name):
        for p in self.panels:
            if p.name==name: return p
        return None
    ###
    def panels_info(self):
        info = f'''Number of panels: {len(self.panels)}\n'''
        for p in self.panels:
            info += f'''Panel info: {p.info()}\n'''
        print(info)

    def panels_power(self):
        power = None
        for p in self.panels:
            if power is None:
                power = p.power()
            else:
                power = power + p.power()

        return power


    def set_condition(self, condition_list):
        for p in self.panels:
            p.set_condition(condition_list)

class Device:
    def __init__(self, name='', voltage=0.0):
        self.name = name
        self.voltage = voltage

    def set_voltage(self, voltage):
        self.voltage = voltage
