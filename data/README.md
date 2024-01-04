# Sample Data

## HDF5

Contains metadata, and the data payload, written together in teh HDF5 format. The _groups_
in the HDF5 files are names correspondingly:
* __meta__: contains the _configuration_ dataset
* __data__: contains the _orbitals_ dataset


## Archive

Kept for reference, not actively used past the end of 2023, after the switch to the HDF5 format.
Small files to be used as inputs, to facilitate testing. Prefab _(mjd,alt,az)_ data:

* `2025-02-10_20.npy` covers the range of MJD: 2025-02-10 00:00:00 to 2025-02-20 03:45:00
* `2025-02-04_03-07.npy` covers the range of MJD: 2025-02-04 00:00:00 to 2025-03-07 03:45:00
