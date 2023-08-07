#! /usr/bin/env python


import lusee
from lusee import Observation as O

import bms

from bms.parts import *

battery = Battery(11.6)
print('Battery voltage:', battery.voltage)

ctr = Controller(battery)
print('Battery voltage from controller:', ctr.battery.voltage)

battery.set_voltage(10.1)
print('Battery voltage from controller:', ctr.battery.voltage)



ctr.add_panel(WPanel('W'))
ctr.add_panel(EPanel('E'))
ctr.add_panel(TPanel('T'))

for p in ctr.panels:
    print(f'''{p.name}''')
    print(p.normal_rot)






#o = O("2025-02-04 00:00:00 to 2025-02-05 23:45:00") # 2025-03-07 23:45:00
#print(o.times)
#(alt, az) = o.get_track_solar('sun')
#print(alt)


