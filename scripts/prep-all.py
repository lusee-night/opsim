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
parser.add_argument("-y", "--yamlfile",     type=str,            help="The input - a YAML file containing configuration", default='')
parser.add_argument("-o", "--outputfile",   type=str,            help="The outpuut", default='')
#######################################

# Example of the time range: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

yamlfile    = args.yamlfile
outputfile  = args.outputfile
verb        = args.verbose


# ---
if verb:
    print("*** Verbose mode ***")
    print(f'''*** Configuration file (YAML): "{yamlfile}" ***''')
    print(f'''*** Output file (YAML): "{outputfile}" ***''')


f = open(yamlfile, 'r')

content = yaml.safe_load(f)


if verb:
    print("*** Top-level keys ***")
    print(*content.keys())
    print("*** Content ***")
    pretty(content)


f = h5py.File(outputfile, 'w')


groups = {}


parsed = yaml.dump(content)


dt = h5py.string_dtype(encoding='utf-8')


grp = f.create_group('test')
                     
ds = grp.create_dataset('VLDS', (1,), dtype=dt)
ds[0,] = parsed

anew = yaml.safe_load(ds[0,])
again = yaml.dump(anew)

print(again)


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


f.close()

exit(0)