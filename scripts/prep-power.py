#! /usr/bin/env python
import argparse
from nav.coordinates import *

#######################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Verbose mode")
parser.add_argument("-c", "--cachefile",type=str,            help="The cache file for Sun coordinates (input)", default='')
parser.add_argument("-p", "--power",    type=str,            help="The cache file for the power data (output)", default='')
#######################################

# Example of the time range: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

cachefile   = args.cachefile
power       = args.power
verb        = args.verbose

if verb:
    print("*** Verbose mode ***")
    print(f'''*** Using nav cache file: "{cachefile}", writing to the power cache file: "{power}" ***''')

# "track" is imported from "coordinates", and wraps "Observation"
# (times, alt, az) = track(timerange)

# N = times.size

# print(N)
# mjds = np.empty(N)
# for i in range(N): mjds[i] = times[i].mjd

# result = np.column_stack((mjds, alt, az))

# print(result)

# with open(cachefile, 'wb') as f:
#     np.save(f, result)
    
exit(0)