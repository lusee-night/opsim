#! /usr/bin/env python
import argparse
import bms

from bms.parts import *
from nav.coordinates import *

#######################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Verbose mode")
parser.add_argument("-f", "--cachefile",type=str,            help="The cache file", default='')
parser.add_argument("-r", "--timerange",type=str,            help="The time range", default='')

args    = parser.parse_args()

timerange   = args.timerange
cachefile   = args.cachefile
verb        = args.verbose

if cachefile!='':
    with open(cachefile, 'rb') as f: mjd_alt_az = np.load(f)
    mjd = mjd_alt_az[:,0]
    alt = mjd_alt_az[:,1]
    az  = mjd_alt_az[:,2]
else:
    # "track" is imported from "coordinates", and wraps "Observation"
    (times, alt, az) = track(timerange)
    mjd = np.empty(times.size)
    for i in range(times.size): mjd[i] = times[i].mjd


#iMidnight = np.argmin(alt)
#iSunrise = np.argmin(np.abs(alt[iMidnight:])) + iMidnight
#hrsFromSunrise = (mjd - mjd[iSunrise])*24
#print(hrsFromSunrise)
#exit(0)

# print(times.size, sun_rad)



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
EPV_choice_list = [e_dot, (1-sun_seg_frac)*e_dot, sun_seg_frac*e_dot, 0]
WPV_choice_list = [w_dot, (1-sun_seg_frac)*w_dot, sun_seg_frac*w_dot, 0]
TPV_choice_list = [t_dot, (1-sun_seg_frac)*t_dot, sun_seg_frac*t_dot_sun_top, 0]

#Apply sunrise condition
EPV_power = np.select(condition_list, EPV_choice_list)
WPV_power = np.select(condition_list, WPV_choice_list)
TPV_power = np.select(condition_list, TPV_choice_list)


for p in ctr.panels:
    print(f'''{p.name}''')
    print(p.normal_rot, p.area)






#o = O("2025-02-04 00:00:00 to 2025-02-05 23:45:00") # 2025-03-07 23:45:00
#print(o.times)
#(alt, az) = o.get_track_solar('sun')
#print(alt)


