# huawei2019
华为2019评判器开源,与线上不完全一致（map1 700时间段以内，map2 600时间段以内）
#更新

2019/3/20 
原代码中，车辆到达设计出发时间无法上路会导致报错。新代码做了更改，未上路的车加入下一时刻判断。
ps:官方并未说明这里如何实现。我的原则如下例子所示：
             按照从左到右依次上路
time:10 [10001,10002,10003,10010] 10010未能上路
time：11 [10010,10004,10005,10006,10007]

answer.txt格式为提交答案格式，但是注意不能有注释。
错误样例：
#****
(carId,plantime,route)
(carId,plantime,route)
(carId,plantime,route)
正例:
(carId,plantime,route)
(carId,plantime,route)
(carId,plantime,route)


运行
python3 simulator.py ../config_11/car.txt ../config_11/road.txt ../config_11/cross.txt ../config_11/answer.txt


class visualization 为可视化模块，输出图片位置在visualization.savePath。
class simulation 中有调用visualization。可注释simulation.simulate()中的 visualize.drawMap()以提高程序运行速度。

#发现问题的记得联系我
qq:2938830818
