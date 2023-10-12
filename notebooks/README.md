# Notebooks

## What's in here

### lusee-test

* calculates the Sun trajectory at runtime, using the wrapped
`Observation` object from `luseepy`, presented in the utility class `Sun`
* can also read prefabricated data, for comparison
* diagnostic printout and graphing of various navigation-related quantities

### sim

Runs the Operations Sim, utilizing `SimPy`

## PYTHONPATH

When running in _VS code_, the environment will be inherited from the shell,
which is helpful since you can conveninetly set `PYTHONPATH` before starting
the session.
