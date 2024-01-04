from    astropy.time import Time
from    dateutil     import parser

# ---
def mjd2dt(mjd):
    t = Time(val=mjd,format='mjd')
    return t.datetime

# ---
def dt2mjd(dt):
    t = Time(val=parser.parse(dt),  format='datetime')
    return t.mjd