#! /usr/bin/env python

import bms

from bms.parts import *
from nav.coordinates import *


(alt, az, times) = track("2025-02-10 00:00:00 to 2025-02-27 23:45:00")

mjd = np.empty(times.size)
for i in range(times.size):
    mjd[i] = times[i].mjd

iMidnight = np.argmin(alt)
iSunrise = np.argmin(np.abs(alt[iMidnight:])) + iMidnight
hrsFromSunrise = (mjd - mjd[iSunrise])*24
print(hrsFromSunrise)
exit(0)

print(times.size, sun_rad)



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

# When dot product is negative, panel is not illuminated
e_dot[e_dot<0] = 0.0
w_dot[w_dot<0] = 0.0
t_dot[t_dot<0] = 0.0

t_dot_sun_top = t.dot(sun_top)
t_dot_sun_top[t_dot_sun_top<0] = 0.0 # For finite disk at sunrise/sunset. Slight aprx: top of sun not center of segment

# print(e_dot, w_dot, t_dot)

# Sanitize input to arccos and sqrt. Values where h<0 are non-physical and will be cut by condition_list.
alt_seg = np.abs(alt)
alt_seg[alt_seg>sun_rad]=sun_rad
sun_seg_area = (sun_rad**2)*np.arccos(1-((sun_rad-alt_seg)/sun_rad))-alt_seg*np.sqrt((sun_rad**2)-(alt_seg)**2)
sun_seg_frac = sun_seg_area/(np.pi*sun_rad**2)

# Conditions are selected in order, as in an if-elif statement
condition_list = [alt>horizon+sun_rad, alt>horizon, alt>horizon-sun_rad, alt<=horizon-sun_rad]

# Full sun, subtract sun segment, add only sun segment, full disk below horizon
EPV_choice_list = [e_dot, (1-sun_seg_frac)*EPV_dot, sun_seg_frac*e_dot, 0]
WPV_choice_list = [w_dotdot, (1-sun_seg_frac)*WPV_dot, sun_seg_frac*w_dot, 0]
TPV_choice_list = [t_dot, (1-sun_seg_frac)*TPV_dot, sun_seg_frac*t_dot_sun_top, 0]


for p in ctr.panels:
    print(f'''{p.name}''')
    print(p.normal_rot, p.area)






#o = O("2025-02-04 00:00:00 to 2025-02-05 23:45:00") # 2025-03-07 23:45:00
#print(o.times)
#(alt, az) = o.get_track_solar('sun')
#print(alt)


