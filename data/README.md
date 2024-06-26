# Sample Data

## HDF5

Contains metadata, and the data payload, written together in the HDF5 format. The _groups_
in the HDF5 files are names correspondingly:
* __meta__: contains the _configuration_ dataset
* __data__: contains the _orbitals_ dataset

The _/meta/configuration_ contains the metadata supplied in the YAML format, such as:
```
period:
  start: "2026-01-10 20:00:00" # "2025-02-10 00:00:00"
  end:   "2027-01-15 02:00:00" # "2025-02-11 23:45:00"
  deltaT: 900

location:
    latitude:                     -23.814 # degrees
    longitude:                    182.258 # degrees
    height:                       0 # meters

satellites:
  lpf:
    semi_major_km:                5738
    eccentricity:                 0.56489
    inclination_deg:              57.097
    raan_deg:                     0
    argument_of_pericenter_deg:   72.625
    aposelene_ref_time:           '2024-05-01T00:00:00'

  bge:
    semi_major_km:                5738
    eccentricity:                 0.56489
    inclination_deg:              57.097
    raan_deg:                     0
    argument_of_pericenter_deg:   252.625
    aposelene_ref_time:           '2024-05-01T00:00:00'
```


## Archive

The __archive__ folder contains data that is kept for reference, not actively used past the end
of 2023, after the switch to the HDF5 format. An example of these archived files
would be prefabricated data containg tupples _(mjd,alt,az)_:

* `2025-02-10_20.npy` covers the range of MJD: 2025-02-10 00:00:00 to 2025-02-20 03:45:00
* `2025-02-04_03-07.npy` covers the range of MJD: 2025-02-04 00:00:00 to 2025-03-07 03:45:00
