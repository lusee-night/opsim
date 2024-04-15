#! /usr/bin/env python
#######################################################################
# The script for the basic unit test of the battery
#######################################################################
import os, sys
import yaml
import argparse


reference_data = [
    862098.347, 858008.045, 6359.889,
    858008.045, 853933.887, 6365.000,
    862098.347, 858011.289, 6354.833,
    858011.289, 853940.272, 6360.056,
    862098.347, 858013.428, 6351.500,
    858013.428, 853944.529, 6356.722
]


# ---
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-r", "--reference",    action='store_true', help="Print reference data and exit")

parser.add_argument("-i", "--initial",      type=float, default='0.95', help="Initial battery level")
parser.add_argument("-t", "--threshold",    type=float, default='0.05', help="SOC threshold")

args        = parser.parse_args()

verbose     = args.verbose
reference   = args.reference

if reference:
    print(reference_data)
    exit(0)

initial     = args.initial
threshold   = args.threshold


luseepy_path    = None
luseeopsim_path = None

result          = []

try:
    luseepy_path=os.environ['LUSEEPY_PATH']
    if verbose: print(f'''The LUSEEPY_PATH is defined in the environment: {luseepy_path}, will be added to sys.path''')
    sys.path.append(luseepy_path)
except:
    if verbose: print('The varieble LUSEEPY_PATH is undefined, will rely on PYTHONPATH')

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
    if verbose: print("Couldn't locate the 'hardware' package, please check the environment")
    exit(-2)


config_all  = yaml.safe_load(open(luseeopsim_path+'/config/devices.yml','r'))
config      = config_all['battery']

init_level = None # To save for the second test run

power   = 20
deltaT  = 10

for T in [0, 20, 40]:
    run = 0
    B = Battery(config, verbose=verbose)
    B.level = B.capacity*initial
    if init_level is None: init_level = B.level

    if not B.OK:
        print('Battery not OK, errors reported:')
        for message in B.errors:
            print(message)
        exit(-1)
    B.set_temperature(T)
    energy = 0
    init_capacity = B.capacity
    while B.SOC() > threshold:
        B.apply_power(-power, deltaT)
        B.apply_age(deltaT) 
        energy += deltaT*power # energy drawn from the battery

    final_capacity = B.capacity
    if verbose: print (f'''Run {run}: temperature {T:2}C, init capacity {init_capacity:10.3f}, final capacity {final_capacity:10.3f}, total energy {(energy/3600):8.3f}Wh''')

    result.extend([init_capacity, final_capacity, energy/3600])


    # Recharge the battery and do over
    run = 1
    B.level = init_level
    energy = 0
    init_capacity = B.capacity # account for age -- inherit from the previous run

    while B.SOC() > threshold:
        B.apply_power(-power, deltaT)
        B.apply_age(deltaT)        
        energy += deltaT*power # energy drawn from the battery

    final_capacity = B.capacity
    if verbose: print (f'''Run {run}: temperature {T:2}C, init capacity {init_capacity:10.3f}, final capacity {final_capacity:10.3f}, total energy {(energy/3600):8.3f}Wh''')

    result.extend([init_capacity, final_capacity, energy/3600])


N1 = len(reference_data)
N2 = len(result)

if N1!=N2:
    if verbose: print(f'''Mismatch between reference data and result, N1={N1}, N2={N2}''')
    exit(-3)


for i in range(N1):
    # print(result[i], reference_data[i])
    if (abs(result[i] - reference_data[i])/reference_data[i])>0.001:
        if verbose: print('Mismatch between reference data and result')
        exit(-3)

if verbose: print('Success!')

exit(0)
