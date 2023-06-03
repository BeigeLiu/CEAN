import os
import struct
import pickle as pkl
import sys
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy import optimize
from scipy import signal
class SignalSelector():
    def __init__(self,**kwargs):
        self._LoadConfig()
        pass
    def _LoadConfig(self,**kwargs):
        self.cut_S2 = kwargs.get('cut_S2',[0,30*1e-9]) ## in ns
        self.cut_S1 = kwargs.get('cut_S1',[100*1e-9,2000*1e-9])
        self.peak_height = kwargs.get('peak_height',0.5)
        self.peak_distance = kwargs.get('peak_distance',300)
        self.peak_threshold = kwargs.get('peak_threshold',0.1)
        return
    def FindPeaks(self,data,rel_height = 0.7):
        peaks = signal.find_peaks(data,height    = max([self.peak_height*np.max(data),0.01]),
                                       threshold = self.peak_threshold*np.max(data),
                                       distance  = self.peak_distance)
        width = signal.peak_widths(data,peaks=peaks[0],rel_height = rel_height)
        #plt.plot(data)
        #plt.plot(peaks[0], data[peaks[0]], "x")
        #plt.hlines(*width[1:], color="C2")
        #plt.show()
        return peaks[0],width[0]*4*1e-9
    def S1_filter(self,data):
        S1_spec = np.fft.fft(data)
        freq    = np.fft.fftfreq(data.shape[0],4*1e-9)
        ids = np.where(freq>0)[0]
        #plt.figure(figsize=(6,4))
        #plt.loglog(freq[ids],np.abs(S1_spec)[ids])
        #plt.xlabel('f(Hz)')
        #plt.ylabel('amp(V)')
        #plt.legend()
        #plt.show()
        ids1     = np.where(np.abs(freq)>5*1e6)[0]
        S1_spec[ids1] = S1_spec[ids1]*np.conj(S1_spec[ids1])*0.1
        S1_filter = np.real(np.fft.ifft(S1_spec))
        #plt.figure(figsize=(6,4))
        #plt.plot(t,data,label = 'orignal S1')
        #plt.plot(t,S1_filter,label = 'After filtering')
        #plt.xlabel('t(s)')
        #plt.ylabel('amp(V)')
        #plt.legend()
        #plt.show()
        return S1_filter

    def FineSelection(self,data,width):
        peaks = signal.find_peaks(data,width=width,height=0.02)
        width = signal.peak_widths(data,peaks=peaks[0],rel_height = 0.1)
        #plt.plot(data)
        #plt.plot(peaks[0], data[peaks[0]], "x")
        #plt.hlines(*width[1:], color="C2")
        #plt.show()
        if peaks[0].shape[0]!= 0:
            Dict   = peaks[1]
            height = Dict['peak_heights']
            id     = np.where(height == np.max(height))[0]
            peaks  = peaks[0][id[0]]  
            width  = width[0][id[0]]
            return peaks,width*4*1e-9
        else:
            return 0,0
    def FindAllSignal(self,data):
        peaks,widths = self.FindPeaks(data)
        output = []
        i = 0
        for width in widths:
            peak = peaks[i]
            i   += 1
            if width < self.cut_S1[1] and width > self.cut_S1[0]:
                S1    = self.S1_filter(data)
                begin = max(0,peak-500)
                end   = min(S1.shape[0],peak+500)
                S1    = S1[begin:end]
                _,width = self.FineSelection(S1,width = 100)
                Dict = {'Signal_type':'S1',
                    'peak_index':peak,
                    'height':data[peak],
                    'width':width}
            elif width < self.cut_S2[1] and width > self.cut_S2[0]:
                S1    = self.S1_filter(data)
                begin = max(0,peak-500)
                end   = min(S1.shape[0],peak+500)
                S1    = S1[begin:end]
                _,width = self.FineSelection(S1,width = 100)
                if width < self.cut_S1[1] and width > self.cut_S1[0]:
                    Dict = {'Signal_type':'S1',
                    'peak_index':peak,
                    'height':data[peak],
                    'width':width}
                else:
                    begin = max(0,peak-20)
                    end   = min(data.shape[0],peak+20)
                    S2    = data[begin:end]
                    #t2    = t[begin:end]
                    #Interpfunction = interp1d(t2,S2)
                    #t2_1      = np.linspace(np.min(t2),np.max(t2),t2.shape[0]*100)
                    #S2_interp =     Interpfunction(t2_1)
                    _,width = self.FineSelection(S2,width = 1)
                    if width < self.cut_S2[1] and width > self.cut_S2[0]:
                       Dict = {'Signal_type':'S2',
                               'peak_index':peak,
                               'height':data[peak],
                               'width':width}
                    else:
                        return output
            else:
                return output
            output.append(Dict)
        return output
