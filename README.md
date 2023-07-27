# LuSEE-Night lander power

## About
Software for calculations related to power generation, management and storage

Comments on TiltedSolar_fullday.ipynb, version from 2023-07-27:

Proceeding through the notebook cells in order for now.

1) Self explanitory, just imports everything we should need for the notebook.

2) def altaz2xyz(alt,az): Function that converts from altitude and azimuth coordinates to Cartesian coordinates, for ease of angle calculations and plotting.
 
3) def PVProjArea(pv_tilt_angle=0, E_area=1, W_area=1, T_area=1, horizon=0.0, lander_pitch=0, lander_roll=0, lander_yaw=0): Function that calculates the projected area of all three photovoltaic (PV) panels, on the top, east, and west faces of LuSEE. Inputs are:
  i) pv_tilt_angle: Specifies the normal angle of the E and W face panels, with respect to horizontal. Positive angles are up. Basically deprecated now, the E&W panels will have pv_tilt_angle=0.
  ii) E_area: Area of the east panel. I used to input areas in m^2, Paul now uses 1 here, and multiplies by the physical area later.
  iii) W_area: Area of the west panel.
  iv) T_area: Area of the top panel.
  v) horizon: cutoff elevation angle for the horizon. Usually zero, but could set higher to account for local geographical features.
  vi) lander_pitch: Rotational angle for lander, angles in degrees. Lander is defined to have "nose" pointing N. Pitch is rotation around E-W axis, + is nose down, - is nose up
  vii) lander_roll: Rotation around N-S axis, + is top rotating left, - is top rotating right
  viii) lander_yaw: Rotation around vertical axis, + is nose right, - is nose left
Function defines normal vectors for each face, rotates by the lander angles, calculates dot product with solar angle (for array of angles across whole lunar cycle, in 15 min increments).
Function then uses condition list to check is sun is completely up, >1/2 up, <1/2 up, or completely down, calculates area of chord above horizon in partially risen cases, and multiplies by fraction of sun area up to account for finite disk of sun.
Function returns arrays of hours from sunrise, and T,E,W areas at each time in hrsFromSunrise.

4) Calculates time indices for key times: iSundown1 (before midnight), iMidnight, iSunrise, iNoon, and iSundown2 (end of lunar day). Makes plots of solar trajectory.

5) Loads and plots Lunar surface temperature data from the Diviner Lunar Radiometer Experiment.

6) def pvEfficiency(T): fits for the PV thermal efficiency as a function of temperature, using Beginning of Life (BOL) specs from SolAero vendor.

7) Plots thermal efficiency data and fit.

8) Calculates and plots solar panel power output throughout one lunar cycle.
   def PVActualPower(t_surface, EPV_area = .313/2, WPV_area = .313/2,TPV_area = .313, \
     solarConstant = 1361, horizon=0, pv_tilt_angle=0, \
     lander_pitch=0, lander_roll=0, lander_yaw=0, \
     dust_obscuration=0, shadowing=0, EOL_degradation=0): Function to calculate power in Watts. Variables are:
     i) t_surface: array of surface temps in 15 min increments for lunar cycle
     ii) EPV_area: Area of E PV panel in m^2
     iii) WPV_area: Area of W PV panel in m^2
     iv) TPV_area: Area of top PV panel in m^2
     v) solarConstant: Radiated power of sun, in W/m^2
     vi)-x) As defined for PVProjArea() above
     xi) dust_obscuration: Fractional decrement in panel power from dust. We usually use 5% as a conservative estimate.
     xii) shadowing: Fractional decrement in panel power from shadows of antennas, deployers, etc. on top face. I had a whole complex section to calculate this as a function of time for a simplified physical geometry of the antennas and deployers, but with the current layout shadows are minimized. This could be implemented approximately with an array: 10% for 25 hours after sunrise and before sunset, then falling sharply to 0% for the rest of the day.
     xiii) EOL_degradation: End of Life degredation factor, including radiation etc. 5% is approximately correct from SolAero specs.
Function returns arrays of power for TPV, EPV, WPV, in 15 minute increments.

9) Daytime and Nighttime power load parameters
    
10) Calculating battery State of Charge (SOC) and plotting

11) Better lunar temp and thermal efficiency plot
