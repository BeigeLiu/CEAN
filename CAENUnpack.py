import os
import struct
import pickle as pkl
import sys
import time
class CAENUnpack():
    def __init__(self):
        return
    def get_bit_val(self,byte, index):
        if byte & (1 << index):
           return 1
        else:
           return 0
    def ReadBytes(self,x,begin,end):
        out = 0
        for i in range(begin,end+1):
            out += self.get_bit_val(x,i)*2**(i-begin)
        return out
    def Unpack(self,pointer):
        self.file.seek(pointer)                                         ## initial the pointer location of this event
        EVENTSIZE    = self.ReadBytes(struct.unpack('i',self.file.read(4))[0],0,27)     
        ## Read out the event size 
        Header   = struct.unpack('3i',self.file.read(12))     ## Read out this event data
        Header   = list(Header)


        ###### Read out header
        BORAD_ID     = self.ReadBytes(Header[0],27,31)  
        BF           = self.ReadBytes(Header[0],26,26) 
        BORAD_EVENT_COUNTER  = self.ReadBytes(Header[1],0,23)   
        BORAD_EVENT_TIME_TAG = self.ReadBytes(Header[2],0,31)                        ## 
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
             temp['Header']['RESERVED'] = self.ReadBytes(Channel_Header[0],23,28)
             temp['Header']['TRUNC']    = self.ReadBytes(Channel_Header[0],29,29)

             temp['Header']['CHANNEL_SIZE']               = self.ReadBytes(Channel_Header[0],0,22)
             temp['Header']['TRIGGER_TIME_STAMP(32LSBs)'] = self.ReadBytes(Channel_Header[1],0,31)
             temp['Header']['TRIGGER_TIME_STAMP(16MSBs)'] = self.ReadBytes(Channel_Header[2],0,15)
             temp['Header']['BASELINE'] = self.ReadBytes(Channel_Header[2],16,29)
             temp['Voltages']= []
             #print(temp)
             #print(self.file.tell())
             #t1 = time.time()
             #for j in range(2*(temp['Header']['CHANNEL_SIZE']-3)):  ## 3 is the length of header char
             number = temp['Header']['CHANNEL_SIZE']-3
             Voltages = struct.unpack(str(2*number)+'h',self.file.read(4*number))
             temp['Voltages'] = Voltages
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
        #self.file.seek(0)                                     ## reset the pointer location
        return OUTPUT,pos

    def UnpackAll(self,Inputfilename,Outputfilename):
        self.file = open(Inputfilename,'rb') ## open file
        totalsize = os.path.getsize(Inputfilename) 
        Output = []
        pos = 0
        #t1 = time.time()
        while pos != totalsize:
            print("\r", end="")
            i = int(pos*100/totalsize)    
            print("Unpacking: {}%: ".format(i), "▓" * (i // 2), end="")    
            sys.stdout.flush()    
            #time.sleep(0.0000000005)
            #t = time.time()
            event,pos = self.Unpack(pos)
            #print(time.time()- t)
            Output.append(event)
        #t2 = time.time()
        print('Finished')
        #print('unpacking binary file uses:',t2-t1,'s')
        #t1 = time.time()
        pkl.dump(Output,open(Outputfilename,'wb+'))
        #t2 = time.time()
        #print('saving to pkl file uses:',t2-t1,'s')
        return