# Notebooks

## Newsim

The most up-to-date version of the simulation notebook. It is using the following elements
of the data:

* Prefabricated _orbitals_ i.e. positions of the Sun and the satellites, calculated as
time series
* _devices_: list of devices, with requisite numbers of the current drawn from the power source, for each of the available states
* _modes_: major modes of the LuSEE apparatus, mapped onto the states of each hardware component
* _comtable_: the command table to be executed

## Datacheck

A simple tool to validate inputs to the simulator, inclusing the _HDF5_-formatted data
and configuration files (in _YAML)

---


# Settings

## PYTHONPATH

When running in _VS code_, the environment will be inherited from the shell,
which is helpful since you can conveninetly set `PYTHONPATH` before starting
the session. This software depends on the _luseepy_ package and the _simpy_
framework to function. This is typically provided by the Python virtual environment.


## Archive

### lusee-test

* calculates the Sun trajectory at runtime, using the wrapped
`Observation` object from `luseepy`, presented in the utility class `Sun`
* can also read prefabricated data, for comparison
* diagnostic printout and graphing of various navigation-related quantities
* _note_: largely superseeded

### sim

The original version of the simulation notebook, utilizing `SimPy`; _note_: largely superseeded.