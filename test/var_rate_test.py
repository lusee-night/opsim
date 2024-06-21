#! /usr/bin/env python
#######################################################################
# The script for the unit test of the variable data transfer rate
#######################################################################


import os, sys
import argparse
import yaml

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

verbose = True
# -------------------------------------------------------------
config_all  = yaml.safe_load(open(luseeopsim_path+'/config/devices.yml','r'))
config      = config_all['comm']


# Define paths in one place, can overwrite later
orbitals    = luseeopsim_path + "/data/orbitals/20260110-20270116.hdf5" ## changed last digit to 6 as of 6/18/24
modes       = luseeopsim_path + "/config/modes.yml"
devices     = luseeopsim_path + "/config/devices.yml"


initial_time    = 2
until           = 4600 #2780


dist_list = [4895.234953916798,6882.4730522543205,5699.930535431102 ,8470.252878855066,5941.4932481588685]
rate_list = [84.79115045361613,84.79115045361613,169.58230090723225,42.39557522680806,169.58230090723225]
alt_list = [8.956959463274808,15.720257630499098,19.58657489665725 , 10.126332012054354, 37.24451294801958]
time_step = [386 ,478 ,475 ,573,1300]

## Test different configs
config['adaptable_rate'] = True
config['if_adaptable'] = {
    'max_rate_kbps': 1024,
    'link_margin_dB': 3}

config['if_fixed'] = {
    'fixed_rate': -20.0}

comm = Comm(max_rate_kbps=config['if_adaptable']['max_rate_kbps'], link_margin_dB=config['if_adaptable']['link_margin_dB'],
            fixed_rate=config['if_fixed']['fixed_rate'])


for i in range(len(dist_list)):
    dr = 0.0
    if not comm.adaptable_rate: 
        dr += comm.fixed_rate
        if verbose:
            print('Constant data rate:',dr,'kbps')
    else:                     
        zero_ext_gain = False
        if verbose:
            if (comm.max_rate_kbps != 1024) or (comm.link_margin_dB != 3):
                print('Max rate kbps or link margin are not default values')
        
        adapt_rate, demo,pw = comm.get_rate(distance_km=dist_list[i],alt_deg = alt_list[i],max_rate_kbps= comm.max_rate_kbps, demod_marg= 
                                            comm.link_margin_dB, zero_ext_gain=False)
        dr += adapt_rate 
        if verbose:
            print(f'''Initial time in ticks: {time_step[i]}, distance in km: {dist_list[i]}, calculated rate in kbps: {dr}, ideal rate: {rate_list[i]}''')
        if adapt_rate != rate_list[i]:
            print('Error: Rates not equal (Adaptable)')
            exit(-3)

