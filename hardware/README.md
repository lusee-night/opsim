# Hardware models of LuSEE-Night components

## Battery

Battery is modelled as a storage of charge (Q). Sample configuration:

```
battery:
  initial: 120.0 #in Ah
  capacity: 240.99 #in Ah
  capacity_fade: 0.0063  # capacity faed applied to capacity
  R_internal: 2 # in Ohms, gives ~5% in power loss for a 20W load at 29V
  self_discharge: 0.03 # defined as fractional loss over 28 days
  VOC_table: ../hardware_data/battery/battery_VOC.dat
  # meaning of columns in the look-up table.
  # SOC = State of charge
  # C@T = charge voltage at temperature T
  # D@T = discharge voltage at temperature T
  VOC_table_cols: SOC C@0 D@0 C@20 D@20 C@40 D@40
```

The capacity is initialized using capacity with capacity_fade applied. 

At every time step we first determine if we are charging or discharging by subtracting the total power consumption from the solar panel energy input.

$V_{OC}$ is calculated using an appropriate look-up table for charging or discharging and interpolating in temperature and SOC (calculated as fill/capacity).

If we are charging, we simply increase the charge by $P/V_{OC}\Delta t$, ignoring internal resistance (assuming that its effect is subsumed in the increased voltage wrt to discharging $V_{OC}$). We do not let charge exceed capacity.

If we are discharging, we first need to calculate the current flowing based on the load power $P_L$ and internal resistance.
Some algebra gives
$$
I = \frac{V-\sqrt{V^2-4R_i P_L}}{2R_I}
$$
We then decrease charge by $I \Delta t$. We do not let charge drop below zero.

We then apply battery ageing by multiplying both the current capacity _and_ the current charge by $\exp(-\Delta t/\tau_{SD})$, where $\tau$ is calculated from self_discharge as $\tau_{SD} = -28 \cdot 24 \cdot 3600 s/\log(1-{\rm self\_discharge})$. 


# Solar panels

Each panel is defined by the normal vector in the lander frame, its area and its own efficiency factor (to simulate dead cells, etc). The global parameters is PV efficiency look-up table as a function of temperature, a temperature look-up table and lander yaw/pitch/roll parameters. These have been copied from Ben's table. There are currently some normalization issues.

# SSD

SSD is modelled as a simple storage of bytes. 



