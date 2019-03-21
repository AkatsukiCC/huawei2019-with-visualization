# huawei2019
华为2019评判器开源,与线上不完全一致（map1 700时间段以内，map2 600时间段以内)

#***** 注意，比赛代码会查重，请小心使用=v=! ****#


#**** 更新 ****#

2019/3/21
加入锁死判据：
    在一个cross循环中，若所有cross都未更新，即锁死。cross循环指按cross id 升序遍历所有cross的过程。（注：例外，当所有cross上所有道路都更新完毕时，再一次cross循环时，所有cross是不会更新的，如起始状态。）

2019/3/20 
原代码中，车辆到达设计出发时间无法上路会导致报错。新代码做了更改，未上路的车加入下一时刻判断。
ps:官方并未说明这里如何实现。我的原则如下例子所示：
             按照从左到右依次上路
time:10 [10001,10002,10003,10010] 10010未能上路
time：11 [10010,10004,10005,10006,10007]



#**** 使用说明 ****#

(1)路径为官方SDK路径，代码存放与src目录下（与CodeCraft-2019.py 同目录）

(2)answer.txt格式为提交答案格式，但是注意不能有注释。
错误样例：
#xxxxx
(carId,plantime,route)
(carId,plantime,route)
(carId,plantime,route)
正例:
(carId,plantime,route)
(carId,plantime,route)
(carId,plantime,route)

(3)运行
python3 simulator.py ../config_11/car.txt ../config_11/road.txt ../config_11/cross.txt ../config_11/answer.txt

(4)可视化部分
请取消visualize.drawMap()的注释以启用可视化。
class visualization 为可视化模块，输出图片所在文件夹记录在visualization.savePath，为所有时刻的车辆状况图片。
class simulation 中有调用visualization。可注释simulation.simulate()中的 visualize.drawMap()以提高程序运行速度。

(5)图片信息详细介绍
参考   "介绍图片.png"

#**** 发现问题的记得联系我 ****#
qq:2938830818
