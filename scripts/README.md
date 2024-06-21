# Utility scripts for the "OpSim" project

## Current scripts

* `prep-all` -- pre-calculation of the Sun's and the satellites trajectoris in the sky,
to facilitate power and other calculations; saved to a cache file in HDF5 format.
For details of the format, please see the README file in the _data_ folder.
* `time-conversion` -- a simple CLI utility to convert between a few popular time formats, useful for data inspection.

## Configuration


## Deferred/Deprected (moved to "attic")

* `prep-sun` -- kept for future development, if more time series need to be added to the cache
* `prep-power` -- pre-calculation of the power output of the solar panels; functionality moved elsewhere
* `prep-validation` -- data checker (for the deprecated format)

## "Parse CSV"

```bash
#
# An example of parsing and conversion of the vendor data on the satellite trajectory
./scripts/parse-csv.py -v  -i ~/sat.csv -o foo.hdf5 -f18,19,20
#
# Same, with the optional time window
./scripts/parse-csv.py  -i ~/sat.csv -s 61050.0 -e 61071.0 -v -o ~/new.hdf5 -f18,19,20
```

The helper script `time-conversion` can be useful for translating the date/time info from
string format into the MJD units.
