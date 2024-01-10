# Utility scripts for the "OpSim" project

## Current scripts

* `prep-sun` -- pre-calculation of the Sun's trajectory in the sky, to facilitate power and other calculations; saved to a cache file in HDF5 format. For details of the format, please see the README file in the _data_ folder.
* `time-conversion` -- a simple CLI utility to convert between a few popular time formats, useful for data inspection.


## Deferred/Deprected (moved to "attic")

* `prep-sun` -- kept for future development, if more time series need to be added to the cache
* `prep-power` -- pre-calculation of the power output of the solar panels; functionality moved elsewhere
* `prep-validation` -- data checker (for the deprecated format)