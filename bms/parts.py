import numpy as np
import simpy
from enum import Enum

from bms.panels import EPanel, TPanel, WPanel

#################################################################################
class Battery:
    def __init__(self, voltage=0.0, charge=0.0, temperature=0.0):
        self.voltage    = voltage
        self.charge     = charge
        self.temperature= temperature

    def set_voltage(self, voltage):
        self.voltage = voltage

    def set_temperature(self, temperature):
        self.temperature = temperature

#################################################################################
class Controller:
    def __init__(self, battery, env=None):
        self.panels     = []
        self.devices    = []
        self.battery    = battery
        self.env        = env


    ### PANELS SECTION ###
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

    ### Simpy machinery
    def run(self):
        while True:
            print(f'''Clock {self.env.now}''')
            yield self.env.timeout(1)

#################################################################################
class Device():
    def __init__(self, name='', state=None):
        self.name   = name
        self.state  = state

    def set_state(self, state):
        self.state = state

    def set_voltage(self, voltage):
        self.voltage = voltage
