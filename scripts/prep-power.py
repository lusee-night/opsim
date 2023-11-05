#! /usr/bin/env python
import argparse
import os

from nav.coordinates    import *
from bms.battery        import Battery
from bms.controller     import Controller

#######################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Verbose mode")
parser.add_argument("-c", "--cachefile",type=str,            help="The cache file for Sun coordinates (input)", default='')
parser.add_argument("-p", "--power",    type=str,            help="The cache file for the power data (output)", default='')
#######################################

# Example of the time range used to calculate nav cache for the Sun: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

cachefile   = args.cachefile
power       = args.power
verb        = args.verbose

if verb:
    print("*** Verbose mode ***")
    print(f'''*** Using nav cache file: "{cachefile}", writing to the power cache file: "{power}" ***''')
    print(f'''*** Current directory: {os.getcwd()} ***''')

mySun = Sun()
mySun.verbose=verb

# NB. In this app the temperature curve for the Sun is not set, efficiency will default to 1.0

mySun.read_trajectory(cachefile)
if verb: print(f'''*** Number of points read from the file {cachefile}: {mySun.N} ***''')

# Dummy battery, needed for the controller API
# It must have none-zero capacity because of the SimPy requirements
battery = Battery(env=None, capacity=1000.)

# Create thec controller and set the sun information for it
ctr = Controller(battery)
ctr.add_all_panels(mySun)
ctr.set_condition(mySun.condition)


# Harvest the power -- this method is just an aggregator
ctr.calculate_power()

if power=='':
    for p in ctr.power: print(p)
    exit(0)

with open(power, 'wb') as f: np.save(f, pwr)


exit(0)