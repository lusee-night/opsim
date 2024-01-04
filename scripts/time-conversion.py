#! /usr/bin/env python
#######################################################################
# Simple time conversion
#######################################################################

import  datetime
from    astropy.time import Time
from    dateutil     import parser

t = Time(val=60725,format='mjd')
print(t.datetime)
# datetime.datetime(2025, 2, 19, 0, 0)


t = datetime.datetime(2025, 2, 19, 0, 0)
b = Time(val=t, format='datetime')
print(b.mjd)
