#-*- encoding=utf8 -*-
import sys
import numpy as np
import cv2 as cv

np.random.seed(951105)



TIME = [0]
CARDISTRIBUTION = [0,0,0]
CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE = [],[],[]
CROSSDICT,CARDICT,ROADDICT ={},{},{}




class CAR(object):
    def __init__(self,id_,from_,to_,speed_,planTime_):
        # **** statistic parameters ****#
        self.id_, self.from_, self.to_, self.speed_, self.planTime_ = id_, from_, to_, speed_, -1
        self.carColor = [int(value) for value in np.random.random_integers(0, 255, [3])]
        # **** dynamic parameters ****#
        self.state,self.x,self.y = 0,0,0
        self.presentRoad, self.nextCrossId = None,self.from_
        self.deltaX,self.deltaY=0,0
        self.wait = False
        self.route,self.routeIndex = None,None
    #
    # simulate initialization
    #
    def simulateInit(self,planTime,route):
        self.planTime_,self.route,self.routeIndex = planTime,route,0
    #
    # dynamic param update
    #
    def updateDynamic(self,state,x=None,y=None,presentRoad=None,roadSpeed=None,nextCrossId=None):
        # car not in carport of car is ready to go
        if self.state != 0 or presentRoad is not None:
            self.state = state
        if presentRoad is not None and self.state != 0 and self.routeIndex < self.route.__len__():
            self.routeIndex += 1
        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y
        self.presentRoad = presentRoad if presentRoad is not None else self.presentRoad
        if nextCrossId is not None:
            self.nextCrossId = nextCrossId
            toX, toY = CROSSDICT[self.to_].__loc__()
            nextCrossX, nextCrossY = CROSSDICT[nextCrossId].__loc__()
            self.deltaX, self.deltaY = toX - nextCrossX, toY - nextCrossY
    # show statistic parameters
    def __id__(self):
        return self.id_
    def __from__(self):
        return self.from_
    def __to__(self):
        return self.to_
    def __speed__(self):
        return  self.speed_
    def __planTime__(self):
        return self.planTime_
    def __carColor__(self):
        return self.carColor
    #
    # show dynamic parameters
    #
    def __state__(self):
        return self.state
    def __x__(self):
        return self.x
    def __y__(self):
        return self.y
    def __presentRoad__(self):
        return self.presentRoad
    def __nextCrossId__(self):
        return self.nextCrossId
    def __deltaX__(self):
        return self.deltaX
    def __deltaY__(self):
        return self.deltaY
    def __wait__(self):
        return self.wait
    def __route__(self):
        return self.route
    def __routeIndex__(self):
        return self.routeIndex
    #
    # show some important info
    #
    def __v__(self):
        return min(self.speed_,ROADDICT[self.presentRoad].__speed__())
    def __distance__(self):
        return abs(self.deltaX)+abs(self.deltaY)
    def __nextRoad__(self):
        try:
            return self.route[self.routeIndex]
        except:
            return -1

class ROAD(object):
    def __init__(self,id_, length_, speed_, channel_, from_, to_, isDuplex_):
        # **** statistic parameters ****#
        self.id_, self.length_, self.speed_, self.channel_, self.from_, self.to_, self.isDuplex_ = \
            id_, length_, speed_, channel_, from_, to_, isDuplex_
        self.carCapcity = self.channel_ * self.length_
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
    #
    # stepInitial
    #
    def stepInit(self):
        # dynamic param initialization
        self.fx, self.fy, self.bx, self.by = [0], [0], [0], [0]
        self.forwardDone, self.backwardDone = [False], [False]
        self.provideBucket, self.receiveBucket = None, None
        self.px, self.py, self.provideNum, self.receiveNum = None, None, None, None
        self.provideDone = None
        # car state initialization
        for i in range(self.length_):
            for j in range(self.channel_):
                if self.forwardBucket[i][j] is not None:
                    car = CARDICT[self.forwardBucket[i][j]]
                    car.updateDynamic(state=1)
                if self.isDuplex_:
                    if self.backwardBucket[i][j] is not None:
                        car = CARDICT[self.backwardBucket[i][j]]
                        car.updateDynamic(state=1)
        # first step
        for channel in range(self.channel_):
            self.moveInChannel(self.forwardBucket, channel)
            if self.isDuplex_:
                self.moveInChannel(self.backwardBucket, channel)
    #
    # function for bucket action
    #
    def moveInChannel(self,bucket,channel):
        # car state: 0,1,2,3 in carport,waiting,finishing,end
        # set guard
        previousCar, previousState = -1, 1
        for i in range(self.length_):
            if bucket[i][channel] is not None:
                car = CARDICT[bucket[i][channel]]
                v = car.__v__()
                if car.__state__() == 2:
                    previousCar, previousState = i, 2
                    continue
                elif i - v > previousCar:
                    bucket[i - v][channel] = bucket[i][channel]
                    bucket[i][channel] = None
                    previousCar, previousState = i - v, 2
                    car.updateDynamic(state=2, x=previousCar)
                elif previousState == 2:
                    if previousCar + 1 != i:
                        bucket[previousCar + 1][channel] = bucket[i][channel]
                        bucket[i][channel] = None
                    previousCar, previousState = previousCar + 1, 2
                    car.updateDynamic(state=2, x=previousCar)
                else:
                    previousCar, previousState = i, 1
    def findCar(self,st,end,channel,bucket):
        # find car backward
        for i in range(end, st, -1):
            if bucket[i][channel] is not None:
                return i
        return -1
    #
    # provide car
    #
    def firstPriorityCar(self):
        if self.provideBucket is None:
            print("Please do CAR.setBucket() first!")
        while True:
            if self.px[0] == self.length_:
                break
            carId = self.provideBucket[self.px[0]][self.py[0]]
            if carId is not None and CARDICT[carId].__state__() != 2:
                car = CARDICT[carId]
                left = car.__v__()
                # speed enough and no front car
                if left > self.px[0] and self.findCar(-1, self.px[0] - 1, self.py[0], self.provideBucket) == -1:
                    return self.provideBucket[self.px[0]][self.py[0]]
            if self.py[0] == self.channel_ - 1:
                self.px[0], self.py[0] = self.px[0] + 1, 0
            else:
                self.py[0] += 1
        self.provideDone[0] = True
        return -1
    def firstPriorityCarAct(self,action):
        if self.provideBucket is None:
            print("Please do CAR.setBucket() first!")
        if action == 0:
            self.provideBucket[self.px[0]][self.py[0]] = None
            self.provideNum[0] -= 1
        elif action == 1:
            carId = self.provideBucket[self.px[0]][self.py[0]]
            self.provideBucket[self.px[0]][self.py[0]] = None
            self.provideBucket[0][self.py[0]] = carId
        self.moveInChannel(self.provideBucket, self.py[0])
    #
    # receive car
    #
    def receiveCar(self,carId):
        if self.receiveBucket is None:
            print("Please do CAR.setBucket() first!")
        car = CARDICT[carId]
        leftX = min(self.speed_, car.__speed__()) - car.__x__()
        nextCrossId = self.from_ if car.__nextCrossId__() != self.from_ else self.to_
        if leftX <= 0:
            car.updateDynamic(state=2,x=0)
            return 1
        #find front car
        for i in range(self.channel_):
            frontCarLoc = self.findCar(self.length_ - leftX - 1, self.length_ - 1, i, self.receiveBucket)
            # if no front car
            if frontCarLoc == -1:
                self.receiveBucket[self.length_ - leftX][i] = carId
                self.receiveNum[0] += 1
                car.updateDynamic(state=2, x=self.length_ - leftX, y=i, presentRoad=self.id_, roadSpeed=self.speed_,
                           nextCrossId=nextCrossId)
                return 0
            frontCar = CARDICT[self.receiveBucket[frontCarLoc][i]]
            # if frontCar.state == waiting
            if frontCar.__state__() == 1:
                return 2
            # if frontCar.state == finish and frontCar.x != road.__length__()-1
            elif frontCarLoc != self.length_ - 1:
                self.receiveBucket[frontCarLoc + 1][i] = carId
                self.receiveNum[0] += 1
                car.updateDynamic(state=2, x=frontCarLoc + 1, y=i, presentRoad=self.id_, roadSpeed=self.speed_,
                           nextCrossId=nextCrossId)
                return 0
            # if frontCar.state == finish and frontCar.x == road.__length__()-1
            else:
                continue
        # if cars' state in all channel is equal to finish
        car.updateDynamic(state=2, x=0)
        return 1
    #
    # show statistic parameters
    #
    def __id__(self):
        return self.id_
    def __length__(self):
        return self.length_
    def __speed__(self):
        return self.speed_
    def __channel__(self):
        return self.channel_
    def __from__(self):
        return self.from_
    def __to__(self):
        return self.to_
    def __isDuplex__(self):
        return self.isDuplex_
    def __carCapcity__(self):
        return self.carCapcity
    #
    # show statistic parameters
    #
    def __forwardBucket__(self):
        return self.forwardBucket
    def __backwardBucket__(self):
        return self.backwardBucket
    def __fx__(self):
        return self.fx[0]
    def __fy__(self):
        return self.fy[0]
    def __bx__(self):
        return self.bx[0]
    def __by__(self):
        return self.by[0]
    def __forwardNum__(self):
        return self.forwardNum[0]
    def __backwardNum__(self):
        return self.backwardNum[0]
    def __forwardDone__(self):
        return self.forwardDone[0]
    def __backwardDone__(self):
        return self.backwardDone[0]
    def __provideBucket__(self):
        return self.provideBucket
    def __receiveBucket__(self):
        return self.receiveBucket
    def __px__(self):
        return self.px[0]
    def __py__(self):
        return self.py[0]
    def __provideNum__(self):
        return self.provideNum[0]
    def __receiveNum__(self):
        return self.receiveNum[0]
    def __provideDone__(self):
        return self.provideDone[0]

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
        self.provider = [[direction, self.roadIds[direction]] for direction in self.providerDirection]
        self.receiver = [self.roadIds[direction] for direction in self.receiverDirection]
        self.validRoad = [self.roadIds[direction] for direction in self.validRoadDirecction]
        self.provider.sort(key=takeSecond)
        self.providerDirection = [self.provider[i][0] for i in range(self.provider.__len__())]
        self.provider = [self.provider[i][1] for i in range(self.provider.__len__())]
        # **** dynamic parameters ****#
        self.readyCars = []
        self.carportCarNum = 0
        self.finishCarNum = 0
        # **** flag ****#
        self.done = False
        self.update = False
    # main functions
    def step(self):
        self.update = False
        for roadId in self.validRoad:
            ROADDICT[roadId].setBucket(self.id_)
        # data preapre
        nextCarId,nextCar,nextRoad,nextDirection =[],[],[],[]
        #
        # 0,1,2,3 denote north,east,south,west
        #
        for index in range(self.provider.__len__()):
            nextCarId.append(ROADDICT[self.provider[index]].firstPriorityCar())
            # if first priority car exists
            if nextCarId[index]!=-1:
                nextCar.append(CARDICT[nextCarId[index]])
                nextRoad.append(nextCar[index].__nextRoad__())
                # nextRoad == -1 => terminal
                if nextRoad[index]==-1:
                    nextDirection.append(2)
                else:
                    nextDirection.append(self.direction(self.provider[index],nextRoad[index]))
            else:
                nextCar.append(-1)
                nextRoad.append(-1)
                nextDirection.append(-1)
        # loop
        for presentRoadIndex in range(self.provider.__len__()):
            while nextCar[presentRoadIndex]!=-1:
                # same next road and high priority lead to conflict
                provider = ROADDICT[self.provider[presentRoadIndex]]
                for otherRoadIndex in range(self.provider.__len__()):
                    # conflict
                    # first priority car exists at road self.provider[otherRoadIndex]
                    if nextCar[otherRoadIndex]!=-1 and \
        self.isConflict(self.providerDirection[presentRoadIndex],nextDirection[presentRoadIndex],self.providerDirection[otherRoadIndex],nextDirection[otherRoadIndex]):
                        break
                if nextRoad[presentRoadIndex] == -1:
                    provider.firstPriorityCarAct(0)
                    CARDISTRIBUTION[1] -= 1
                    CARDISTRIBUTION[2] += 1
                    self.finishCarNum += 1
                    self.update = True
                else:
                    nextroad_ = ROADDICT[nextRoad[presentRoadIndex]]
                    action = nextroad_.receiveCar(nextCar[presentRoadIndex].__id__())
                    if action == 2:
                        break
                    self.update = True
                    provider.firstPriorityCarAct(action)
                nextCarId[presentRoadIndex] = provider.firstPriorityCar()
                if nextCarId[presentRoadIndex] != -1:
                    nextCar[presentRoadIndex] = CARDICT[nextCarId[presentRoadIndex]]
                    nextRoad[presentRoadIndex] = nextCar[presentRoadIndex].__nextRoad__()
                    # nextRoad == -1 => terminal
                    if nextRoad[presentRoadIndex] == -1:
                        nextDirection[presentRoadIndex] = 2
                    else:
                        nextDirection[presentRoadIndex]= self.direction(self.provider[presentRoadIndex], nextRoad[presentRoadIndex])
                else:
                    nextCar[presentRoadIndex] = -1
                    nextRoad[presentRoadIndex]= -1
                    nextDirection[presentRoadIndex] = -1
        done = True
        for fromA in range(self.provider.__len__()):
            if nextCar[fromA] != -1:
                done = False
        self.done = done
    def outOfCarport(self):
        self.readyCars = self.left
        self.left=[]
        if TIME[0] in self.carport.keys():
            self.carport[TIME[0]].sort()
            self.readyCars.extend(self.carport[TIME[0]])
        if self.readyCars.__len__() == 0:
            return
        #self.readyCars.sort()
        for roadId in self.receiver:
            ROADDICT[roadId].setBucket(self.id_)
        for i in range(self.readyCars.__len__()):
            carId = self.readyCars[i]
            roadId = CARDICT[carId].__nextRoad__()
            road = ROADDICT[roadId]
            if roadId not in self.receiver:
                print("Car(%d).Road(%d) not in cross(%d).function:class.outOfCarport"%(carId,roadId,self.id_))
            act = road.receiveCar(carId)
            if act!=0:
                self.left=self.readyCars[i:]
                break
            #assert act==0, print("Time(%d),Cross(%d),Road(%d),Car(%d) can't pull away from carport"%(TIME[0],self.id_,roadId,carId))
            self.carportCarNum -= 1
            CARDISTRIBUTION[0] -= 1
            CARDISTRIBUTION[1] += 1
    #
    # other functions
    #
    def isConflict(self,fromA,directionA,fromB,directionB):
        # -1,0,1,2,3,4,5 => guard_w,n,e,s,w,guard_n,guard_e
        # -1 ,1, 2 => right left, straight
        # reason why:
        # direction:-1,1,2
        # 0-1=-1=>3=>west,0+1=1=>east,0+2=>2=>south
        # 1-1=0=>north,1+2=2=>south,1+2=3=>west
        # and so...
        #       0
        #   3       1
        #       2
        #
        if (fromA + directionA)%4 == (fromB + directionB)%4 and directionA < directionB:
            return True
        else:
            return False
    def direction(self,providerId,receiverId):
        return self.directionMap[providerId][receiverId]
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
    def carportInitial(self, timePlan, carId):
        if timePlan not in self.carport.keys():
            self.carport[timePlan] = [carId]
        else:
            self.carport[timePlan].append(carId)
        self.carportCarNum += 1
    #
    # show statistic parameters
    #
    def __id__(self):
        return self.id_
    def __roadIds__(self):
        return self.roadIds
    def __providerDirection__(self):
        return self.providerDirection
    def __receiverDirection__(self):
        return self.receiverDirection
    def __validRoadDirection__(self):
        return self.validRoadDirection
    def __provider__(self):
        return self.provider
    def __receiver__(self):
        return self.receiver
    def __validRoad__(self):
        return self.validRoad
    def __x__(self):
        return self.x
    def __y__(self):
        return self.y
    def __mapX__(self):
        return self.mapX
    def __mapY__(self):
        return self.mapY
    def __done__(self):
        return self.done
    #
    # show dynamic parameters
    #
    def __carportCarNum__(self):
        return self.carportCarNum
    def __finishCarNum__(self):
        return self.finishCarNum
    def __update__(self):
        return self.update
    #
    # show some important info
    #
    def __loc__(self):
        return self.x,self.y
    def __mapLoc__(self):
        return self.mapX,self.mapY

class simulation(object):
    def __init__(self):
        self.dead = False
    def step(self):
        print("time:%d"%TIME[0])
        for crossId in CROSSNAMESPACE:
            CROSSDICT[crossId].setDone(False)
        print("pre-movement...")
        for road in ROADNAMESPACE:
            ROADDICT[road].stepInit()
        print("while loop...")
        unfinishedCross = CROSSNAMESPACE
        while unfinishedCross.__len__() > 0:
            self.dead = True
            nextCross = []
            for crossId in unfinishedCross:
                cross = CROSSDICT[crossId]
                cross.step()
                if not cross.__done__():
                    nextCross.append(crossId)
                if cross.__update__() or cross.__done__():
                    if TIME[0] == 55:
                        print(crossId,cross.__update__(),cross.__done__())
                    self.dead = False
            unfinishedCross = nextCross
            if TIME[0]==55:
                print(unfinishedCross)
            assert self.dead is False, print("dead lock in", unfinishedCross)
        print("car pulling away from carport")
        for i in range(CROSSNAMESPACE.__len__()):
            crossId = CROSSNAMESPACE[i]
            for roadId in CROSSDICT[crossId].__validRoad__():
                ROADDICT[roadId].setBucket(crossId)
            CROSSDICT[crossId].outOfCarport()
    def simulate(self):
        visualize = visualization()
        visualize.crossLocGen()
        while True:
            self.step()
            #visualize.drawMap()
            if CARDISTRIBUTION[2]==CARNAMESPACE.__len__():
                print(CARDISTRIBUTION[2])
                break
            if self.dead:
                break
            TIME[0] +=1

class visualization(object):
    def __init__(self):
        self.maxX,self.maxY = 0,0
        self.savePath = '../../../simulatePictures'
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
        # plot info
        self.plotInfo(img)
        cv.imwrite(self.savePath+'/%d.jpg'%TIME[0],img)
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
                if bucket[i][j] is  None:
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
    def plotInfo(self,img):
        for crossId in CROSSNAMESPACE:
            cross = CROSSDICT[crossId]
            x,y = cross.__mapLoc__()
            cn,fn = cross.__carportCarNum__(),cross.__finishCarNum__()
            cv.putText(img,"%d,%d"%(cn,fn),(int(x),int(y-1.1*self.crossRadius)),\
                       cv.FONT_HERSHEY_SIMPLEX,0.4,[0,0,255],1)
        cv.putText(img, "in the carport:%d,on the road:%d,end of the trip:%d" % (CARDISTRIBUTION[0],CARDISTRIBUTION[1],CARDISTRIBUTION[2]),(30,30), \
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, [0, 0, 255], 2)

def takeSecond(elem):
    return elem[1]


def main():
    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]
    # ************************************* M A I N *******************************************#
    # load .txt files
    carInfo = open(car_path, 'r').read().split('\n')[1:]
    roadInfo = open(road_path, 'r').read().split('\n')[1:]
    crossInfo = open(cross_path, 'r').read().split('\n')[1:]
    answerInfo = open(answer_path,'r').read().split('\n')
    # *****************************Create NameSpace And Dictionary*****************************#
    # create car objects
    # line = (id,from,to,speed,planTime)
    for line in carInfo:
        id_, from_, to_, speed_, planTime_ = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        CARNAMESPACE.append(int(id_))
        CARDICT[int(id_)] = CAR(int(id_), int(from_), int(to_), int(speed_), int(planTime_))
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
    # car route initialize
    # line = (id,startTime,route)
    count = 0
    for i,line in enumerate(answerInfo):
        if line.strip() =='':
            break
        line=line.strip()[1:-1].split(',')
        carId = int(line[0])
        planTime_ = int(line[1])
        route = [int(roadId) for roadId in  line[2:]]
        CARDICT[carId].simulateInit(planTime_,route)
        count+=1
    print("There are %d cars' route preinstalled"%count)
    CARDISTRIBUTION[0] = CARNAMESPACE.__len__()
    # **** cross initialization ****#
    for carId in CARNAMESPACE:
        CROSSDICT[CARDICT[carId].__from__()].carportInitial(CARDICT[carId].__planTime__(), carId)
    # ****Initialization ****#
    CARNAMESPACE.sort()
    CROSSNAMESPACE.sort()
    # simulator
    simulate = simulation()
    simulate.simulate()



if __name__  ==   "__main__":
    main()



# python simulator.py ../config_11/car.txt ../config_11/road.txt ../config_11/cross.txt ../config_11/answer.txt
# python simulator.py ../config_12/car.txt ../config_12/road.txt ../config_12/cross.txt ../config_12/answer.txt
