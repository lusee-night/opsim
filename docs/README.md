# The prototype notebook for power calculation

Comments on the original __TiltedSolar_fullday.ipynb__ (in the `notebooks` repo), version from 2023-07-27.
Proceeding through the notebook cells in order for now.

1) Self explanitory, just imports everything we should need for the notebook.
2) `def altaz2xyz(alt,az)`: Function that converts from altitude and azimuth coordinates to Cartesian coordinates, for ease of angle calculations and plotting.
3) `def PVProjArea(pv_tilt_angle=0, E_area=1, W_area=1, T_area=1, horizon=0.0, lander_pitch=0, lander_roll=0, lander_yaw=0)`: function that calculates the projected area of all three photovoltaic (PV) panels, on the top, east, and west faces of LuSEE. Inputs are:
    1) `pv_tilt_angle``: Specifies the normal angle of the E and W face panels, with respect to horizontal. Positive angles are up. Basically deprecated now, the E&W panels will have pv_tilt_angle=0.
    2) `E_area`: Area of the east panel. I used to input areas in m^2, Paul now uses 1 here, and multiplies by the physical area later.
    3) `W_area`: Area of the west panel.
    4) `T_area``: Area of the top panel.
    5) `horizon``: cutoff elevation angle for the horizon. Usually zero, but could set higher to account for local geographical features.
    6) `lander_pitch`: Rotational angle for lander, angles in degrees. Lander is defined to have "nose" pointing N. Pitch is rotation around E-W axis, + is nose down, - is nose up
    7) `lander_roll`: Rotation around N-S axis, + is top rotating left, - is top rotating right
    8) `lander_yaw`: Rotation around vertical axis, + is nose right, - is nose left

Function defines normal vectors for each face, rotates by the lander angles, calculates dot product with solar angle (for array of angles across whole lunar cycle, in 15 min increments).

Function then uses condition list to check is sun is completely up, >1/2 up, <1/2 up, or completely down, calculates area of chord above horizon in partially risen cases, and multiplies by fraction of sun area up to account for finite disk of sun.
Function returns arrays of hours from sunrise, and T,E,W areas at each time in hrsFromSunrise.

4) Calculates time indices for key times: iSundown1 (before midnight), iMidnight, iSunrise, iNoon, and iSundown2 (end of lunar day). Makes plots of solar trajectory.

5) Loads and plots Lunar surface temperature data from the Diviner Lunar Radiometer Experiment.

6) def pvEfficiency(T): fits for the PV thermal efficiency as a function of temperature, using Beginning of Life (BOL) specs from SolAero vendor.

7) Plots thermal efficiency data and fit.

8) Calculates and plots solar panel power output throughout one lunar cycle. Function to calculate power in Watts. Variables are
described below the code block:

        def PVActualPower(t_surface, EPV_area = .313/2, WPV_area = .313/2,TPV_area = .313,
           solarConstant = 1361, horizon=0, pv_tilt_angle=0,
           lander_pitch=0, lander_roll=0, lander_yaw=0,
           dust_obscuration=0, shadowing=0, EOL_degradation=0)

    1) `t_surface`: array of surface temps in 15 min increments for lunar cycle
    2) `EPV_area`: Area of E PV panel in m^2
    3) `WPV_area`: Area of W PV panel in m^2
    4) TPV_area: Area of top PV panel in m^2
    5) solarConstant: Radiated power of sun, in W/m^2
    6) through 10 as defined for PVProjArea() above
    7) -
    8) -
    9) -
    10) -
    11) dust_obscuration: Fractional decrement in panel power from dust. We usually use 5% as a conservative estimate.
    12) shadowing: Fractional decrement in panel power from shadows of antennas, deployers, etc. on top face. I had a whole complex section to calculate this as a function of time for a simplified physical geometry of the antennas and deployers, but with the current layout shadows are minimized. This could be implemented approximately with an array: 10% for 25 hours after sunrise and before sunset, then falling sharply to 0% for the rest of the day.
     13) EOL_degradation: End of Life degredation factor, including radiation etc. 5% is approximately correct from SolAero specs.

Function returns arrays of power for TPV, EPV, WPV, in 15 minute increments.

9) Daytime and Nighttime power load parameters.
    
    1) PPT: Peak Power Tracker, manages solar panels
    2) PDU: Power Distribution Unit, distributes power from solar panels and battery to other components
    iii) PFPS: Picket Fence Power Supply, power supply with precise switching to limit RFI to "picket fence" in freq space
    iv) CDH: Renamed DCB, Digital Control Board, controls onboard operations
    v) SPT: Spectrometer
    vi) Preamp: Science antenna preamplifiers
    vii) RF RX/TX: Communications receiver and transmitter modules
    viii) Charging/Discharging Efficiency: estimate of power lost to inefficiencies in battery and Ohmic heating. Modeling should be expanded.
    ix) Uncertainty Margin: Uncertainty factor for total power load, since all components have not been assembled and tested their loads are not precisely known.
    
10) Calculating battery State of Charge (SOC) and plotting.
    Using the power loads from 9), and the power output profile from 8), calculates the State of Charge (SOC) of the battery, and plotts results.
    
    1) PPT_threshold: PPT only active when input power estimated to be greater than net draw from PPT and other nighttime instrumentation.
    
    ii) radio_threshold: RF RX/TX systems only active when net power greater than total daytime power draw.
    
    iii)nameplateCapacity: Nominal capacity of battery
    
    iv) maxCharge: Specified maximum battery charge, from vendor
    
    v) maxDoD: Maximum Depth of Discharge (minimum safe charge), specified by vendor. N.B. NASA requirement may be significantly higher than vendor spec! NASA recommends 40% min safe SOC, possibly grants waivers for lower operation.
   
11) Better lunar temp and thermal efficiency plot.
    Should be incorporated with previous lunar temp plot cell.
