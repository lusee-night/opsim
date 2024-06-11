import lusee
#from lusee.observation import LObservation ## MR --will have to figure out where these packages are
#from lusee.lunar_satellite import LSatellite, ObservedSatellite ## MR --will have to figure out where these packages are, but the code doesn't run when these are up
import numpy as np
#import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import time
import pickle

# MR -- copied the functions below from previously defined transfer_rate.ipynb from notebooks_git

class Comm():
    def __init__(self, adaptable_rate, max_rate_kbps=None, link_margin_dB=None, fixed_rate=None):
        self.adaptable_rate = adaptable_rate
        if adaptable_rate:
            self.max_rate_kbps = max_rate_kbps ## MR -- generally set to 1024
            self.link_margin_dB = link_margin_dB
        else:
            self.fixed_rate = fixed_rate
        ## MR -- other hardcoded parameters, at some point many of these will be inputs?
        self.R = np.array([430, 1499.99, 1500, 1999.99, 2000, 2999.99, 3000, 4499.99, 4500, 7499.99, 7500, 10000])
        self.Pt_error = np.array([11.00, 11.00, 8.50, 8.50, 6.00, 6.00, 4.00, 4.00, 3.00, 3.00, 2.50, 2.50])
        self.Antenna_gain = np.arange(11)
        self.SANT = np.array([21.8, 21.8, 21.6, 21.2, 20.6, 19.9, 18.9, 17.7, 16.4, 14.6, 12.6])
        self.ant_gain = [6.5, 4.5, 0]
        self.ant_angle = [90, 60, 30]
        self.popt, self.pcov = curve_fit(self._ext_gain_func, self.ant_angle, self.ant_gain) ## MR -- do we use the cov matrix at all?
        self.ext_gain = lambda angle: self._ext_gain_func(angle, *self.popt)
        

    def _ext_gain_func(self, x, a, b, c):
        '''
        A quadratic function with fittable parameters a,b,c with input x and output y.
        '''
        return a * x**2 + b * x + c

    def demodulation(self, dis_range, max_rate_kbps, extra_ant_gain):
        '''
        Determines signal strength by using minimum link margin to have a higher SNR.
        
        input: range of distances (array), max_rate_kbps (integer of form 2**N), extra_ant_gain (float)

        output: data demodulation margin and data rate.
        
        '''
        
        ## MR -- changed rate_pw2 to max_rate_kbps, is this right???
        # MR -- there are so many hardcoded values here... not sure if they should be here.
        Srange_max = 8887.0   #Slant Range ## MR -- LOS b/w sat and receiver 
        Srange_min = 2162.0
        Srange_mean = 6297.0
    
        Freq_MHz = 2250.0  ## MR -- relay signal? should there be an uncertainty on this? bandwidth uncertainty?
        Asset_EIRP = 13.0 + extra_ant_gain#dBW ## MR -- strength of signal assuming radially symmetric
    
        Srange = dis_range
     
        free_space_path_loss = -20*np.log10(4*np.pi*Freq_MHz*1000000*Srange*1000/300000000) ## MR-- E loss in free space prop to srange and freq
    
        R_interp = np.linspace(430,10000,1000) ## MR -- finer steps of R
        Pt_error_intp = interp1d(self.R,self.Pt_error)  ## MR -- interp function
    
        Off_pt_angle = 0 ## MR -- ideal case of directly overhead? Variation in position angle
        Pt_error_main = Pt_error_intp(Srange) ## MR -- pt 
    
        Antenna_gain_intp = np.linspace(0,10,1000) 
        SANT_intp = interp1d(self.Antenna_gain,self.SANT,fill_value="extrapolate")
        #print(Off_pt_angle + Pt_error_main)
        SANT_main = SANT_intp(Off_pt_angle+Pt_error_main)
        Antenna_return_loss = 15 ## MR-- E loss due to refections
        Mismatch_loss = 10*np.log10(1-(10**(-Antenna_return_loss/20))**2) ## MR --impedance mismatch? 
        SC_noise_temp = 26.8
        SCGT = SANT_main + Mismatch_loss - SC_noise_temp 
        
        Uplink_CN0 = Asset_EIRP + free_space_path_loss + SCGT - 10*np.log10(1.38e-23) ## MR --system carrier to noise
        Mod_loss = 0.0  #says calculated but given
        Implementation_loss = -1.0  #assumed
        Pll_bw_Hz = 700 #assumed ## MR-- Phase locked loop
        Pll_bw_dB = 10*np.log10(Pll_bw_Hz)
        SN_loop = 17.9470058901322 ## MR -- SNR
    
        Carrier_margin = Uplink_CN0 + Implementation_loss - Pll_bw_dB - SN_loop 

        #rate_pw2 = self.max_rate_kbps ## MR -- 1024 so 2**32? is this the max rate??
        #print('Rate is',rate_pw2) ## MR -- debug 
        
        rate_pw2 = np.sqrt(max_rate_kbps)
        Coded_symb_rt_input = rate_pw2 ## MR -- symbols transmitted per second
        Coded_symb_rt = 2**Coded_symb_rt_input
    
        Code_rate = 0.662430862918876   #theory ## MR -- ratio of useful data bits to total transmitted bits
        Data_rate = Coded_symb_rt * Code_rate ## MR -- data rate?
    
        EbN0 = Uplink_CN0 + Implementation_loss - 10*np.log10(Data_rate*1000) ## MR -- E per bit --> noise power spec density ratio?
    
        Threshold_EbN0 = 2.1
        Data_demod_margin = EbN0 - Threshold_EbN0
        
        return Data_demod_margin, Data_rate
        

    def get_rate(self, distance_km, alt_deg, demod_marg, zero_ext_gain=False):
        '''
        Data transfer rate calculation. Begin with minimum power 2**5, tests out different powers and different 
        demods and rates. Converges when maximum pw2 reached (12) or minimum demod_marg (3) is acheived.
        
        input: distance (array), alt_deg (array), demod_marg (integer), zero_ext_gain (boolean)
        output: rate (in what units?), demod, bit rate?
        
        '''
        extra_gain = self.ext_gain(alt_deg) if not zero_ext_gain else 0
        pw2 = 5
        demod_marg = self.link_margin_dB
        print('Demod margin is',demod_marg)
        while True:
            try_demod, try_rate = self.demodulation(distance_km, pw2, extra_gain)
            if (try_demod < demod_marg) or (pw2 == 12):
                break
            pw2 += 1
            rate = try_rate
            demod = try_demod
        return rate, demod, (2**(pw2-1))



