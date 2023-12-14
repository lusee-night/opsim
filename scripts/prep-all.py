#! /usr/bin/env python
#######################################################################
# The script to prepare ALL of the conditions data e.g. Sun, satellites
#######################################################################

import argparse
import yaml

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
#######################################

# Example of the time range: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

yamlfile    = args.yamlfile
verb        = args.verbose


# ---
if verb:
    print("*** Verbose mode ***")
    print(f'''*** Configuration file (YAML): "{yamlfile}" ***''')


f = open(yamlfile, 'r')

content = yaml.safe_load(f)


if verb:
    print("*** Top-level keys ***")
    print(*content.keys())
    print("*** Content ***")
    pretty(content)

exit(0)