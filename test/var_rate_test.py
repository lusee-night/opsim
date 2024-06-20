#! /usr/bin/env python
#######################################################################
# The script for the unit test of the variable data transfer rate
#######################################################################


import os, sys
import argparse

##############################################



# -------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", action='store_true', help="Verbose mode")
args    = parser.parse_args()

verbose = args.verbose


# -------------------------------------------------------------


try:
    luseepy_path=os.environ['LUSEEPY_PATH']
    if verbose: print(f'''The LUSEEPY_PATH is defined in the environment: {luseepy_path}, will be added to sys.path''')
    sys.path.append(luseepy_path)
except:
    if verbose: print('The varieble LUSEEPY_PATH is undefined, will rely on PYTHONPATH')


luseeopsim_path=''
try:
    luseeopsim_path=os.environ['LUSEEOPSIM_PATH']
    if verbose: print(f'''The LUSEEOPSIM_PATH is defined in the environment: {luseeopsim_path}, will be added to sys.path''')
    sys.path.append(luseeopsim_path)
except:
    if verbose: print('The variable LUSEEOPSIM_PATH is undefined, will rely on PYTHONPATH')
    luseeopsim_path = '../'
    sys.path.append(luseeopsim_path)  # Add parent to path, to enable running locally (also for data)

if verbose: print(sys.path)

try:
    from hardware import *
except:
    if verbose: print("Couldn't load the 'hardware' package, please check the path or the Python environment -- maybe simpy is missing")
    exit(-2)
    
# ---------------------------------------------------------
import  lusee        # Core lusee software
from    nav import * # Astro/observation wrapper classes
from    utils.timeconv import *


import  sim # Main simulation module, which contains the Simulator class
from    sim import Simulator


# -------------------------------------------------------------
config_all  = yaml.safe_load(open(luseeopsim_path+'/config/devices.yml','r'))
config      = config_all['comm']


# Define paths in one place, can overwrite later
orbitals    = luseeopsim_path + "/data/orbitals/20260110-20270116.hdf5" ## changed last digit to 6 as of 6/18/24
modes       = luseeopsim_path + "/config/modes.yml"
devices     = luseeopsim_path + "/config/devices.yml"
comtable    = luseeopsim_path + "/config/comtable-20260110-20270116.yml"

initial_time    = 2
until           = 4600 #2780

smltr = Simulator(orbitals, modes, devices, comtable, initial_time=initial_time, until=until, verbose=verbose)

mjd_start   = smltr.sun.mjd[initial_time]
mjd_end     = smltr.sun.mjd[until]



