# OpSim Configuration Data

## Purpose

There are several types of configuration data: one for use in pre-calculations of the "orbitals",
and others, to define the behavior of the simulated LuSEE operation.

## Files

* `comtable` : the _command table_, essentially a schedule of LuSEE modes (and transitions)
* `modes` : a map of LuSEE modes to the states of the components
* `conf` : configuration for prepped data production e.g. the _orbitals_ (stored in a cache file)
* `devices` : enumerates and maps the device states and power draw


## Notes on time conversion -- MJD to datetime, and back

```python
from astropy.time import Time
t = Time(val=60725,format='mjd')
t.datetime
datetime.datetime(2025, 2, 19, 0, 0)


import datetime
t = datetime.datetime(2025, 2, 19, 0, 0)
b = Time(val=t, format='datetime')
b.mjd
```

