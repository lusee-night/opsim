
#
# This code converts 'SOC vs EMF Summary_2023.11.15.xlsx' to
# and equivalent VOC and internal resistance as a function of temperature
# and SOC.
#

import os, sys
import numpy as np


header = """Battery data exported from 'SOC vs EMF Summary_2023.11.15.xlsx'  
into battery_VLoad.dat and from there to here using script/process_battery_data.py script
Columns are:
 1 - SOC in percent
 2,3 open circuit Voltage [Volts], R_internal [Ohms] at 0 degree C
 4,5 open circuit Voltage [Volts], R_internal [Ohms] at 20 degree C
 6,7 open circuit Voltage [Volts], R_internal [Ohms] at 40 degree C"""

def VLoad2VOC(V_charge, V_load, P_charge = 20, P_load = 20):
    """
    Converts load voltages in open circuit voltage + resistance

    On the charge side, we have
    VC-RI*I = VOC
    VC*I = PC

    On the load side, we have
    VL+ RI*I = VOC
    VL*I = PL

    Solving for VOC and R, we get

    RI = VL*VC*(VC-VL)/(PC*VL+PL*VC)
    VOC = (PC*VL**2+PL*VC**2)/(PC*VL+PL*VC)

    Charge and load power are assumed to be 20W as per POC email on 1/30/24
    """

    R = V_load*V_charge*(V_charge-V_load)/(P_charge*V_load+P_load*V_charge)
    VOC = (P_charge*V_load**2+P_load*V_charge**2)/(P_charge*V_load+P_load*V_charge)

    ## sanity check 
    I = P_load/V_load
    assert np.allclose(V_load+R*I, VOC)

    return VOC, R


def main():
    fname_in = 'data/hardware/battery/battery_VLoad.dat'
    fname_out = 'data/hardware/battery/battery_VOC.dat'
    print ("Loading data from %s" % fname_in)
    data = np.loadtxt(fname_in, skiprows=6)
    SOC = data[:,0]
    for col in [1,3,5]:
        V_charge = data[:,col]
        V_load = data[:,col+1]
        VOC, R = VLoad2VOC(V_charge, V_load)
        data[:,col] = VOC
        data[:,col+1] = R
    print ("Saving data to %s" % fname_out)
    np.savetxt(fname_out, data, header=header)



if __name__=="__main__":
    main()
