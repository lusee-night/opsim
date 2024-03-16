#! /usr/bin/env python
#######################################################################
# The script for basic unit test of the battery
#######################################################################

import yaml
from   hardware        import *

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

print("Testing the battery", profile_yaml)

battery_config = yaml.safe_load(profile_yaml)
print(battery_config)
Battery(battery_config)
