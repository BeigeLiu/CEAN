import os
import struct
import pickle as pkl
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy import optimize
from scipy import signal
from CAENSignalFinder import SignalSelector
class CAENUnpack():
    def __init__(self,Inputfilename):
        self.file = open(Inputfilename,'rb') ## open file
        self.totalsize = os.path.getsize(Inputfilename) 
        self.SignalSelector = SignalSelector()
        self.initial_dict()
        return
    def initial_dict(self):
        self.Data         = None
        self.NumOfChannel = 16
        self.NumOfEventEachCh   = np.zeros((self.NumOfChannel),dtype=int)
        self.NumOfEvent         = 0
        self.Total_Charge       = []
        return 
    def get_bit_val(self,byte, index):
        if byte & (1 << index):
           return 1
        else:
           return 0
    def read_bytes(self,x,begin,end):
        out = 0
        for i in range(begin,end+1):
            out += self.get_bit_val(x,i)*2**(i-begin)
        return out
    def find_event_pointer(self,index):
        id  = 0
        pos = 0
        sizes = 0
        self.file.seek(0)
        for i in range(index):
            size = self.read_bytes(struct.unpack('i',self.file.read(4))[0],0,27)
            sizes += size
            self.file.seek(sizes*4)
            #print('size',size)
        pos = self.file.tell()
        #print(pos)
        return pos

    def ReadOneEvent(self,index = 0,pointer=None):
        #print(self.file.read(4))
        if pointer == None:
           pointer = self.find_event_pointer(index) 
        self.file.seek(pointer)                                         ## initial the pointer location of this event
        EVENTSIZE    = self.read_bytes(struct.unpack('i',self.file.read(4))[0],0,27)
        #return 
        ## Read out the event size 
        Header   = struct.unpack('3i',self.file.read(12))     ## Read out this event data
        Header   = list(Header)


        ###### Read out header
        BORAD_ID     = self.read_bytes(Header[0],27,31)  
        BF           = self.read_bytes(Header[0],26,26) 
        BORAD_EVENT_COUNTER  = self.read_bytes(Header[1],0,23)   
        BORAD_EVENT_TIME_TAG = self.read_bytes(Header[2],0,31)                        ## 
        CHANNEL_MASK = []
        for i in range(8):
            CHANNEL_MASK.append(self.get_bit_val(Header[0],i))          ## Read out channel mask 0 ~ 7
        for i in range(8):
            CHANNEL_MASK.append(self.get_bit_val(Header[1],24+i))       ## Read out channel mask 8 ~ 15
        #print(BORAD_EVENT_COUNTER,
        #      BF,
        #      BORAD_ID,
        #      BORAD_EVENT_COUNTER,
        #      BORAD_EVENT_TIME_TAG,
        #      CHANNEL_MASK)
        DATA = []

        ###### Read out each channel data
        for i in range(len(CHANNEL_MASK)):  ### totally 16 channels
          if CHANNEL_MASK[i] == 1:          ### find the active channels
             Channel_Header             = struct.unpack('3i',self.file.read(12))
             temp = {}
             temp['Channel'] = i
             temp['Header']  = {}
             temp['Header']['RESERVED'] = self.read_bytes(Channel_Header[0],23,28)
             temp['Header']['TRUNC']    = self.read_bytes(Channel_Header[0],29,29)
             temp['Header']['CHANNEL_SIZE']               = self.read_bytes(Channel_Header[0],0,22)
             temp['Header']['TRIGGER_TIME_STAMP(32LSBs)'] = self.read_bytes(Channel_Header[1],0,31)
             temp['Header']['TRIGGER_TIME_STAMP(16MSBs)'] = self.read_bytes(Channel_Header[2],0,15)
             temp['Header']['BASELINE'] = self.read_bytes(Channel_Header[2],16,29)*0.00012
             temp['Voltages']= []
             #print(temp)
             #print(self.file.tell())
             #t1 = time.time()
             #for j in range(2*(temp['Header']['CHANNEL_SIZE']-3)):  ## 3 is the length of header char
             number = temp['Header']['CHANNEL_SIZE']-3
             Voltages = np.fromfile(self.file,dtype=np.short,count = 2*number,offset=0)#struct.unpack(str(2*number)+'h',self.file.read(4*number))
             temp['Voltages'] = Voltages*0.00012 ## 0.00012 Digital-to-simulate conversion factor
             #print(self.file.tell())

             DATA.append(temp)
        ### output event data
        OUTPUT = {'Header':{}}
        OUTPUT['Header']['EVENTSIZE'] = EVENTSIZE
        OUTPUT['Header']['BORAD_ID']  = BORAD_ID
        OUTPUT['Header']['BF']        = BF
        OUTPUT['Header']['BORAD_EVENT_COUNTER']  = BORAD_EVENT_COUNTER
        OUTPUT['Header']['BORAD_EVENT_TIME_TAG'] = BORAD_EVENT_TIME_TAG
        OUTPUT['Header']['CHANNEL_MASK']         = CHANNEL_MASK
        OUTPUT['DATA']                = DATA
        pos = self.file.tell()                                ## reserve the current pointer location
        #print(pos)
        #self.file.seek(0)                                     ## reset the pointer location
        #print(OUTPUT)
        return OUTPUT,pos

    def PrintEventInfo(self,index=0,pointer = None):
        event,pos = self.ReadOneEvent(index = index,pointer=pointer)
        for key in event.keys():
            if key == 'Header':
                print('===Header of the event===')
                for k in event[key].keys():
                    print(k+':'+str(event[key][k]))
            elif key == 'DATA':
                for item in event[key]:
                    for k in item.keys():
                      if k == 'Channel':
                        channel = item[k]
                      elif k == 'Header':
                        print('===Information of channel '+str(channel)+'===')
                        for k_1 in item[k].keys():
                            print(k_1 +':'+str(item[k][k_1]))
                      else:
                        print(k+':'+str(item[k]))
        return

    def ToPickle(self,Outputfilename =None):
        if self.Data == None:
            self.ReadAll()
        if Outputfilename != None:
            pkl.dump(self.Data,open(Outputfilename,'wb+'))
        return

    def GetOneEventCharge(self,index = 0,pointer = None):
        event,pos            = self.ReadOneEvent(index = index,pointer = pointer)
        channel_mask         = np.asarray(event['Header']['CHANNEL_MASK'])
        charge_of_this_event = np.zeros(channel_mask.shape[0])
        for item in event['DATA']:
            baseline   = item['Header']['BASELINE']
            voltages   = -(item['Voltages'] - baseline)
            channel_id = item['Channel']
            peaks      = self.SignalSelector.FindAllSignal(voltages)
            if len(peaks) != 0:
                peak_id    = peaks[0]['peak_index']
                peak_width = peaks[0]['width']
                voltages   = voltages[int(peak_id-3*(peak_width)/(2*4*1e-9)):int(peak_id+3*(peak_width)/(2*4*1e-9))]*4*1e-9/50
                charge     = np.sum(np.asarray(voltages))
                charge_of_this_event[channel_id] = charge
            else:
                charge_of_this_event[channel_id] = 0
        return charge_of_this_event,pos

    def GetAllCharge(self,verbose = True):
        pos = 0
        self.Total_Charge = []
        while pos != self.totalsize:
            if verbose:
               print("\r", end="")
               i = int(pos*100/self.totalsize)    
               print("Calculating Charge: {}%: ".format(i), "▓" * (i // 2), end="")    
            #sys.stdout.flush()    
            #time.sleep(0.0000000005)
            #t = time.time()
            Charge,pos = self.GetOneEventCharge(pointer= pos)
            #print(time.time()- t)
            self.Total_Charge.append(np.asarray(Charge))
        self.Total_Charge = np.asarray(self.Total_Charge)
        return self.Total_Charge
    def PlotChargeHistogram(self,channel_id = 0,bins = 50,save_path = None):
        if len(self.Total_Charge) == 0:
               self.Total_Charge = self.GetAllCharge()
        Charge = self.Total_Charge[:,channel_id]
        ids    = np.where(Charge != 0)[0]
        Charge = -Charge[ids]
        Fit_y,Fit_x,_    = self.GuassFit(Charge,bins)
        plt.figure(figsize=(6,4))
        plt.hist(Charge,bins = bins,label = 'Data')
        plt.plot(Fit_x,Fit_y,'r--')#,label = 'Fit Params:'+'\n'+'mu = '+str(mu)+'\n'+'sigma = '+str(sigma))
        plt.xlabel('Charge')
        plt.ylabel('Probablity(%)')
        plt.legend(fontsize = 8)
        plt.title('Charge Histogram of Channel '+str(channel_id))
        plt.show()
        if save_path != None:
            plt.savefig(save_path+'_channel_'+str(channel_id)+'.pdf')
        return 
    def GuassFunction(self,x,height,mu,sigma):
        y = height*np.exp(-np.power(x-mu,2)/np.power(sigma,2))
        return y
    def GuassFit(self,data,bins):
        mu    = np.mean(data)
        sigma = np.std(data)
        count,bins = np.histogram(data,bins = bins)
        y = self.GuassFunction(bins,mu,sigma)
        return y,bins,mu,sigma
    def DoubleGuassFit(self,data,bins):
        count,bins = np.histogram(data,bins = bins)
        bins       = bins[1:]
        peaks,_    = signal.find_peaks(count,height = 0.2*np.median(count),distance=10)
        params_1,pcov1 = optimize.curve_fit(self.GuassFunction, ydata = count[peaks[0]-5:peaks[0]+5],
                                                            xdata = bins[peaks[0]-5:peaks[0]+5],
                                                            #p0    = [np.max(count[peaks[0]-5:peaks[0]+5]),
                                                            #         np.mean(bins[peaks[0]-5:peaks[0]+5]),
                                                            #         np.std(bins[peaks[0]-5:peaks[0]+5])
                                                            #         ]
        )
        perr1      = np.sqrt(np.diag(pcov1))
        params_2,pcov2 = optimize.curve_fit(self.GuassFunction, ydata = count[peaks[1]-5:peaks[1]+5],
                                                            xdata = bins[peaks[1]-5:peaks[1]+5],
                                                            #p0    = [np.max(count[peaks[1]-7:peaks[1]+7]),
                                                            #         np.mean(bins[peaks[1]-7:peaks[1]+7]),
                                                            #         np.std(bins[peaks[1]-7:peaks[1]+7])
                                                            #                ]
        )
        perr2      = np.sqrt(np.diag(pcov2))
        Fit_y_1 = self.GuassFunction(bins,*params_1)
        Fit_y_2 = self.GuassFunction(bins,*params_2)
        return Fit_y_1,Fit_y_2,bins,params_1,params_2,perr1,perr2
    def PlotSPE(self,channel_id = 0,bins = 120,save_path = None):
        if len(self.Total_Charge) == 0:
               self.Total_Charge = self.GetAllCharge()
        Charge = self.Total_Charge[:,channel_id]
        ids    = np.where(Charge != 0)[0]
        Charge = Charge[ids]/(1.6*1e-19)
        #Fit_y_1,Fit_y_2,Fit_x,params1,params2,perr1,perr2     = self.DoubleGuassFit(Charge,bins)
        #collabels = ['height','mean','std']
        #rowlabels = ['BE','SPE']
        #params    = np.asarray([[str(np.round(params1[0],decimals=2))+chr(177)+str(np.round(perr1[0],decimals=2)),
        #                 str(np.round(params1[1],decimals=2))+chr(177)+str(np.round(perr1[1],decimals=2)),
        #                 str(np.round(params1[2],decimals=2))+chr(177)+str(np.round(perr1[2],decimals=2))],
        #                 [str(np.round(params2[0],decimals=2))+chr(177)+str(np.round(perr2[0],decimals=2)),
        #                 str(np.round(params2[1],decimals=2))+chr(177)+str(np.round(perr2[1],decimals=2)),
        #                 str(np.round(params2[2],decimals=2))+chr(177)+str(np.round(perr2[2],decimals=2))]])
        charge,bins = np.histogram(Charge,bins = bins)
        plt.figure(figsize=(9,6))
        plt.plot(bins[1:],charge,drawstyle='steps-mid')
        #plt.plot(Fit_x,Fit_y_1,'--')
        #plt.plot(Fit_x,Fit_y_2,'--')
        plt.xlabel('charge')
        plt.ylabel('count')
        plt.yscale('log')
        #plt.ylim([1,1.3*np.max(Fit_y_1)])
        #plt.table(cellText=params,
        #  colLabels=collabels,
        #  rowLabels=rowlabels,
        #  colWidths=[0.2]*4,
        #  loc = 'upper right')
        plt.title('Charge Histogram of Channel '+str(channel_id))
        plt.show()
        if save_path != None:
            plt.savefig(save_path+'_channel_'+str(channel_id)+'.pdf')
        return 
    def PlotOneEvent(self,index = 0, pointer = None,save_path = None,peaks = None):
        event,pos = self.ReadOneEvent(index=index,pointer=pointer)
        for item in event['DATA']:
            channel  = item['Channel']
            baseline = item['Header']['BASELINE']
            voltages = item['Voltages']-baseline
            t        = np.linspace(0,voltages.shape[0],voltages.shape[0])*4
            plt.figure(figsize=(6,4))
            plt.plot(t,voltages, drawstyle='steps-mid')
            plt.xlabel('time(ns)')
            plt.ylabel('voltages(V)')
            plt.title('Wave shape of Channel '+str(channel))
            plt.legend(['Baseline is :'+str(baseline)],
                       loc = 'upper right')
            plt.show()
            if save_path != None:
               plt.savefig(save_path+'_event_'+str(index)+'_channel_'+str(channel)+'.pdf')
        return
    
    def ReadAll(self,verbose = True):
        self.Data = []
        pos = 0
        #n = 0
        #t1 = time.time()
        while pos != self.totalsize:
            #n += 1
            if verbose:
               print("\r", end="")
               i = int(pos*100/self.totalsize)    
               print("Unpacking: {}%: ".format(i), "▓" * (i // 2), end="")    
            #sys.stdout.flush()    
            #time.sleep(0.0000000005)
            #t = time.time()
            event,pos = self.ReadOneEvent(pointer= pos)
            #print(time.time()- t)
            self.Data.append(event)
            #if n == 4:
            #    break
        print('\n')
        #t2 = time.time()
        return 

    def GetTotalEventNumber(self):
        if self.Data == None:
            self.ReadAll(verbose=False)
        if np.max(self.NumOfEventEachCh) == 0:
            for event in self.Data:
                self.NumOfEventEachCh += np.array(event['Header']['CHANNEL_MASK'])
            self.NumOfEvent       = int(np.max(self.NumOfEventEachCh))
            self.NumOfEventEachCh = self.NumOfEventEachCh
        else:
            pass
        return self.NumOfEvent,self.NumOfEventEachCh
