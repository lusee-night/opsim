import lusee
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import time
import pickle

# copied the functions below from previously defined transfer_rate.ipynb from notebooks_git

class Comm():
    def __init__(self, max_rate_kbps=None, link_margin_dB=None, fixed_rate=False):
        if fixed_rate is True:
            self.adaptable_rate = False
            self.fixed_rate = fixed_rate
        else:
            self.adaptable_rate = True
            self.max_rate_kbps = max_rate_kbps # generally set to 1024
            self.link_margin_dB = link_margin_dB
            
        self.R = np.array([430,1499.99,1500,1999.99,2000,2999.99,3000,4499.99,4500,7499.99,7500,10000])
        self.Pt_error = np.array([11.00, 11.00, 8.50, 8.50, 6.00, 6.00, 4.00, 4.00, 3.00, 3.00, 2.50, 2.50])
        self.Antenna_gain = np.arange(11)
        self.SANT = np.array([21.8, 21.8, 21.6, 21.2, 20.6, 19.9, 18.9, 17.7, 16.4, 14.6, 12.6])
        self.ant_gain = [6.5, 4.5, 0]
        self.ant_angle = [90, 60, 30]
        self.popt, self.pcov = curve_fit(self._ext_gain_func, self.ant_angle, self.ant_gain) 
        self.ext_gain = lambda angle: self._ext_gain_func(angle, *self.popt)
        
        self.Freq_MHz = 2250.0
        self.R_interp = np.linspace(430,10000,1000) # finer steps of R
        self.Pt_error_intp = interp1d(self.R,self.Pt_error)  # interp function
    
        self.Off_pt_angle = 0 #
        
        self.Antenna_gain_intp = np.linspace(0,10,1000) 
        self.SANT_intp = interp1d(self.Antenna_gain,self.SANT,fill_value="extrapolate")

    def _ext_gain_func(self, x, a, b, c):
        '''
        A quadratic function with fittable parameters a,b,c with input x and output y.
        '''
        return a * x**2 + b * x + c

    def demodulation(self, dis_range, rate_pw2, extra_ant_gain):
        '''
        Determines signal strength by using minimum link margin to have a higher SNR.
        
        input: range of distances (array), rate_pw2 (integer of form 2**N, kbps), extra_ant_gain (float)

        output: data demodulation margin and data rate (kbps).
        
        '''
        
        Asset_EIRP = 13.0 + extra_ant_gain#dBW # strength of signal assuming radially symmetric
    
        Srange = dis_range
     
        free_space_path_loss = -20*np.log10(4*np.pi*self.Freq_MHz*1000000*Srange*1000/300000000) # E loss in free space prop to srange and freq
    
        
        Pt_error_main = self.Pt_error_intp(Srange)
        SANT_main = self.SANT_intp(self.Off_pt_angle+Pt_error_main)
        Antenna_return_loss = 15 # E loss due to refections
        Mismatch_loss = 10*np.log10(1-(10**(-Antenna_return_loss/20))**2) # impedance mismatch? 
        SC_noise_temp = 26.8
        SCGT = SANT_main + Mismatch_loss - SC_noise_temp 
        
        Uplink_CN0 = Asset_EIRP + free_space_path_loss + SCGT - 10*np.log10(1.38e-23) ## system carrier to noise
        Mod_loss = 0.0  #says calculated but given
        Implementation_loss = -1.0  #assumed
        Pll_bw_Hz = 700 #assumed 
        Pll_bw_dB = 10*np.log10(Pll_bw_Hz)
        SN_loop = 17.9470058901322 
    
        Carrier_margin = Uplink_CN0 + Implementation_loss - Pll_bw_dB - SN_loop 

        #print('Rate power of 2 is',rate_pw2)
        
        Coded_symb_rt_input = rate_pw2 # symbols transmitted per second
        Coded_symb_rt = 2**Coded_symb_rt_input
    
        Code_rate = 0.662430862918876   #theory # ratio of useful data bits to total transmitted bits
        Data_rate = Coded_symb_rt * Code_rate # kbps
    
        EbN0 = Uplink_CN0 + Implementation_loss - 10*np.log10(Data_rate*1000) 
    
        Threshold_EbN0 = 2.1
        Data_demod_margin = EbN0 - Threshold_EbN0
        
        return Data_demod_margin, Data_rate
        

    def get_rate(self, distance_km, alt_deg, max_rate_kbps, demod_marg, zero_ext_gain=False):
        '''
        Data transfer rate calculation. Begin with minimum power 2**5, tests out different powers and different 
        demods and rates. Converges when maximum pw2 reached (12) or minimum demod_marg (3) is acheived.
        
        input: distance (array), alt_deg (array), demod_marg (integer), zero_ext_gain (boolean)
        output: rate (kbps), demod
        
        '''
        extra_gain = self.ext_gain(alt_deg) if not zero_ext_gain else 0
        pw2 = 5
        max_rate_kbps = self.max_rate_kbps
        demod_marg = self.link_margin_dB
        while True:
            try_demod, try_rate = self.demodulation(distance_km, pw2, extra_gain)
            if (try_demod < demod_marg) or (pw2 == int(np.log10(max_rate_kbps)/np.log10(2))-1):
                break
            pw2 += 1
            rate = try_rate
            demod = try_demod
        return rate, demod, (2**(pw2-1))



