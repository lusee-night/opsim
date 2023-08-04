#! /usr/bin/env python

import bms

from bms.parts import *

battery = Battery(11.6)
print('Battery voltage:', battery.voltage)

controller = Controller(battery)
print('Battery voltage from controller:', controller.battery.voltage)

battery.set_voltage(10.1)
print('Battery voltage from controller:', controller.battery.voltage)
