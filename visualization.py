#
#这是一条骗星的注释
#欢迎来github:https://github.com/AkatsukiCC/huawei2019-with-visualization点星 =v=
#




#**********************************python可视化开源*****************************#
import sys
import numpy as np
import cv2 as cv

np.random.seed(951105)

TIME = [0]
CARDISTRIBUTION = [0,0,0]
CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE = [],[],[]
CROSSDICT,CARDICT,ROADDICT ={},{},{}



class CAR(object):
    def __init__(self,id_):
        self.id_= id_
        self.carColor = [int(value) for value in np.random.random_integers(0, 255, [3])]
    #
    def __carColor__(self):
        return self.carColor

class ROAD(object):
    def __init__(self,id_, length_, speed_, channel_, from_, to_, isDuplex_):
        # **** statistic parameters ****#
        self.id_, self.length_, self.speed_, self.channel_, self.from_, self.to_, self.isDuplex_ = \
            id_, length_, speed_, channel_, from_, to_, isDuplex_
        # **** dynamic parameters ****#
        # absolute bucket
        self.forwardBucket = {i: [None for j in range(self.channel_)] for i in range(self.length_)}
        self.backwardBucket = {i: [None for j in range(self.channel_)] for i in
                               range(self.length_)} if self.isDuplex_ else None
        self.fx, self.fy, self.bx, self.by, self.forwardNum, self.backwardNum = [0], [0], [0], [0], [0], [0]
        self.forwardDone, self.backwardDone = [False], [False]
        # relative bucket
        self.provideBucket, self.receiveBucket = None, None
        self.px, self.py, self.provideNum, self.receiveNum = None, None, None, None
        self.provideDone = None
    #
    # determine relative bucket
    #
    def chooseAbsoluteBucket(self,crossId,pr):
        if crossId == self.from_ and pr == 'provide':
            return 'backward'
        elif crossId == self.from_ and pr == 'receive':
            return 'forward'
        elif crossId == self.to_ and pr == 'provide':
            return 'forward'
        elif crossId == self.to_ and pr == 'receive':
            return 'backward'
        else:
            print("Keywords mistake in CAR.chooseAbsoluteBucket()")
    def setBucket(self,crossId):
        bucket = self.chooseAbsoluteBucket(crossId, 'provide')
        if bucket == 'forward':
            self.provideBucket, self.px, self.py, self.provideDone, self.provideNum = \
                [self.forwardBucket, self.fx, self.fy, self.forwardDone, self.forwardNum]
            if self.isDuplex_:
                self.receiveBucket, self.receiveNum = \
                    self.backwardBucket, self.backwardNum
            else:
                self.receiveBucket, self.receiveNum = None, None
        else:
            self.receiveBucket, self.receiveNum = \
                self.forwardBucket, self.forwardNum
            if self.isDuplex_:
                self.provideBucket, self.px, self.py, self.provideDone, self.provideNum = \
                    self.backwardBucket, self.bx, self.by, self.backwardDone, self.backwardNum
            else:
                self.provideBucket, self.px, self.py, self.provideDone, self.provideNum = \
                    None, None, None, None, None
    def writeForward(self,data):
        for i in range(self.length_):
            for j in range(self.channel_):
                self.forwardBucket[i][j] = data[j][i]
    def writeBackward(self,data):
        for i in range(self.length_):
            for j in range(self.channel_):
                self.backwardBucket[i][j] = data[j][i]
    def __from__(self):
        return self.from_
    def __to__(self):
        return self.to_
    def __length__(self):
        return self.length_
    def __channel__(self):
        return self.channel_
    def __isDuplex__(self):
        return self.isDuplex_
    def __forwardBucket__(self):
        return self.forwardBucket
    def __backwardBucket__(self):
        return self.backwardBucket

class CROSS(object):
    def __init__(self, id_, north_, east_, south_, west_):
        # **** statistic parameters ****#
        self.id_ = id_
        self.roadIds = [north_, east_, south_, west_]
        self.carport = {}
        self.left=[]
        # absolute loc
        self.x, self.y = 0, 0
        self.mapX,self.mapY = 0,0
        # priorityMap
        self.directionMap = {north_: {east_: 1, south_: 2, west_: -1}, \
                             east_: {south_: 1, west_: 2, north_: -1}, \
                             south_: {west_: 1, north_: 2, east_: -1}, \
                             west_: {north_: 1, east_: 2, south_: -1}}
        # relationship with roads
        self.providerDirection, self.receiverDirection, self.validRoadDirecction = [], [], []
        for index, roadId in enumerate(self.roadIds):
            road = ROADDICT[roadId] if roadId != -1 else None
            if road is not None and (road.__isDuplex__() or road.__to__() == self.id_):
                self.providerDirection.append(index)
            if road is not None and (road.__isDuplex__() or road.__from__() == self.id_):
                self.receiverDirection.append(index)
            if road is not None:
                self.validRoadDirecction.append(index)
        self.provider = [self.roadIds[direction] for direction in self.providerDirection]
        self.receiver = [self.roadIds[direction] for direction in self.receiverDirection]
        self.validRoad = [self.roadIds[direction] for direction in self.validRoadDirecction]
        # **** flag ****#
        self.done = False
    def setDone(self,bool):
        self.done = bool
    def setLoc(self,x,y):
        self.x,self.y = x,y
    def setMapLoc(self,mapX,mapY):
        self.mapX,self.mapY = mapX,mapY
    def roadDirection(self,roadId):
        if self.roadIds[0]==roadId:
            return 0
        elif self.roadIds[1]==roadId:
            return 1
        elif self.roadIds[2]==roadId:
            return 2
        elif self.roadIds[3]==roadId:
            return 3
        else:
            return -1
    def __done__(self):
        return self.done
    def __loc__(self):
        return  self.x,self.y
    def __mapLoc__(self):
        return self.mapX,self.mapY
    def __validRoad__(self):
        return self.validRoad


class visualization(object):
    def __init__(self):
        self.maxX,self.maxY = 0,0
        self.savePath = './simulatePictures'
        if not os.path.exists(self.savePath):
            os.makdir(self.savePath)
        # ** cross param **#
        self.crossRadius = 14
        self.crossDistance = 150
        self.crossColor = [25,200,0]
        # ** road param **#
        self.roadColor = [0,0,0] #black
        self.roadLineType = 4
        self.channelWidth = 5
        self.channelDistance = 3
        self.lineWidth = 2
        self.time = 0
    #
    # cross location gen
    #
    def crossLocGen(self):
        #**** relative location ****#
        # denote the first cross as the origin of coordinates
        for crossId in CROSSNAMESPACE:
            CROSSDICT[crossId].setDone(False)
        crossList = [CROSSNAMESPACE[0]]
        minX,minY = 0,0
        while(crossList.__len__()>0):
            nextCrossList = []
            for crossId in crossList:
                presentX,presntY = CROSSDICT[crossId].__loc__()
                validRoad = CROSSDICT[crossId].__validRoad__()
                for roadId in validRoad:
                    #next cross id
                    nextCrossId = ROADDICT[roadId].__from__() if ROADDICT[roadId].__from__() != crossId \
                                                            else ROADDICT[roadId].__to__()
                    # if next cross is visited
                    if not CROSSDICT[nextCrossId].__done__():
                        # visit sets true
                        CROSSDICT[nextCrossId].setDone(True)
                        # relative location of nextcross
                        nextX,nextY = self.crossRelativeLoc(presentX,presntY,crossId,roadId)
                        # update location
                        CROSSDICT[nextCrossId].setLoc(nextX,nextY)
                        minX,minY,self.maxX,self.maxY=\
                                    min(nextX,minX),min(nextY,minY),max(nextX,self.maxX),max(nextY,self.maxY)
                        nextCrossList.append(nextCrossId)
            crossList = nextCrossList
        self.maxX,self.maxY = (self.maxX-minX+2)*self.crossDistance,(self.maxY-minY+2)*self.crossDistance
        for crossId in CROSSNAMESPACE:
            x,y = CROSSDICT[crossId].__loc__()
            CROSSDICT[crossId].setLoc(x-minX,y-minY)
            CROSSDICT[crossId].setMapLoc((x - minX+1)*self.crossDistance, (y - minY+1)*self.crossDistance)
    def crossRelativeLoc(self,x,y,crossId,roadId):
        roadDirection = CROSSDICT[crossId].roadDirection(roadId)
        if roadDirection==0:
            return x,y-1
        elif roadDirection==1:
            return x+1,y
        elif roadDirection==2:
            return x,y+1
        elif roadDirection==3:
            return x-1,y
        else:
            print("Cross(%d) don't interact with road(%d)"%(self.id_,roadId))
    #
    # draw functions
    #
    def drawMap(self):
        img = np.ones((self.maxX,self.maxY,3),np.uint8)*255
        #draw road
        for roadId in ROADNAMESPACE:
            self.plotRoad(roadId,img)
        # draw cross
        for crossId in CROSSNAMESPACE:
            self.plotCross(crossId,img)
        cv.imwrite(self.savePath+'/%05d.jpg'%TIME[0],img)
    def plotCross(self,crossId,img):
        x, y = CROSSDICT[crossId].__mapLoc__()
        cv.circle(img,(x,y),self.crossRadius,color=self.crossColor,thickness=-1,lineType=-1)
        if crossId>=10:
            xx, yy = int(x - 4*self.crossRadius/5), int(y + self.crossRadius / 2)
        else:
            xx, yy = int(x- self.crossRadius/2), int(y + self.crossRadius / 2)
        cv.putText(img,str(crossId),(xx,yy ),cv.FONT_HERSHEY_SIMPLEX,0.6,[0,0,255],2)
    def plotRoad(self,roadId,img):
        # get road info
        road = ROADDICT[roadId]
        fromX, fromY = CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = CROSSDICT[road.__to__()].__mapLoc__()
        # plot line
        cv.line(img,(fromX, fromY),(toX, toY),color=self.roadColor,thickness=2)
        # plot bucket
        self.drawBucket(road,'forward',img)
        if road.__isDuplex__():
            self.drawBucket(road,'backward',img)
    def drawBucket(self,road,lane,img):
        bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__()
        channel = road.__channel__()
        fromX, fromY = CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = CROSSDICT[road.__to__()].__mapLoc__()
        XY, intervalXY, rectangleSize, channel2XY, length2XY = self.bucketDrawInitial(fromX,fromY,toX,toY,lane,length)
        for i in range(length):
            for j in range(channel):
                xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
                if bucket[i][j] == -1:
                    cv.rectangle(img,(int(XY[0]),int(XY[1])),(xRD,yRD),(0,0,0),1)
                else:
                    color = CARDICT[bucket[i][j]].__carColor__()
                    cv.rectangle(img, (int(XY[0]), int(XY[1])),(xRD, yRD),color=color,thickness=-1)
                XY[channel2XY] = XY[channel2XY] + intervalXY[channel2XY]
            XY[channel2XY] = XY[channel2XY] - intervalXY[channel2XY]*channel
            XY[length2XY] = XY[length2XY] + intervalXY[length2XY]
    def bucketDrawInitial(self,fromX,fromY,toX,toY,lane,length):
        direction = self.bucketDirection(fromX,fromY,toX,toY,lane)
        unitLength = (self.crossDistance - self.crossRadius * 4) / length
        if lane=='backward':
            toY=fromY
            toX=fromX
        if direction == 'north':
            XY = [fromX + self.channelDistance,toY + self.crossRadius * 2]
            intervalXY = self.channelDistance  + self.channelWidth , unitLength
            rectangleSize = self.channelWidth , unitLength
            channel2XY, length2XY = 0, 1
        elif direction == 'south':
            XY = [fromX - self.channelDistance - self.channelWidth,toY - self.crossRadius * 2 - unitLength]
            intervalXY = -(self.channelDistance  + self.channelWidth ), -unitLength
            rectangleSize = self.channelWidth , unitLength
            channel2XY, length2XY = 0, 1
        elif direction == 'east':
            XY = [toX - self.crossRadius * 2 - unitLength,fromY + self.channelDistance]
            intervalXY = -unitLength, self.channelDistance + self.channelWidth
            rectangleSize = unitLength, self.channelWidth
            channel2XY, length2XY = 1, 0
        elif direction == 'west':
            XY = [toX + self.crossRadius * 2, fromY - self.channelDistance - self.channelWidth]
            intervalXY = unitLength, -(self.channelDistance + self.channelWidth)
            rectangleSize = unitLength, self.channelWidth
            channel2XY, length2XY = 1, 0
        return XY,intervalXY,rectangleSize,channel2XY,length2XY
    def bucketDirection(self,fromX,fromY,toX,toY,lane):
        if fromY > toY:
            direction = 'north' if lane=='forward' else 'south'
        elif fromY < toY:
            direction = 'south' if lane == 'forward' else 'north'
        elif fromX < toX:
            direction = 'east' if lane == 'forward' else 'west'
        else:
            direction = 'west' if lane == 'forward' else 'east'
        return direction



def main():
    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    data_path = sys.argv[4]
    # ************************************* M A I N *******************************************#
    # load .txt files
    carInfo = open(car_path, 'r').read().split('\n')[1:]
    roadInfo = open(road_path, 'r').read().split('\n')[1:]
    crossInfo = open(cross_path, 'r').read().split('\n')[1:]
    dataInfo = open(data_path,'r').read().split('time:')
    #data格式，考虑道其他语言，data格式采用下方所示
    #forward指由 道路起点指向终点的方向
    #backward指由 道路终点指向起点的方向
    #time:n 注：time表示下一时刻到了
    #(roadId,forward/backward,[[车道0],[车道1],[车道2]])注：车道内从左到右，按离道路出口升序排列
    #exp:
    #time:10
    #(5001,forward,[[-1,-1,-1,10005],[-1,-1,10010,-1]])
    #(5001,backward,[[-1,-1,-1,10007],[-1,-1,10210,-1]])
    #   backward    [-1][-1][10210][-1]    大车道
    #    进车口     [-1][-1][-1][10007]    小车道
    #              ---------------------
    #     小车道    [10005][-1][-1][-1]    forward
    #     大车道    [-1][10010][-1][-1]    出车口
    # *****************************Create NameSpace And Dictionary*****************************#
    # create car objects
    # line = (id,from,to,speed,planTime)
    for line in carInfo:
        line = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        CARNAMESPACE.append(int(line[0]))
        CARDICT[int(line[0])] = CAR(int(line[0]))
    # create road objects
    # line = (id,length,speed,channel,from,to,isDuplex)
    for line in roadInfo:
        id_, length_, speed_, channel_, from_, to_, isDuplex_ = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ROADNAMESPACE.append(int(id_))
        ROADDICT[int(id_)] = ROAD(int(id_), int(length_), int(speed_), int(channel_), int(from_), int(to_),
                                  int(isDuplex_))
    # create cross objects
    # line = (id,north,east,south,west)
    for line in crossInfo:
        id_, north_, east_, south_, west_ = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        CROSSNAMESPACE.append(int(id_))
        CROSSDICT[int(id_)] = CROSS(int(id_), int(north_), int(east_), int(south_), int(west_))
    #************************************** Visualization ***************************************#
    visualize = visualization()
    visualize.crossLocGen()
    for dataOneTime in dataInfo[1:]:
        dataOneTime = dataOneTime.split('\n')
        TIME[0] = int(dataOneTime[0])
        print(TIME[0])
        for line in dataOneTime[1:]:
            if line.__len__()<3:
                break
            line=line[1:-1]
            firstComma = line.find(',')
            secondComma = line[line.find(',')+1:].find(',')+firstComma+1
            roadId = int(line[0:firstComma])
            which = line[firstComma+1:secondComma]
            cars =  eval(line[secondComma+1:])
            road = ROADDICT[roadId]
            if which=='forward':
                road.writeForward(cars)
            else:
                road.writeBackward(cars)
        visualize.drawMap()



if __name__  ==   "__main__":
    main()
# python visualization.py ../config_11/car.txt ../config_11/road.txt ../config_11/cross.txt ../config_11/viz_data
# python visualization.py ../config_12/car.txt ../config_12/road.txt ../config_12/cross.txt ../config_12/viz_data
