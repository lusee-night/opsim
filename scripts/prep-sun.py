#! /usr/bin/env python
import argparse
from nav.coordinates import *

#######################################
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-V", "--veryverbose",  action='store_true', help="Very verbose mode")

parser.add_argument("-c", "--cachefile",type=str, help="The cache file for Sun coordinates (output)", default='')
parser.add_argument("-t", "--timerange",type=str, help="The time range", default='')

parser.add_argument("-b", "--begin",    type=str, help="Begin (start)", default='')
parser.add_argument("-e", "--end",      type=str, help="End (stop)", default='')
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

if begin != '' and end !='': timerange = (begin, end)

if verb:
    print("*** Verbose mode ***")
    print(f'''*** Cache file: "{cachefile}", time range: "{timerange}" ***''')

(times, alt, az) = track(timerange) # "track" is imported from "coordinates", and wraps "Observation"

N = times.size

print(N)
mjds = np.empty(N)
for i in range(N): mjds[i] = times[i].mjd

result = np.column_stack((mjds, alt, az))

if very: print(result)

if cachefile != '':
    with open(cachefile, 'wb') as f:
        np.save(f, result)
    
exit(0)