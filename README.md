# CAEN
Simple analyse code for TPC data in USTC

一.加载数据

from Dataset import Dataset

Dataset.py 是用于加载并控制数据的模组,对于给定的文件,可以如下构建数据

data = Dataset()

data.loadfromraw(filename)

此时你已经加载了数据,需要查看某个给定的触发时,可以如下索引:

item = data.datalist[i] ## 取出第i个触发

每个触发（即上述item）是一个类,其内置display方法用以绘制这个触发各通道的波形图：

item.display()

item 一个item包含如下性质
item.triggerTime ## 触发相对于第一次触发的时间,单位μs
item.traces      ## 一个列表,每个元素为各个激活通道的触发波形
item.charge      ## 一个列表,各个通道的电量积分值,在建立Dataset时自动计算
item.peaks       ## 一个列表,各个通道的峰位索引,在建立Dataset时自动计算

二.基本数据分析

Dataset类包含了基本的数据分析算法,包括寻峰,波形识别,电量计算,绘图等

在建立Dataset对象时,会自动进行寻峰,波形识别与电量计算

需要绘制PE谱时,则需要调用:
data = Dataset()

data.loadfromraw(filename)

data.PlotPE()
