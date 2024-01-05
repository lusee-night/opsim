#! /usr/bin/env python

#######################################
# Work in progress, coding deferred
# until we add same to the sim notebook
#######################################


import argparse
import os

#######################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Verbose mode")
parser.add_argument("-c", "--cachefile",type=str,            help="The cache file for Sun coordinates (input)", default='')
parser.add_argument("-p", "--power",    type=str,            help="The cache file for the power data (iput)", default='')
#######################################

# Example of the time range used to calculate nav cache for the Sun: "2025-02-04 00:00:00 to 2025-03-07 23:45:00"

args    = parser.parse_args()

cachefile   = args.cachefile
power       = args.power
verb        = args.verbose

if power!='' and cachefile!='':
    print('Please select either the Sun coordinates file, or the power series cache file... Will exit now...')
    exit(-1)

if verb:
    print("*** Verbose mode ***")
    print(f'''*** Current directory: {os.getcwd()} ***''')

if verb:
    if cachefile!='': print(f'''*** Using the nav cache file: "{cachefile}" ***''')
    if power!='': print(f'''*** Using the power cache file: "{power}" ***''')

exit(0)
