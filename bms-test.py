#! /usr/bin/env python

import bms

from bms.battery import Battery as Bat
from bms.controller import Controller as Ctr

battery = Bat(11.6)
print('Battery voltage:', battery.voltage)

controller = Ctr(battery)
print('Battery voltage from controller:', controller.battery.voltage)

battery.set_voltage(10.1)
print('Battery voltage from controller:', controller.battery.voltage)
