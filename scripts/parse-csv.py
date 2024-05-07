#! /usr/bin/env python
#######################################################################
# The script to prepare ALL of the "orbitals" data e.g. Sun, satellites
#######################################################################

import argparse
import yaml
import csv
import h5py

# lusee/opsim
from    nav.coordinates import *
from    lunarsky.time   import Time
# ----------------------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-o", "--outputfile",   type=str,            help="The output", default='')
parser.add_argument("-i", "--inspectfile",  type=str,            help="File to inspect (overrides other options)", default='')
# ----------------------------------------------------------------------------------
args        = parser.parse_args()

verb        = args.verbose
outputfile  = args.outputfile
inspectfile = args.inspectfile

# ---
if verb:
    print("*** Verbose mode ***")
    if inspectfile == '':
        print(f'''*** Output file (HDF5): "{outputfile}" ***''')
    else:
        print(f'''*** File to inspect (will exit on completion): "{inspectfile}" ***''')

# ----------------------------------------------------------------------------------
# -- INSPECT EXISTING DATA
if inspectfile != '': # inspect and exit
    csv_file = open(inspectfile, "r")
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'{len(row)} columns detected. Column names are:')
            print('---------------------------------------')
            i = 0
            for col in row:
                print(f'{i:2} {col}')
                i+=1
            print('---------------------------------------')
            line_count += 1
        else:
            if (len(row) == 0): break
            if line_count == 1: start_time = row[0]
            current_time = row[0]
            line_count += 1

    print(f'Processed {line_count} CSV lines total (including the header).')
    print(f'Time range of the data: "{start_time}" to "{current_time}"')


    exit(0)

# ----------------------------------------------------------------------------------
# -- READ AND PARSE THE CONFIGURATION DATA
#
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
# -- PRODUCE DATA

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

# Combine all data in an array suitable for output
result = np.column_stack((mjd, alt, az, obsLpfSat.alt, obsLpfSat.az, obsBgeSat.alt, obsBgeSat.az))


if verb: print('Finished calculations, formed the data package...')

if outputfile == '': # print useful info and exit
    if verb:
        print(f'''No output file name detected, will exit now. Shape of the orbitals data: {result.shape}''')
    exit(0)


# HDF5 output -- there will be two groups, (a) meta and (b) the payload data
f = h5py.File(outputfile, 'w')

grp_meta = f.create_group('meta')
dt = h5py.string_dtype(encoding='utf-8')
ds_meta = grp_meta.create_dataset('configuration', (1,), dtype=dt)
ds_meta[0,] = yaml.dump(conf)

grp_data = f.create_group('data')
ds_data = grp_data.create_dataset("orbitals", data=result, compression="gzip")

f.close()

exit(0)

