#! /usr/bin/env python
#######################################################################
# The script for the basic unit test of the battery
#######################################################################

import yaml
import argparse
from   hardware        import *


parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose mode")
parser.add_argument("-i", "--initial",      type=float, default='0.95', help="Initial battery level")
parser.add_argument("-t", "--threshold",    type=float, default='0.05', help="SOC threshold")

args        = parser.parse_args()
verbose     = args.verbose
initial     = args.initial
threshold   = args.threshold

config_all  = yaml.safe_load(open('../config/devices.yml','r'))
config      = config_all['battery']


init_level = config['capacity']*initial
config['initial'] = init_level
# if verbose: print(config)

power   = 20
deltaT  = 10


for T in [0, 20, 40]:
    run = 0
    B = Battery(config, verbose=False)
    B.set_temperature(T)
    energy = 0

    init_capacity = B.capacity
    while B.SOC() > threshold:
        # print(B.SOC())
        B.apply_power(-power, deltaT)
        B.apply_age(deltaT) 
        energy += deltaT*power # energy drawn from the battery

    final_capacity = B.capacity
    print (f'''Run {run}: temperature {T:2}C, init capacity {init_capacity:10.3f}, final capacity {final_capacity:10.3f}, total energy {(energy/3600):9.4f}Wh''')

    run = 1
    # Recharge the battery and do over
    B.level = init_level*3600
    init_capacity = B.capacity # account for age

    while B.SOC() > threshold:
        B.apply_power(-power, deltaT)
        B.apply_age(deltaT)        
        energy += deltaT*power # energy drawn from the battery

    final_capacity = B.capacity
    print (f'''Run {run}: temperature {T:2}C, init capacity {init_capacity:10.3f}, final capacity {final_capacity:10.3f}, total energy {(energy/3600):9.4f}Wh''')    