#! /usr/bin/env python
#######################################################################
# The script for the unit test of the simulator
#######################################################################

import os, sys
import argparse


# With pv_angle_corr() power correction
reference_data = [
    0.0, 105.36868297988804, 72.54664051464663, 0.0, 0.0, 
    103.82236471639506, 0.0, 0.0, 77.8140578786585, 105.99853263239054
]

# Without pv_angle_corr() power correction
#reference_data = [
#    0.0, 95.49671147101515, 67.72649421694697, 0.0, 0.0,
#    93.43520726609137, 0.0, 0.0, 73.42301727632977, 96.2092542051847
#]

profile_yaml="""
initial: 120.0 #in Ah
capacity: 240.99 #in Ah
capacity_fade: 0.0063  # capacity fade applied to capacity
self_discharge: 0.01 # defined as fractional loss over 28 days
VOC_table: ../data/hardware/battery/battery_VOC.dat
# meaning of columns in the look-up table.
# SOC = State of charge
# VOC@T = open circuit voltage at temperature T
# R@T = internal resistance at temperature T
VOC_table_cols: SOC VOC@0 R@0 VOC@20 R@20 VOC@40 R@40
"""

##############################################
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", action='store_true', help="Verbose mode")
args    = parser.parse_args()

verbose = args.verbose


# ---
try:
    luseepy_path=os.environ['LUSEEPY_PATH']
    if verbose: print(f'''The LUSEEPY_PATH is defined in the environment: {luseepy_path}, will be added to sys.path''')
    sys.path.append(luseepy_path)
except:
    if verbose: print('The varieble LUSEEPY_PATH is undefined, will rely on PYTHONPATH')

# ---
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

from   hardware        import *


# ---------------------------------------------------------
import  lusee        # Core lusee software
from    nav import * # Astro/observation wrapper classes
from    utils.timeconv import *


import  sim # Main simulation module, which contains the Simulator class
from    sim import Simulator


# -------------------------------------------------------------
# Define paths in one place, can overwrite later
orbitals    = luseeopsim_path + "/data/orbitals/20260110-20270115.hdf5"
modes       = luseeopsim_path + "/config/modes.yml"
devices     = luseeopsim_path + "/config/devices.yml"
comtable    = luseeopsim_path + "/config/comtable-20260110-20270115.yml"

initial_time    = 2
until           = 4600 #2780

smltr = Simulator(orbitals, modes, devices, comtable, initial_time=initial_time, until=until, verbose=verbose)

mjd_start   = smltr.sun.mjd[initial_time]
mjd_end     = smltr.sun.mjd[until]


if verbose:
    print(f'''Initial time in ticks: {initial_time}, mjd: {mjd_start}, datetime: {mjd2dt(mjd_start)}, Sun Alt: {smltr.sun.alt[initial_time]}''')
    print(f'''Until time in ticks: {until}, mjd: {mjd_end}, datetime: {mjd2dt(mjd_end)}''')
    smltr.power_info()


smltr.verbose = False # True
smltr.simulate()

pwr = smltr.controller.power
N = pwr.shape[0]

# Checkpoints

step = int(N/10)

if verbose: print('The samples of the power curve are:')

for i in range(10):
    n = i*step
    result = pwr[n]
    if verbose: print(f'''{result:6.3f}''')
    if (abs(result - reference_data[i])>0.00001):
        if verbose: print('Mismatch between reference data and result')
        exit(-3)

if verbose: print('Success!')

exit(0)