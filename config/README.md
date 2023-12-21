# OpSim Configuration Data

## Purpose

To facilitate running of the OpSim machinery, this folder contains configuration
data to modify the behavior of the software without having to modofy the source.

## Devices

Power profile of the devices.

## Files

* `comtable` : the _command table_, essentially a schedule of state transitions
* `modes` : definition of modes of operation of the components
* `conf` : configuration for prepped data production (cache)
* `devices` : states and power draw


## MJD to datetime, and back: conversion

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

