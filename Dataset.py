import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt
from CAENReader import RawTrigger,DataFile
import os
import SimpleSelector
import PeakAnalyser
import sys
class Dataset:
    def __init__(self):
        self.datalist = []
        self.PE      = {'S1_PE':[],
                         'S2_PE':[]}
        self.LoadParams()
        return
    def LoadParams(self):
        self.gain = 3e6
        self.electroncharge = 1.6*1e-19 
    def CalculatePE(self):
        S1_charge = []
        S2_charge = []
        for item in self.datalist:
            for channel in range(len(item.signaltype)):
                if item.signaltype[channel] == 1:
                    S1_charge.append(item.charge[channel]/(self.electroncharge*self.gain))
                elif item.signaltype[channel] == 2:
                    S2_charge.append(item.charge[channel]/(self.electroncharge*self.gain))
        count,bins  = np.histogram(S1_charge,bins = 100)
        self.PE['S1_PE'] = (bins,count)
        count,bins = np.histogram(S2_charge,bins = 100)
        self.PE['S2_PE'] = (bins,count)
        return self.PE
    def PEFit(self):
        return
    def PlotPE(self,channel_id = 0,bins = 50,save_path = None,x_scale = None,y_scale = None):
        if len(self.PE['S1_PE']) == 0:
            self.CalculatePE()
        plt.figure(figsize=(6,4))
        bins,count = self.PE['S1_PE']
        plt.plot(bins[1:],count,drawstyle='steps-mid',label = 'S1')
        bins,count = self.PE['S2_PE']
        plt.plot(bins[1:],count,drawstyle='steps-mid',label = 'S2')
        plt.xlabel('PE')
        plt.ylabel('Count')
        plt.legend(fontsize = 8)
        plt.grid()
        plt.title('Charge Histogram of Channel '+str(channel_id))
        if x_scale != None:
            plt.xscale(x_scale)
        if y_scale != None:
            plt.xscale(y_scale)
        if save_path != None:
            plt.savefig(save_path+'_channel_'+str(channel_id)+'.pdf')
        plt.show()
        return 
    def dumpPE(self,filename):
        pkl.dump(self.PE,open(filename,'wb'))
        return 
    def append(self,x):
        self.datalist.append(x)
    def dumptopkl(self,filepath):
        output = {'events':[],
                  'PE':self.PE}
        for item in self.datalist:
            output['events'].append(item.todict())
        pkl.dump(output,open(filepath,'wb'))
        return 
    def loadfrompkl(self,filepath):
        Dict = pkl.load(open(filepath,'rb'))
        data = Dict['events']
        self.PE = Dict['PE']
        for item in data:
            trigger = RawTrigger()
            trigger.loadfromdict(item)
            self.datalist.append(trigger)
        return 
    def loadfromraw(self,filepath):
        dataFile = DataFile(filepath)
        totalsize       = os.path.getsize(filepath)
        pos             = 0
        while pos < 0.999*totalsize:
            i = int(pos*100/totalsize)    
            print("\r", end="")
            i = int(pos*100/totalsize)  
            print("Unpacking: {}%: ".format(i), "▓" * (i // 2), end="") 
            sys.stdout.flush() 
            trigger = dataFile.getNextTrigger()
            for key in trigger.traces.keys():
                data    = 0.00012*trigger.traces[key][5:]
                data    = -(data-data[0])
                Dict    = SimpleSelector.SignalSelect(data = data)
                trigger.signaltype.append(Dict['Signal_type'])
                trigger.peakindex.append(Dict['peak_index'])
                charge,begin,end =  PeakAnalyser.CalculateCharge(data,Dict['peak_index'],Dict['Signal_type'])
                trigger.charge.append(charge)
                trigger.integrate_range.append([begin,end])
            pos     = trigger.filePos
            self.datalist.append(trigger) 
        return
