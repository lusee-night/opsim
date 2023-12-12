#! /usr/bin/env python
import argparse

from nav.coordinates    import *

# The script to prepare ALL of the conditions data. NB. on hold due to refactoring

#######################################
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-V", "--veryverbose",  action='store_true', help="Very verbose mode")

parser.add_argument("-c", "--cachefile",    type=str,            help="The cache file (output)", default='')
parser.add_argument("-t", "--timerange",    type=str,            help="The time range", default='')

parser.add_argument("-b", "--begin",        type=str,            help="Begin (start)", default='')
parser.add_argument("-e", "--end",          type=str,            help="End (stop)", default='')
#######################################

# Example of the time range: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

cachefile   = args.cachefile
timerange   = args.timerange

verb        = args.verbose
very        = args.veryverbose

begin       = args.begin
end         = args.end

# ---
if verb:
    print("*** Verbose mode ***")
    print(f'''*** Cache file (output): "{cachefile}", begin: "{begin}, end: {end}" ***''')


if begin=='' or end=='':
    if verb:
        print('Missing inputs, exiting...')
    exit(-1)

(times, alt, az) = track((begin, end)) # "track" is imported from "coordinates", and wraps "Observation"

N = times.size

if verb: print(f'''Number of points: {N}''')

mjds = np.empty(N)
for i in range(N): mjds[i] = times[i].mjd # FIXME - change to list comprehension later

result = np.column_stack((mjds, alt, az))

if very: print(result)

if cachefile != '':
    with open(cachefile, 'wb') as f:
        np.save(f, result)
    
exit(0)