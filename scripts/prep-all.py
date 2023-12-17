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

# Example of the time range: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

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
        print(f'''*** File to inspect: "{inspectfile}" ***''')



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

# -- PRODUCE DATA
if conffile=='' or outputfile=='':
    print('Incomplete input parameters, exiting...')
    exit(-2)

f = open(conffile, 'r')
conf = yaml.safe_load(f)  # ingest the configuration data

if verb:
    print("*** Top-level configuration keys ***")
    print(*conf.keys())

# groups = {}

f = h5py.File(outputfile, 'w')

grp_meta = f.create_group('meta')

dt = h5py.string_dtype(encoding='utf-8')                     
ds_meta = grp_meta.create_dataset('configuration', (1,), dtype=dt)
ds_meta[0,] = yaml.dump(conf)

# ---
t_start, t_end = (conf['period']['start'], conf['period']['end']) # a tuple of (start, end)

if verb:
    print(f'''*** Time range: "{t_start}" to "{t_end}"***''')

# ------------------------------------------------------
#
# Do the calculation (solar and sat)
#

# Lander location
loc = conf['location']
lat = loc['latitude']
lon = loc['longitude']

print(f'''Latitude: {lat}, longitude: {lon}''')
observation = O((t_start, t_end), lat, lon)
(times, alt, az) = track_from_observation(observation) # Sun
N = times.size
mjd = [t.mjd for t in times]

if verb: print(f'''Sun: generated {N} data points''')

esa = conf['satellites']['esa']
semi_major_km               = esa['semi_major_km']
eccentricity                = esa['eccentricity']
inclination_deg             = esa['inclination_deg']
raan_deg                    = esa['raan_deg']
argument_of_pericenter_deg  = esa['argument_of_pericenter_deg']
aposelene_ref_time          = Time(esa['aposelene_ref_time'])


esaSat      = Satellite(semi_major_km, eccentricity, inclination_deg, raan_deg, argument_of_pericenter_deg, aposelene_ref_time)
obsEsaSat   = ObservedSatellite(observation, esaSat)

N = len(obsEsaSat.mjd)
if verb: print(f'''ESA Satellite: generated {N} data points''')


elytra = conf['satellites']['elytra']
semi_major_km               = elytra['semi_major_km']
eccentricity                = elytra['eccentricity']
inclination_deg             = elytra['inclination_deg']
raan_deg                    = elytra['raan_deg']
argument_of_pericenter_deg  = elytra['argument_of_pericenter_deg']
aposelene_ref_time          = Time(elytra['aposelene_ref_time'])


elytraSat      = Satellite(semi_major_km, eccentricity, inclination_deg, raan_deg, argument_of_pericenter_deg, aposelene_ref_time)
obsElytraSat   = ObservedSatellite(observation, elytraSat)

N = len(obsElytraSat.mjd)
if verb: print(f'''Elytra Satellite: generated {N} data points''')

result = np.column_stack((mjd, alt, az, obsEsaSat.alt, obsEsaSat.az, obsElytraSat.alt, obsElytraSat.az))

grp_data = f.create_group('data')
ds_data = grp_data.create_dataset("orbitals", data=result)


f.close()

exit(0)

# Reference: the satellite ctor API
# semi_major_km               = 5738,
# eccentricity                = 0.56489,
# inclination_deg             = 57.097,
# raan_deg                    = 0,
# argument_of_pericenter_deg  = 72.625,
# aposelene_ref_time          = Time("2024-05-01T00:00:00")
