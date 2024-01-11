#! /usr/bin/env python
#######################################################################
# The script to prepare ALL of the conditions data e.g. Sun, satellites
#######################################################################

import argparse
import yaml

import h5py


# lusee "nav" package

import nav
from nav.coordinates import *

from    lunarsky.time       import Time


# ----------------------------------------------------------------------------------
# Pretty print the dictionary we read from the input YAML, for an extra check:
def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


#######################################
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-c", "--conffile",     type=str,            help="The input - a YAML file containing configuration", default='')
parser.add_argument("-o", "--outputfile",   type=str,            help="The output", default='')
parser.add_argument("-i", "--inspectfile",  type=str,            help="File to inspect (overrides other options)", default='')
#######################################

# Reference time range often used in testing: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args        = parser.parse_args()

verb        = args.verbose
conffile    = args.conffile
outputfile  = args.outputfile
inspectfile = args.inspectfile

# ---
if verb:
    print("*** Verbose mode ***")
    if inspectfile == '':
        print(f'''*** Configuration file (YAML): "{conffile}" ***''')
        print(f'''*** Output file (HDF5): "{outputfile}" ***''')
    else:
        print(f'''*** File to inspect (will exit on completion): "{inspectfile}" ***''')

# -- INSPECT EXISTING DATA
if inspectfile != '': # inspect and exit
    f = h5py.File(inspectfile, "r")
    ds_meta = f["/meta/configuration"]
    conf    = yaml.safe_load(ds_meta[0,])
    check   = yaml.dump(conf)
    print(check)

    ds_data = f["/data/orbitals"]
    data_array = np.array(ds_data[:])
    print(f'''Shape of the data payload: {data_array.shape}''')

    print('First 10 rows')
    print(data_array[:10])

    exit(0)

# ----------------------------------------------------------------------------------
# -- PRODUCE DATA
if conffile=='':
    print('Missing configuration, exiting...')
    exit(-2)


try:
    conf_f = open(conffile, 'r')
    conf = yaml.safe_load(conf_f)  # ingest the configuration data
except:
    print('Error opening and reading the configuration file:', conffile)
    exit(-2)

if verb:
    print("*** Top-level configuration keys ***")
    print(*conf.keys())

# ---
prd = conf['period']
t_start, t_end, deltaT= (prd['start'], prd['end'], prd['deltaT'])

if verb:
    print(f'''*** Time range: "{t_start}" to "{t_end}, time step: {deltaT}"***''')

# ------------------------------------------------------
# Do the calculation (solar and sat)

# Lander location
loc = conf['location']
lat = loc['latitude']
lon = loc['longitude']
hgt = loc['height']

print(f'''Latitude: {lat}, longitude: {lon}''')

# Initialize the Observation obejct with the data gleaned from the configuraiton file
observation = O((t_start, t_end), lat, lon, hgt, deltaT)
(times, alt, az) = track_from_observation(observation) # Sun
N = times.size
mjd = [t.mjd for t in times]

if verb: print(f'''Sun: generated {N} data points''')

lpf = conf['satellites']['lpf']
semi_major_km               = lpf['semi_major_km']
eccentricity                = lpf['eccentricity']
inclination_deg             = lpf['inclination_deg']
raan_deg                    = lpf['raan_deg']
argument_of_pericenter_deg  = lpf['argument_of_pericenter_deg']
aposelene_ref_time          = Time(lpf['aposelene_ref_time'])


lpfSat      = Satellite(semi_major_km, eccentricity, inclination_deg, raan_deg, argument_of_pericenter_deg, aposelene_ref_time)
obsLpfSat   = ObservedSatellite(observation, lpfSat)

N = len(obsLpfSat.mjd)
if verb: print(f'''LPF (ESA) Satellite: generated {N} data points''')


bge = conf['satellites']['bge']
semi_major_km               = bge['semi_major_km']
eccentricity                = bge['eccentricity']
inclination_deg             = bge['inclination_deg']
raan_deg                    = bge['raan_deg']
argument_of_pericenter_deg  = bge['argument_of_pericenter_deg']
aposelene_ref_time          = Time(bge['aposelene_ref_time'])


bgeSat      = Satellite(semi_major_km, eccentricity, inclination_deg, raan_deg, argument_of_pericenter_deg, aposelene_ref_time)
obsBgeSat   = ObservedSatellite(observation, bgeSat)

N = len(obsBgeSat.mjd)
if verb: print(f'''BGE (ELytra) Satellite: generated {N} data points''')

result = np.column_stack((mjd, alt, az, obsLpfSat.alt, obsLpfSat.az, obsBgeSat.alt, obsBgeSat.az))


if verb: print('Finished calculations...')

if outputfile == '': # print useful info and exit
    if verb:
        print(f'''No output file name detected, will exit now. Shape of the orbitals data: {result.shape}''')
    exit(0)


# Let's output the results, formatted in HDF5
f = h5py.File(outputfile, 'w')
grp_meta = f.create_group('meta')
dt = h5py.string_dtype(encoding='utf-8')                     
ds_meta = grp_meta.create_dataset('configuration', (1,), dtype=dt)
ds_meta[0,] = yaml.dump(conf)

grp_data = f.create_group('data')
ds_data = grp_data.create_dataset("orbitals", data=result)
f.close()

exit(0)

# ----- ATTIC
# Reference numbers: originally in the satellite ctor API
# semi_major_km               = 5738,
# eccentricity                = 0.56489,
# inclination_deg             = 57.097,
# raan_deg                    = 0,
# argument_of_pericenter_deg  = 72.625,
# aposelene_ref_time          = Time("2024-05-01T00:00:00")
