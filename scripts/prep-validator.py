#! /usr/bin/env python
import argparse
import os

#######################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Verbose mode")
parser.add_argument("-c", "--cachefile",type=str,            help="The cache file for Sun coordinates (input)", default='')
parser.add_argument("-p", "--power",    type=str,            help="The cache file for the power data (output)", default='')
#######################################

# Example of the time range used to calculate nav cache for the Sun: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

cachefile   = args.cachefile
power       = args.power
verb        = args.verbose

if verb:
    print("*** Verbose mode ***")
    print(f'''*** Using nav cache file: "{cachefile}", writing to the power cache file: "{power}" ***''')
    print(f'''*** Current directory: {os.getcwd()} ***''')

exit(0)