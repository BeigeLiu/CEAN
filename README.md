# CEAN
Simple analyse code for  CEAN DAQ  
CAENUnpack.py 是用于解码CAEN Digitizer （725 and 730 系列）的脚本

一.使用方法：
import CAENUnpack

调用UnpackAll 函数即可将二进制文件转换为pickle文件

CAENUnpack().UnpackAll(Inputfilename = ??,Outputfilename = ??)



二.转换出的pickle文件结构：

用如下代码读出转换好的pkl文件
Data = pkl.load(open(filename,'rb')) 
读出的Data为一个列表，每一个元素对应一个事例
Data[0] ：对应第一个事例，其为一个字典类型,下称其为Dict

Dict['Header']为这个事例的一些参数，其为一个字典类型，比如BORAD_ID,PATTERN等等，其意义参考UM5954_724_725_730_DPP-DAW_UserManual_rev2.pdf文档
   
Dict['DATA']为各个Channel读出的数据，其为一个列表类型，下称其为List
   
List中的每一个元素为一个激活channel的数据。
         
List的长度 = 激活的channel数量
         
List[0]: 是一个字典类型，下称其为dict
         
dict['Channel']：int 类型，   对应的channel数，例如: 1
                     
dict['Header']  :  字典类型， 对应这个channel的一些参数，例如TRIGGER_TIME_STAMP(16MSBs)，BASELINE..
                     
dict['Voltages']:  列表类型 ，对应这个channel读出的电压数据
                     
