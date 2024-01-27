# Hardware models of LuSEE-Night components

## Battery

Battery is modelled as a storage of charge (Q). The following parameters are recognized:
 * `initial` - initial capacity in Wh
 * `capacity` - total capacity in Wh. This capacity should already include any margin factors wrt to the nameplate capacity.
 * `fiducial_voltage` - voltage in Volts used to convert capacities into charges 
 * `charge_efficiency` - efficiency factor when charging
 * `discharge_efficiency` - efficiency factor when discharging

Inital and capacity charges in Ah are calculated from `initial` and `capacity` values using `fiducial_voltage`. 

The fill-level $f$ is calculated by dividing the current charge with the capacity charge. The terminal voltage is determined from a look up table and is a function of fill-level $f$ and temperature T:
$$
V = V(f,T)
$$
(at the moment assumed to be always pinned to fiducial_voltage).
At every time step, we put charge into the battery and take-it out based on this voltage
$$
\Delta Q = \left(+\frac{P_{\rm panels} \epsilon_c }{V(f,T)} - \frac{P_{\rm cons}}{V(f,T) \epsilon_d}\right)\Delta t,
$$
where $\epsilon_c$ and $\epsilon_d$ are charge and discharge efficiencies.  Note that one comes on top and the other comes on the bottom, i.e. they always make things worse when less than unity.

Note that in this scenario, it voltage is a strong function of temperature, it makes sense to charge batter when voltage is low and discharge it when it is high, in effect getting energy "for free" (in reality the battery thermodynamics acting as a heat engine).

# Solar panels

Each panel is defined by the normal vector in the lander frame, its area and its own efficiency factor (to simulate dead cells, etc). The global parameters is PV efficiency look-up table as a function of temperature, a temperature look-up table and lander yaw/pitch/roll parameters. These have been copied from Ben's table. There are currently some normalization issues.

# SSD

SSD is modelled as a simple storage of bytes. 



