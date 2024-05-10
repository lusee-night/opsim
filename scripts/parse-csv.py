#! /usr/bin/env python
#######################################################################
# The script to convert the CSV-formatted data about the satellite
# trajectory, to HDF5 for compactness and efficiency, also converting
# time to MJD to conform with the usual convention.
#######################################################################

import argparse

import csv
import h5py

from datetime import datetime

import numpy as np

# lusee/opsim
from    nav.coordinates import *
from    lunarsky.time   import Time

parse_time_string = '%d %b %Y %H:%M:%S.%f'
# ----------------------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-I", "--inspect",      action='store_true', help="Inspect CSV and exit")
parser.add_argument("-o", "--outputfile",   type=str,            help="The output", default='')
parser.add_argument("-i", "--inputfile",    type=str,            help="The CSV file to read", default='')
parser.add_argument("-f", "--fields",       type=str,            help="Column numbers to process, comma-separated, default ALL, zero is always included", default='')
parser.add_argument("-N", "--N",            type=int,            help="Optional: max lines to process", default=0)
# ----------------------------------------------------------------------------------
args        = parser.parse_args()

verb        = args.verbose
inspect     = args.inspect
outputfile  = args.outputfile
inputfile   = args.inputfile
fields      = args.fields
N           = args.N

# ---
if verb:
    print("*** Verbose mode ***")
    if not inspect:
        print(f'''*** Input file: {inputfile}, output file (HDF5): "{outputfile}" ***''')
    else:
        print(f'''*** Inspect mode. File to inspect (will exit on completion): "{inputfile}" ***''')

# ----------------------------------------------------------------------------------
csv_file, csv_reader = None, None
buffer = []
line_count = 0
header = ''

try:
    csv_file = open(inputfile, "r")
except:
    if verb: print(f'Problem opening the input CSV file {inputfile}, exiting...')
    exit(-3)

try:
    csv_reader = csv.reader(csv_file, delimiter=',')
except:
    if verb: print(f'Problem creating a CSV reader for the file {inputfile}, exiting...')
    exit(-3)

# -- INSPECT EXISTING DATA AND EXIT
if inspect : 
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
    t_start =   Time(datetime.strptime(start_time,   parse_time_string))
    t_end   =   Time(datetime.strptime(current_time, parse_time_string))
    print(f'Time range of the data (string format ** MJD): "{start_time} ** {t_start.mjd}" to "{current_time} ** {t_end.mjd}"')
    exit(0)

index_list = []
if len(fields)>0:
    try:
        indices = fields.split(',')
        if 0 not in index_list: index_list.append(0)
        for index in indices: index_list.append(int(index))
        if verb and len(index_list)>0: print('*** Will select columns: ', index_list, '***')
    except:
        if verb: print('Error parsing fields, exiting...')
        exit(-4)
else:
    if verb: print('*** All columns in the file fill be processed ***')


# -- PROCESS
for row in csv_reader:
    if line_count == 0:
        line_count += 1
        if len(index_list)>0:
            row = [row[i] for i in index_list]
        header = ','.join(row) # preserve, to add to the metadata in HDF5; then skip to the data
        continue

    if N>0 and line_count>N: break

    if (len(row) == 0): break # protect against the trailing empty string(s)
    my_time =  Time(datetime.strptime(row[0], '%d %b %Y %H:%M:%S.%f'))
    row[0] = my_time.mjd

    if len(index_list)>0:
        row = [float(row[i]) for i in index_list]
    else:
        row = [float(x) for x in row]

    buffer.append(row) # print(row)
    line_count += 1

result = np.array(buffer, dtype=np.float64)

if verb:
    print(f'*** Finished calculations, formed the data package, size: {result.shape}... ***')
    print(f'*** Header: {header} ***')

if outputfile == '': # print useful info and exit
    if verb:
        print(f'''*** No output file name detected, will exit now. Shape of the orbitals data: {result.shape} ***''')
        print('*** First 10 rows ***')
        for i in range(10):
            try:
                print(result[i])
            except:
                pass
    exit(0)


# HDF5 output -- there will be two groups, (a) meta and (b) the payload data
if verb: print(f'*** Writing to HDF file {outputfile} ***')
f = h5py.File(outputfile, 'w')

grp_meta = f.create_group('meta')
dt = h5py.string_dtype(encoding='utf-8')
ds_meta = grp_meta.create_dataset('header', (1,), dtype=dt)
ds_meta[0,] = header


if verb: print(f'*** Writing the trajectory data ***')
grp_data = f.create_group('data')
ds_data = grp_data.create_dataset("trajectory", data=result, compression="gzip")

f.close()
if verb: print(f'*** All done ***')
exit(0)

