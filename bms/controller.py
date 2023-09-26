from    bms.panels  import *
from    bms.parts   import *

#################################################################################
class Controller:
    def __init__(self, env=None, time = None, battery = None, monitor = None):
        self.time       = time
        self.battery    = battery
        self.env        = env
        self.monitor    = monitor
        self.panels     = []
        self.devices    = []



    ### PANELS SECTION ###
    def add_panel(self, panel):
        self.panels.append(panel)

    ### DEVICES SECTION ###
    def add_device(self, device):
        self.devices.append(device)

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

    ###
    def panels_power(self):
        power = None
        for p in self.panels:
            if power is None:
                power = p.power()
            else:
                power = power + p.power()

        return power

    ###
    def set_condition(self, condition_list):
        for p in self.panels:
            p.set_condition(condition_list)

    ###
    def set_time(self, time):
        self.time = time

    ### SimPy machinery
    # print(f'''Clock: {self.time[myT]}, power: {Panel.profile[myT]}''')

    def run(self):
        while True:
            myT = int(self.env.now)

            myPwr = Panel.profile[myT]
            self.monitor.buffer[myT] = myPwr
            try:
                self.battery.put(myPwr)
            except:
                pass

            for d in self.devices:
                self.battery.get(d.current) # print(self.battery.level)

            self.monitor.charge+=myPwr
            self.monitor.battery[myT] = self.battery.level
            
            yield self.env.timeout(1)
