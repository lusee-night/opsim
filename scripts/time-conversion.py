#! /usr/bin/env python
#######################################################################
# Simple time conversion, from MJD to datetime and vice versa.
# Using code in the "utils" folder.
#######################################################################

import  argparse
import  datetime
from    astropy.time import Time
from    dateutil     import parser

from    utils.timeconv import *

#######################################
argparser = argparse.ArgumentParser()
argparser.add_argument("-m", "--mjd", type=str, help="Input MJD (e.g. 60725.0)", default='')
argparser.add_argument("-d", "--dt",  type=str, help="Input DateTime (e.g. 2025-02-10 00:00:00)", default='')
#######################################
args    = argparser.parse_args()
mjd     = args.mjd
dt      = args.dt

# ---
if mjd !='':
    print(mjd2dt(mjd))
    exit(0)
# ---
if dt !='':
    print(dt2mjd(dt))
    exit(0)


exit(0)

