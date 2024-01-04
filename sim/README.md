# Simulator

The main simulator class in _OpSim_. Content:

1. _orbitals_: tuples of _(alt,az)_ for the Sun and the two satellites, read from an external ("prefabricated") file in __HDF5__ format.
2. _modes_: the LuSEE modes definition
3. _comtable_: the __command table__, i.e. a schedule to switch modes
4. Misc. devices: battery, controller
5. The _simpy_ "Environment" in which to run the simulation
