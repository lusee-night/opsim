# OpSim: Simulation of the LuSEE-Night Operations Logic

## About
Software for calculations related to operation control for LuSEE-Night, such power
generation and management, data taking (science), comms etc.

__Glossary__

* _modes_: reference to the modes of the LuSEE-Night apparatus' operations, this choice is in order to conform with the convention in the "ConOps" document
  * science
  * main
  * powersave
* _states_: states of the devices as stipulated by the specific LuSEE _mode_.

__Devices Included in the simulation__

* _UT_ -- Comm module
* _PDU_ -- Power distribution
* _PCDU_ -- The battery management circuit
* _PFPS_ -- PFPS picket fance power supply
* _DCB_ -- Flight computer


## Folders in this repository

### Configuration and data

1. _config_: configuration data, typically formatted in YAML
2. _data_: pre-calculated data to be fed to the simulator. The current format is HDF5 and a few older files in the _numpy_ format are kept for reference only.

Please see the `README` file in the _config_ folder for more detail on how these pieces
of configuration relate to each other.

### "Scripts"

1. _scripts_: an assembly of scripts, such as used in preparation of the
"prefabricated" data on the position of celestial objects, to be later used
in the simulation. The important one is `prep-all`


### Core software

1. _notebooks_: an assembly of notebooks to diagnose the data and run the simulation
2. _nav_ contains utility accessor methods to interface
various coordinate calculations
3. _hardware_: classes describing various elements of the LuSEE hardware
4. _sim_: the main simulator class


### Archival/reference folders

1. The `docs` folder is reserved for the future documentation website materials (if needed)
2. In the `reference` folder there is a "sandbox" version of the original power
calculation notebook (heavily modified and not to be used for anything practical)
and some requisite inputs. Kept for continuity with the power calculation notebook.


## Misc


### Dependencies

This software depends of the _luseepy_ suite, plus the `simpy` package. This is typically handled
by setting up an appropriate Python virtual environment. The _hdf5_ interface is provided via the `h5py`
Python package, which happens to be already in _luseepy_ so no separate installation is required.

### lzma

In some Debian instances, the `lzma` Python package is missing, while it's needed for a
few dependencies to work. One way to fix that is to do the `backport`` package
installation in a virtual environment, and then define the path for it to be referenced,
as shown in the following example:

```bash
export PYTHONPATH=/home/maxim/projects/lusee/luseepy:/home/maxim/projects/lusee/opsim:/home/maxim/.virtualenvs/lusee/lib/python3.10/site-packages/backports
```

### MJD

The MJD gives the number of days since midnight on November 17, 1858. This date corresponds
to 2400000.5 days after day 0 of the Julian calendar. MJD is still in common usage in
tabulations by the U. S. Naval Observatory. Care is needed in converting to other
time units, however, as a result of the half day offset (unlike the Julian date,
the modified Julian date is referenced to midnight instead of noon) and because
of the insertion of semiannual leap seconds (which are inserted at midnight).

