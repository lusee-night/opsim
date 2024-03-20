#! /usr/bin/env python
#######################################################################
# The script for the unit test of the simulator
#######################################################################

import yaml
import argparse
from   hardware        import *


# ---------------------------------------------------------
import  lusee        # Core lusee software
from    nav import * # Astro/observation wrapper classes
from    utils.timeconv import *


import  sim # Main simulation module, which contains the Simulator class
from    sim import Simulator

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


# Define paths in one place, can overwrite later
orbitals    = "../data/orbitals/20260110-20270115.hdf5"
modes       = "../config/modes.yml"
devices     = "../config/devices.yml"
comtable    = "../config/comtable-20260110-20270115.yml"

##############################################
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", action='store_true', help="Verbose mode")
args    = parser.parse_args()

verbose = args.verbose

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
