# Notebooks

## newsim

The most up-to-date version of the simulation notebook. It is using the following elements
of the data:

a) Prefabricated _orbitals_ i.e. positions of the Sun and the satellites, calculated as
time series
b) _devices_: list of devices, with requisite numbers of the current drawn from the power source, for each of the available states
c) _modes_: major modes of the LuSEE apparatus, mapped onto the states of each hardware component
d) _comtable_: the command table to be executed

## PYTHONPATH

When running in _VS code_, the environment will be inherited from the shell,
which is helpful since you can conveninetly set `PYTHONPATH` before starting
the session.



## Archive

### lusee-test

* calculates the Sun trajectory at runtime, using the wrapped
`Observation` object from `luseepy`, presented in the utility class `Sun`
* can also read prefabricated data, for comparison
* diagnostic printout and graphing of various navigation-related quantities
* _note_: largely superseeded

### sim

The original version of the simulation notebook, utilizing `SimPy`; _note_: largely superseeded.