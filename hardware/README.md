# Hardware models of LuSEE-Night components

## Battery

Battery is modelled as a storage of charge (Q). We have a model for open circuit voltage and internal resistance as a function of temperature. These are derived from V_load and V_charge under 20W discharging and charging voltages as given by the vendor model (which is not directly accessible to us).  This is processed thrugh the `script/process_battery_data.py` script.
 
```
battery:
  initial: 120.0 #in Ah
  capacity: 240.99 #in Ah
  capacity_fade: 0.0063  # capacity fade applied to capacity
  self_discharge: 0.01 # defined as fractional loss over 28 days
  VOC_table: ../data/hardware/battery/battery_VOC.dat
  # meaning of columns in the look-up table.
  # SOC = State of charge
  # VOC@T = open circuit voltage at temperature T
  # R@T = internal resistance at temperature T
  VOC_table_cols: SOC VOC@0 R@0 VOC@20 R@20 VOC@40 R@40
```

When discharging, we solve for the current drawn so that power across $V_{OC}-R I$ equals the requested power.
$$
I = \frac{V-\sqrt{V^2-4R_i P_L}}{2R_I}
$$
When we charge we require that power across $V_{OC}+RI$ equals the charging power giving
$$
I = \frac{-V+\sqrt{V^2+4R_i P_L}}{2R_I}
$$
In both cases the change in stored charge equals $I \Delta t$.

We then apply battery ageing by multiplying both the current capacity _and_ the current charge by $\exp(-\Delta t/\tau_{SD})$, where $\tau$ is calculated from self_discharge as $\tau_{SD} = -28 \cdot 24 \cdot 3600 s/\log(1-{\rm self\_discharge})$. 

We do not let charge drop below zero.



# Solar panels

Each panel is defined by the normal vector in the lander frame, its area and its own efficiency factor (to simulate dead cells, etc). The global parameters is PV efficiency look-up table as a function of temperature, a temperature look-up table and lander yaw/pitch/roll parameters. These have been copied from Ben's table. There are currently some normalization issues.

# SSD

SSD is modelled as a simple storage of bytes. 



