# CEAN
Simple analyse code for  CEAN DAQ  
CAENUnpack.py 是用于解码CAEN Digitizer （725 and 730 系列）的脚本

一.使用方法：

     import CAENUnpack
   
     CAENUnpack().ReadAll(Inputfilename = ??,Outputfilename = ??)



二.转换出的数据结构：
读出的Data为一个列表，每一个元素对应一个事例
Data[0] ：对应第一个事例，其为一个字典类型,下称其为Dict

Dict['Header']为这个事例的一些参数，其为一个字典类型，比如BORAD_ID,PATTERN等等，其意义参考UM5954_724_725_730_DPP-DAW_UserManual_rev2
   
Dict['DATA']为各个Channel读出的数据，其为一个列表类型，下称其为List
   
List中的每一个元素为一个激活channel的数据。
         
List的长度 = 激活的channel数量
         
List[0]: 是一个字典类型，下称其为dict
         
dict['Channel']：int 类型，   对应的channel数，例如: 1
                     
dict['Header']  :  字典类型， 对应这个channel的一些参数，例如TRIGGER_TIME_STAMP(16MSBs)，BASELINE..
                     
dict['Voltages']:  列表类型 ，对应这个channel读出的电压数据
                     
三.内置方法
1. 绘制单个事例 
Module.PlotOneEvent(index = optional,pointer = optional)。其中参数index是第几个事例,pointer是指这个事例的指针,如果没有给定pointer,默认按照index绘图,如果不含index参数默认绘制第0个事例。

2. S1，S2寻峰算法
S1,S2寻峰算法可以用户指定也可以使用默认算法,用户指定需要重写SignalSelector模组,这个模组需要包含一个名为FindSignal()的方法。
具体地,用户需要写一个包含FindSignal()方法的模组,这里令这个模组为MySignalSelector()，则只需要在分析代码前指定：
Module.SignalSelector() = MySignalSelector()即可。

3. 绘制SPE能谱 Module.PlotSPE()
