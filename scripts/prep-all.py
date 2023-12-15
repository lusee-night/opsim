#! /usr/bin/env python
#######################################################################
# The script to prepare ALL of the conditions data e.g. Sun, satellites
#######################################################################

import argparse
import yaml

import h5py

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



if inspectfile != '': # inspect and exit
    f = h5py.File(inspectfile, "r")
    ds = f["/meta/configuration"]
    # confstring = list(ds)[0]
    conf    = yaml.safe_load(ds[0,])
    check   = yaml.dump(conf)
    print(check)
    exit(0)


if conffile=='' or outputfile=='':
    print('Incomplete input parameters, exiting...')
    exit(-2)

f = open(conffile, 'r')

conf = yaml.safe_load(f)  # ingest the configuration data

if verb:
    print("*** Top-level configuration keys ***")
    print(*conf.keys())
    # print("*** Content ***")
    # pretty(content)


# groups = {}

f = h5py.File(outputfile, 'w')
grp = f.create_group('meta')

dt = h5py.string_dtype(encoding='utf-8')                     
ds = grp.create_dataset('configuration', (1,), dtype=dt)
ds[0,] = yaml.dump(conf)
f.close()

exit(0)

# for cntK, cntV in content.items():
#     grp = f.create_group(cntK)
#     if isinstance(cntV, dict):
#         l = len(cntV)
#         print('!', l, cntV)
#         ds = grp.create_dataset('VLDS', (l,), dtype=dt)
#         for i in range(0,l):
#             ds[i] = cntV[i]
#     groups[cntK] = grp
#dt = h5py.string_dtype(encoding='utf-8')
#ds = grp.create_dataset('VLDS', (100,100), dtype=dt)
#ds[0,2] = 'foo'