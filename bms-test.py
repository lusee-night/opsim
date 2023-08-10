#! /usr/bin/env python

import bms

from bms.parts import *
from nav.coordinates import *


(alt, az, times) = track("2025-02-04 00:00:00 to 2025-02-05 23:45:00")

print(times.size, sun_rad)

mjds = np.empty(times.size)
for i in range(times.size):
    mjds[i] = times[i].mjd

alt_sun_top = np.asarray(alt)+sun_rad

# using radians:
sun     = altaz2xyz(alt, az)
sun_top = altaz2xyz(alt_sun_top, az)

battery = Battery(11.6)
print('Battery voltage:', battery.voltage)

ctr = Controller(battery)
print('Battery voltage from controller:', ctr.battery.voltage)

battery.set_voltage(10.1)
print('Battery voltage from controller:', ctr.battery.voltage)


e = EPanel('E')
ctr.add_panel(e)

w = WPanel('W')
ctr.add_panel(w)

t = TPanel('T')
ctr.add_panel(t)

e_dot = e.dot(sun)
w_dot = w.dot(sun)
t_dot = t.dot(sun)

e_dot[e_dot<0] = 0.0
w_dot[w_dot<0] = 0.0
t_dot[t_dot<0] = 0.0

print(e_dot, w_dot, t_dot)

for p in ctr.panels:
    print(f'''{p.name}''')
    print(p.normal_rot, p.area)






#o = O("2025-02-04 00:00:00 to 2025-02-05 23:45:00") # 2025-03-07 23:45:00
#print(o.times)
#(alt, az) = o.get_track_solar('sun')
#print(alt)


