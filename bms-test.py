#! /usr/bin/env python

import bms

from bms.parts import *
from nav.coordinates import *


(alt, az, times) = track("2025-02-04 00:00:00 to 2025-02-05 23:45:00")

print(times.size)

mjds = np.empty(times.size)
for i in range(times.size):
    mjds[i] = times[i].mjd

print(mjds)

# print(alt)

alt_sun_top = np.asarray(alt)+sun_rad

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
    print(p.normal_rot, p.area)






#o = O("2025-02-04 00:00:00 to 2025-02-05 23:45:00") # 2025-03-07 23:45:00
#print(o.times)
#(alt, az) = o.get_track_solar('sun')
#print(alt)


