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
