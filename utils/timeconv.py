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
# ---
def pretty(d, indent=0, retstring=""):
    for key, value in d.items():
        retstring+='\t' * indent + str(key) + '\n'
        if isinstance(value, dict):
            retstring+=pretty(d=value, indent=indent+1)
        else:
            retstring+='\t' * (indent+1) + str(value) + '\n'

    return retstring
