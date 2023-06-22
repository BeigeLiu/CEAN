import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

cut_S1         = [0,100*1e-9] # in ns
cut_S2         = [100*1e-9,2000*1e-9] # in ns
peak_height    = 0.02
peak_distance  = 200 # in ns
peak_threshold = 0.02 # in V

def S2_filter(data):
    S1_spec = np.fft.fft(data)
    freq    = np.fft.fftfreq(data.shape[0],4*1e-9)

    ids1     = np.where(np.abs(freq)>5*1e6)[0]
    S1_spec[ids1] = S1_spec[ids1]*np.conj(S1_spec[ids1])*0.1
    S1_filter = np.real(np.fft.ifft(S1_spec))
    return S1_filter

def FineSelection(data,width,plot = False):
    peaks = signal.find_peaks(data,width=width,height=0.02)
    width = signal.peak_widths(data,peaks=peaks[0],rel_height = 0.5)
    if plot:
        plt.plot(data,drawstyle='steps-mid')
        plt.plot(peaks[0], data[peaks[0]], "x")
        plt.hlines(*width[1:], color="C2")
        plt.xlabel('t(4ns)')
        plt.ylabel('V')
        plt.show()
    if peaks[0].shape[0]!= 0:
        Dict   = peaks[1]
        height = Dict['peak_heights']
        id     = np.where(height == np.max(height))[0]
        peaks  = peaks[0][id[0]]  
        width  = width[0][id[0]]
        return peaks,width*4*1e-9
    else:
        return 0,0

def SignalSelect(data):

    ###### input : a 1-d array, wave shape
    #      output: a dict, key: 'Signal_type':int1 for S1, 2 for S2, 0 for others,
    #                           'peak_index': int where the peak begin  
    data    = S2_filter(data)
    peaks,_ = signal.find_peaks(data,height=0.5*np.max(data),distance = 300)
    width   = signal.peak_widths(data,peaks=peaks,rel_height = 0.1)
    if peaks.shape[0] == 0:
        Dict  = {'Signal_type':0,
             'peak_index':0}
        return Dict
    peaks   = peaks[0]  
    width   = width[0][0]*4*1e-9
    Dict  = {'Signal_type':0,
             'peak_index':0}
    if (width < cut_S2[1]) and (width > cut_S2[0]):
        Dict = {'Signal_type':2,
                 'peak_index':peaks} 
    elif width < cut_S1[1] and width > cut_S1[0]:
        Dict = {'Signal_type':1,
                 'peak_index':peaks} 
    else:
        Dict = {'Signal_type':0,
                 'peak_index':0} 
    return Dict