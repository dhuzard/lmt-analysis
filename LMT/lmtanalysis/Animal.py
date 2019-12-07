'''
Created on 7 sept. 2017

@author: Fab
'''

#aNIAMLS DE PD

#GES
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import numpy as np
import math
from lxml import etree

from mpl_toolkits.mplot3d import *
import matplotlib.ticker
import time
from statistics import *
from scipy.ndimage.measurements import standard_deviation
from statistics import mean

from lmtanalysis.Event import EventTimeLine

from lmtanalysis.Point import Point
from lmtanalysis.Mask import Mask
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import *
from lmtanalysis.Detection import *

# matplotlib fix for mac
# matplotlib.use('TkAgg')
# The backend... is it the reason why my figures freeze ? => Solved with plt.show(block=true)


idAnimalColor = [None, "red", "green", "blue", "orange"]


def getAnimalColor(animalId):
    return idAnimalColor[animalId]


class Animal:

    def __init__(self, baseId, RFID, name=None, genotype=None, user1=None, conn=None):
        self.baseId = baseId
        self.RFID = RFID
        self.name = name
        self.genotype = genotype
        self.user1 = user1
        self.conn = conn
        self.detectionDictionnary = {}

    def __str__(self):
        return "Animal Id:{id} Name:{name} RFID:{rfid} Genotype:{genotype} User1:{user1}" \
            .format(id=self.baseId, rfid=self.RFID, name=self.name, genotype=self.genotype, user1=self.user1)

    def getColor(self):
        return getAnimalColor(self.baseId)

    def loadDetection(self, start=None, end=None, lightLoad=False):
        """
        lightLoad only loads massX and massY to speed up the load.
        Then one can only compute basic features such as global speed of the animals.
        """
        print(self.__str__(), ": Loading detection.")
        chrono = Chronometer("Load detection")

        self.detectionDictionnary.clear()

        cursor = self.conn.cursor()
        query = ""
        if lightLoad is True:
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y FROM DETECTION WHERE ANIMALID={}".format(self.baseId)
        else:
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y, MASS_Z, FRONT_X, FRONT_Y, FRONT_Z, BACK_X, BACK_Y, BACK_Z," \
                    "REARING,LOOK_UP,LOOK_DOWN FROM DETECTION WHERE ANIMALID={}".format(self.baseId)

        if start is not None:
            query += " AND FRAMENUMBER>={}".format(start)

        if end is not None:
            query += " AND FRAMENUMBER<={}".format(end)

        print(query)
        cursor.execute(query)

        rows = cursor.fetchall()
        cursor.close()

        for row in rows:
            frameNumber = row[0]
            massX = row[1]
            massY = row[2]

            # filter detection at 0

            if massX < 10:
                continue

            if not lightLoad:
                massZ = row[3]

                frontX = row[4]
                frontY = row[5]
                frontZ = row[6]

                backX = row[7]
                backY = row[8]
                backZ = row[9]

                rearing = row[10]
                lookUp = row[11]
                lookDown = row[12]

                detection = Detection(massX, massY, massZ,
                                      frontX, frontY, frontZ,
                                      backX, backY, backZ,
                                      rearing, lookUp, lookDown)
            else:
                detection = Detection(massX, massY)

            self.detectionDictionnary[frameNumber] = detection

        print(self.__str__(), " ", len(self.detectionDictionnary),
              " detections loaded in {} seconds.".format(chrono.getTimeInS()))

    def getNumberOfDetection(self, tmin, tmax):
        return len(self.detectionDictionnary.keys())

    def filterDetectionByInstantSpeed(self, minSpeed, maxSpeed):
        """
        Removes (.pop()) from dictionary the detections out of speed range specified
        Speed function in LMT use t-1 and t+1 detection to provide a result.
        Here we remove spurious tracking jump, so we check on t to t+1 frame.
        Speed is expressed in cm/s.
        """
        nbRemoved = 0

        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get(key)
            b = self.detectionDictionnary.get(key + 1)

            if a is None or b is None:
                continue

            speed = math.hypot(a.massX - b.massX, a.massY - b.massY) * scaleFactor / (1 / 30)

            if speed > maxSpeed or speed < minSpeed:
                self.detectionDictionnary.pop(key)
                nbRemoved += 1

        print("Filtering Instant speed min:", minSpeed, "max:", maxSpeed, ". Number of detection removed:", nbRemoved)

    def filterDetectionByArea(self, x1, y1, x2, y2):
        """
        Filters the detection in the cage (using centimeter, starting from the top left of the cage).
        The scaleFactor (cm => pixel) = 10/57 (in measures.py) => 1 pixel = 0.175 cm
        """
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get(key)

            if a is None:
                continue

            x = (a.massX - cornerCoordinates50x50Area[0][0]) * scaleFactor  # X coordinate from top-left corner (114)
            y = (a.massY - cornerCoordinates50x50Area[0][1]) * scaleFactor  # Y coordinate from top-left corner (63)

            if x < x1 or x > x2 or y < y1 or y > y2:  # Checks that (X,Y) coordinates are within the zone
                self.detectionDictionnary.pop(key)
                nbRemoved += 1
        print("Filtering area, number of detection removed:", nbRemoved)

    def filterDetectionByEventTimeLine(self, eventTimeLine):
        """
        Filters detection using an event.
        It keeps only what matches the specified event.
        """
        eventDic = eventTimeLine.getDictionnary()
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get(key)

            if a is None:
                continue

            if not (key in eventDic):
                self.detectionDictionnary.pop(key)
                nbRemoved += 1

        print("Filtering area, number of detection removed:", nbRemoved)

    def clearDetection(self):
        self.detectionDictionnary.clear()

    def getMaxDetectionT(self):
        """
        Returns the timepoint of the last detection.
        """

        if len(self.detectionDictionnary.keys()) == 0:
            return None

        return sorted(self.detectionDictionnary.keys())[-1]

    def getTrajectoryData(self, maskingEventTimeLine=None):
        keyList = sorted(self.detectionDictionnary.keys())

        if maskingEventTimeLine is not None:
            keyList = maskingEventTimeLine.getDictionnary()

        xList = []
        yList = []

        previousKey = 0

        for key in keyList:
            # print("key:", key, ", Speed value:", self.getSpeed(key), ", previous key:", previousKey)

            if previousKey + 1 != key:
                xList.append([np.nan, np.nan])
                yList.append([np.nan, np.nan])
                previousKey = key

                # print("break previous")
                continue

            previousKey = key
            a = self.detectionDictionnary.get(key)
            if a is None:
                xList.append([np.nan, np.nan])
                yList.append([np.nan, np.nan])
                # print("break none A")
                continue

            b = self.detectionDictionnary.get(key + 1)
            if b is None:
                xList.append([np.nan, np.nan])
                yList.append([np.nan, np.nan])
                # print("break none B")
                continue

            xList.append([a.massX, b.massX])
            yList.append([-a.massY, -b.massY])

        return xList, yList

    def plotTrajectory(self, show=True, color='k', maskingEventTimeLine=None, title=""):
        """ Plot the trajectory of an animal """
        print("Plot trajectory of 1 animal:")
        print("Plotting the trajectory of animal " + self.name)

        # plt.ioff()

        xList, yList = self.getTrajectoryData(maskingEventTimeLine)

        plt.figure()
        print(xList)
        print(yList)

        plt.plot(xList, yList, color=color, linestyle='-', linewidth=1, alpha=0.5, label=self.name)
        plt.title(title + self.RFID)
        plt.xlim(90, 420)
        plt.ylim(-370, -40)

        # plt.draw()
        # plt.pause(1)

        if show:
            plt.show(block=True)

    def plotTrajectory3D(self):
        """ Plot 3D trajectory of an animal """

        print("Plot the 3D trajectory")
        keyList = sorted(self.detectionDictionnary.keys())

        mpl.rcParams['legend.fontsize'] = 10

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)

        z = np.linspace(-2, 2, 100)
        r = z ** 2 + 1
        x = r * np.sin(theta)
        y = r * np.cos(theta)

        '''
        print ( z )
        print ( r )
        print ( x )
        print ( y )
        '''

        xList = []
        yList = []
        zList = []

        for key in keyList:
            a = self.detectionDictionnary.get(key)
            b = self.detectionDictionnary.get(key + 1)
            if b is None:
                continue

            xList.append(a.massX)
            yList.append(a.massY)
            zList.append(a.massZ)

        ax.plot(xList, yList, zList, label="3D Trajectory of " + self.RFID)
        ax.legend()

        # plt.draw()
        # plt.pause(2)

        plt.show(block=True)

    def getDistance(self, tmin=0, tmax=None):
        """
        Returns the distance traveled by the animal (in cm).
        """

        print("Compute total distance between min:{} and max:{} ".format(tmin, tmax))
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        totalDistance = 0
        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            b = self.detectionDictionnary.get(key + 1)

            if b is None:
                continue

            if math.hypot(a.massX - b.massX, a.massY - b.massY) > 85.5:
                # if the distance calculated between two frames is too large, discarded
                # Dax: WHY 85.5 ??
                continue

            totalDistance += math.hypot(a.massX - b.massX, a.massY - b.massY)
        totalDistance *= scaleFactor

        return totalDistance

    def getDistancePerBin(self, binFrameSize, minFrame=0, maxFrame=None):
        if maxFrame is None:
            maxFrame = self.getMaxDetectionT()

        distanceList = []
        t = minFrame

        while t < maxFrame:
            distanceBin = self.getDistance(t, t + binFrameSize)
            print("Distance bin n:{} value:{}".format(t, distanceBin))
            distanceList.append(distanceBin)
            t += binFrameSize

        return distanceList

    def getOrientationVector(self, t):
        """
        Returns the vector of orientation of the animal.
        A vector is a Point(deltaX, deltaY).
        """
        d = self.detectionDictionnary.get(t)

        if d is None:
            return None

        if d.frontX is None:
            return None

        if d.backX is None:
            return None

        deltaX = d.frontX - d.backX
        deltaY = d.frontY - d.backY
        p = Point(deltaX, deltaY)
        return p

    def getSpeedVector(self, t):
        """ Returns the Speed vector at time t """
        a = self.detectionDictionnary.get(t - 1)
        b = self.detectionDictionnary.get(t + 1)

        if a is None or b is None:
            return None

        speedVectorX = a.massX - b.massX
        speedVectorY = a.massY - b.massY

        p = Point(speedVectorX, speedVectorY)
        return p

    def getFrontSpeed(self, t):
        """ Returns the Speed of the head """
        a = self.detectionDictionnary.get(t - 1)
        b = self.detectionDictionnary.get(t + 1)

        if a is None or b is None:
            return None

        speedVectorX = a.frontX - b.frontX
        speedVectorY = a.frontY - b.frontY

        p = Point(speedVectorX, speedVectorY)
        return p

    def getBackSpeed(self, t):
        """ Returns the Speed of the tail base """
        a = self.detectionDictionnary.get(t - 1)
        b = self.detectionDictionnary.get(t + 1)

        if a is None or b is None:
            return None

        speedVectorX = a.backX - b.backX
        speedVectorY = a.backY - b.backY

        p = Point(speedVectorX, speedVectorY)
        return p

    def getDistanceSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        """ Returns the distance of an animal to a specified zone, within a time bin """
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        distance = 0

        for key in keyList:
            if key <= tmin or key >= tmax:
                # print(1)
                continue

            a = self.detectionDictionnary.get(key)
            b = self.detectionDictionnary.get(key + 1)

            if b is None:
                continue

            if a.massX < xa or a.massX > xb or a.massY < ya or a.massY > yb or b.massX < xa or b.massX > xb or \
                    b.massY < ya or b.massY > yb:
                # print(2)
                continue

            if math.hypot(a.massX - b.massX, a.massY - b.massY) > 85.5:
                # if the distance calculated between two frames is too large, discard
                # Dax Why using 85.5 as limit distance ? => define it in Measure.py ?!
                continue

            distance += math.hypot(a.massX - b.massX, a.massY - b.massY)

        distance *= scaleFactor
        return distance

    def getDistanceTo(self, t, animalB):
        """
        Determines the distance between the focal animal and another one at a specified time point t.
        It checks first that both animals are detected at the time point t.
        """
        distanceTo = None

        if not (t in animalB.detectionDictionnary):
            return None

        if not (t in self.detectionDictionnary):
            return None

        if animalB.detectionDictionnary[t].massX is None:
            return None

        if math.hypot(self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX,
                      self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY) > 71 * 57 / 10:
            # If the distance calculated between the two individuals is too large, discard
            # 71*57/10 = 404.7 => Why using This ??
            # Dax: Why not using MAX_DISTANCE_THRESHOLD as in getDistanceToPoint ??
            return None

        else:
            distanceTo = math.hypot(self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX,
                                    self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY)
            return distanceTo

    def getDistanceToPoint(self, t, xPoint, yPoint):
        """
        Determines the distance between the focal animal and a specific point in the arena at a specified time point t.
        """
        distanceToPoint = None

        if not (t in self.detectionDictionnary):
            return None

        if math.hypot(self.detectionDictionnary[t].massX - xPoint,
                      self.detectionDictionnary[t].massY - yPoint) > MAX_DISTANCE_THRESHOLD:
            # if the distance calculated is too large, discard
            return None

        else:
            distanceToPoint = math.hypot(self.detectionDictionnary[t].massX - xPoint,
                                         self.detectionDictionnary[t].massY - yPoint)
            return distanceToPoint

    def getMeanBodyLength(self, tmin=0, tmax=None):
        """
        Returns the mean body length of the animal within the time window specified
        """
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        if tmax is None:  # If the previous self.getMaxDetectionT()= None
            self.meanBodyLength = None
            return self.meanBodyLength
        # Dax: Is it the same to directly return None ?
        # Dax: Where does the meanBodyLength comes from?

        bodySizeList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            bodySizeList.append(a.getBodySize())

        mean = np.nanmean(bodySizeList)
        print("Mean animal body length: ", mean)

        self.meanBodyLength = mean
        # Dax: Define this in _init_ first ?
        # Dax: Or Why defining a meanBodyLength? We could just "return mean" ?

        return self.meanBodyLength

    """ Previous functions from Fabrice return bodyThreshold and medianBodyHeight in Self
    I remove bodyThreshold from self, it just return bodyThreshold 
    
    def getBodyThreshold(self, tmin=0, tmax=None):
        keyList = sorted(self.detectionDictionnary.keys())
        
        if tmax is None:
            tmax = self.getMaxDetectionT()
    
        bodySizeList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            bodySizeList.append(a.getBodySize())
            
        #verifier si ce calcul tourne bien:
        threshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)
        
        self.bodyThreshold = threshold
        
        return self.bodyThreshold
        
    
    def getMedianBodyHeight (self, tmin=0, tmax=None): 
        keyList = sorted(self.detectionDictionary.keys())
        
        if tmax is None:
            tmax = self.getMaxDetectionT()

        bodyHeightList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionary.get(key)
            bodyHeightList.append(a.massZ)
            
        self.medianBodyHeight = np.median(np.array(bodyHeightList))
        
        return self.medianBodyHeight

    """

    def getBodyThreshold(self, tmin=0, tmax=None):
        """
        Determine the body size threshold used to determine SAP (Stretch attend postures)
        """

        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        bodySizeList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            bodySizeList.append(a.getBodySize())

        # verifier si ce calcul tourne bien:
        # Dax: ???
        threshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)
        return threshold

    def getBodyThresholdLowSpeed(self, tmin=0, tmax=None):
        """ (Dax)
        Determine the body size threshold used to determine SAP (Stretch attend postures)
        Dax: This one computes the body size when the animal is walking between SPEED_THRESHOLD_LOW and
        SPEED_THRESHOLD_HIGH
        """

        # Filters data depending on the speed
        print("Filter speed within getBodyThresholdLowSpeed():")
        self.filterDetectionByInstantSpeed(SPEED_THRESHOLD_LOW, SPEED_THRESHOLD_HIGH)

        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        bodySizeList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            bodySizeList.append(a.getBodySize())

        # verifier si ce calcul tourne bien:
        # Dax: ???
        threshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)

        return threshold

    def getMedianBodyHeight(self, tmin=0, tmax=None):
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        bodyHeightList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            bodyHeightList.append(a.massZ)

        medianBodyHeight = np.median(np.array(bodyHeightList))

        return medianBodyHeight

    def getMeasures(self, tmin=0, tmax=None, speedmin=SPEED_THRESHOLD_LOW, speedmax=SPEED_THRESHOLD_HIGH):
        """
        Dax: it returns the different measures of the animal
        for different speeds
        """

        if tmax is None:
            tmax = self.getMaxDetectionT()

        print("Filtering speed (", speedmin, "-", speedmax, "):")
        self.filterDetectionByInstantSpeed(speedmin, speedmax)
        keyList = sorted(self.detectionDictionnary.keys())

        bodySizeList = []
        detection = []
        massZHeightList = []
        frontZList = []
        bodySlopeList = []
        rearingList = []
        rearingZList = []
        bodyThreshold = []
        thresholdMassHeight = []
        speed = []
        verticalSpeed = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            a = self.detectionDictionnary.get(key)
            detection.append(a)
            bodySizeList.append(a.getBodySize())
            massZHeightList.append(a.massZ)
            # massZHeightList = [x for x in massZHeightList if x != 0.0]  # Removes the 0 from the list
            frontZList.append(a.frontZ)
            # massZHeightList = [x for x in massZHeightList if x != 0.0]  # Removes the 0 from the list
            bodySlopeList.append(a.getBodySlope())
            rearingList.append(a.isRearing())
            rearingZList.append(a.isRearingZ())
            speed.append(self.getSpeed(key))
            verticalSpeed.append(self.getVerticalSpeed(key))

        # Computing means, medians, min and max for each measure
        # bodySizeList = [x for x in bodySizeList if x != 0.0]  # Removes the 0 from the list
        minBodySize = np.nanmin(np.array(bodySizeList))
        meanBodySize = np.nanmean(np.array(bodySizeList))
        medianBodySize = np.nanmedian(np.array(bodySizeList))
        maxBodySize = np.nanmax(np.array(bodySizeList))

        minBodyHeight = np.nanmin(np.array(massZHeightList))
        meanBodyHeight = np.nanmean(np.array(massZHeightList))
        medianBodyHeight = np.nanmedian(np.array(massZHeightList))
        maxBodyHeight = np.nanmax(np.array(massZHeightList))

        minBodySlope = np.nanmin(np.array(list(filter(None, bodySlopeList))))
        meanBodySlope = np.nanmean(np.array(list(filter(None, bodySlopeList))))
        medianBodySlope = np.nanmedian(np.array(list(filter(None, bodySlopeList))))
        maxBodySlope = np.nanmax(np.array(list(filter(None, bodySlopeList))))

        minFrontZ = np.nanmin(np.array(frontZList))
        meanFrontZ = np.nanmedian(np.array(frontZList))
        medianFrontZ = np.nanmedian(np.array(frontZList))
        maxFrontZ = np.nanmax(np.array(frontZList))

        minSpeed = np.nanmin(np.array(np.array(list(filter(None, speed)))))
        meanSpeed = np.nanmean(np.array(np.array(list(filter(None, speed)))))
        medianSpeed = np.nanmedian(np.array(np.array(list(filter(None, speed)))))
        maxSpeed = np.nanmax(np.array(np.array(list(filter(None, speed)))))

        minVerticalSpeed = np.nanmin(np.array((list(filter(None, verticalSpeed)))))
        meanVerticalSpeed = np.nanmean(np.array((list(filter(None, verticalSpeed)))))
        medianVerticalSpeed = np.nanmedian(np.array((list(filter(None, verticalSpeed)))))
        maxVerticalSpeed = np.nanmax(np.array((list(filter(None, verticalSpeed)))))

        minBodyThreshold = np.nanmin(bodySizeList) + np.nanstd(bodySizeList)
        meanBodyThreshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)
        medianBodyThreshold = np.nanmedian(bodySizeList) + np.nanstd(bodySizeList)
        maxBodyThreshold = np.nanmax(bodySizeList) + np.nanstd(bodySizeList)

        decile = 7 * len(massZHeightList) / 10
        massHeightThreshold = sorted(massZHeightList)[math.ceil(decile) - 1]

        numberOfDetections = self.getNumberOfDetection(tmin, tmax)

        listOfNames = ["minBodySize", "meanBodySize", "medianBodySize", "minBodySize", "meanBodyHeight", "medianBodyHeight", "meanBodySlope",
                       "medianBodySlope", "meanFrontZ", "meanSpeed", "medianSpeed", "meanVerticalSpeed",
                       "medianVerticalSpeed", "bodyThreshold", "massHeightThreshold", "numberOfDetections"]
        listOfMeasures = [minBodySize, meanBodySize, medianBodySize, maxBodySize,
                          minBodyHeight, meanBodyHeight, medianBodyHeight, maxBodyHeight,
                          minBodySlope, meanBodySlope, medianBodySlope, maxBodySlope,
                          minFrontZ, meanFrontZ, medianFrontZ, maxFrontZ,
                          minSpeed, meanSpeed, medianSpeed, maxSpeed,
                          minVerticalSpeed, meanVerticalSpeed, medianVerticalSpeed, maxVerticalSpeed,
                          minBodyThreshold, meanBodyThreshold, medianBodyThreshold, maxBodyThreshold,
                          massHeightThreshold,
                          numberOfDetections
                          ]

        return listOfMeasures

    def getThresholdMassHeight(self, tmin=0, tmax=None):
        """
        Determine the body size height threshold used to determine whether the animal is rearing or not.
        Here, we use the 7th decile.
        """
        # Dax: Why 7th decile? From publications on mice movements?

        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        massHeightList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue

            a = self.detectionDictionnary.get(key)
            massHeightList.append(a.massZ)

        decile = 7 * len(massHeightList) / 10
        # print("7th decile of the Mass:")
        # print(decile)
        # print("arrondi massZ:")
        # print(math.ceil(decile)-1)

        self.eightDecileMassHeight = sorted(massHeightList)[math.ceil(decile) - 1]

        return self.eightDecileMassHeight

    def getThresholdFrontHeight(self, tmin=0, tmax=None):
        """
        determine the body size height threshold used to determine whether the animal is rearing or not
        here we use the 7th decile
        """
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        frontHeightList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue

            a = self.detectionDictionnary.get(key)
            frontHeightList.append(a.frontZ)

        decile = 7 * len(frontHeightList) / 10
        print("7th decile of the Front:")
        print(decile)
        print("arrondi frontZ:")
        print(math.ceil(decile) - 1)

        self.eightDecileFrontHeight = sorted(frontHeightList)[math.ceil(decile) - 1]

        return self.eightDecileFrontHeight

    def getDirection(self, t):
        """
        Determines the direction of the animal using the head and the mass center
        """
        a = self.detectionDictionnary.get(t)
        return a.getDirection();

    def getSpeed(self, t):
        """
        Calculates the instantaneous speed of the animal at each frame 't'
        """
        a = self.detectionDictionnary.get(t - 1)
        b = self.detectionDictionnary.get(t + 1)

        if b is None or a is None:
            return None

        speed = math.hypot(a.massX - b.massX, a.massY - b.massY) * scaleFactor / (2 / 30)
        return speed

    def getVerticalSpeed(self, t):
        """
        calculate the instantaneous vertical speed of the mass center of the animal at each frame
        """
        a = self.detectionDictionnary.get(t - 1)
        b = self.detectionDictionnary.get(t + 1)

        if b is None or a is None:
            return None

        verticalSpeed = (b.massZ - a.massZ) / 2
        return verticalSpeed

    """ PREVIOUS VERSION FROM FABRICE (With bodyThreshold in Self!)
    I removed bodyThreshold from Self and use a local variable "bodyThreshold"
    def getSap(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):

        print("Compute number of frames in SAP in specific zone of the cage")
    
        self.getBodyThreshold()
        self.getMedianBodyHeight()
    
        #TODO: pas mettre body threshold en self car c'est pas la peine.
    
        keyList = sorted(self.detectionDictionnary.keys())
    
        if tmax is None:
            tmax = self.getMaxDetectionT()
    
        sapList = []
        
        for key in keyList:
            if key <= tmin or key >= tmax:
                #print(1)
                continue
            
            detection = self.detectionDictionnary.get(key)
            if detection.massX < xa or detection.massX > xb or detection.massY < ya \
                    or detection.massY > yb or detection.massZ > self.medianBodyHeight:
                #print(2)
                continue
    
            speed = self.getSpeed(key)
            if speed is None:
                #print(3)
                continue
    
            if detection.getBodySize() >= self.bodyThreshold and speed < SPEED_THRESHOLD_LOW \
                    and detection.massZ < self.medianBodyHeight:
                #print(4)
                sapList.append(detection)

        return sapList    
    """

    def getSap(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        """
        Determines the SAP (Stretch Attend Postures)
        Can specify, the timebin (tmin, tmax) and a specific zone (xa, xb, ya, yb)
        (Reminder for zones: Start (0,0) is top left corner.
        """

        print("Compute number of frames in SAP in specific zone of the cage")

        bodyThreshold = self.getBodyThreshold()
        medianBodyHeight = self.getMedianBodyHeight()

        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        sapList = []

        for key in keyList:
            if key <= tmin or key >= tmax:
                # print(1)
                continue

            detection = self.detectionDictionnary.get(key)
            # Check that animal is in the specified zones and not rearing
            if detection.massX < xa or detection.massX > xb or detection.massY < ya \
                    or detection.massY > yb or detection.massZ > medianBodyHeight:
                # print(2)
                continue

            # Dax: Why?? Checks that speed is not None
            speed = self.getSpeed(key)
            if speed is None:
                # print(3)
                continue

            # SAP when; body elongation, low speed and body close to floor
            if detection.getBodySize() >= bodyThreshold and speed < SPEED_THRESHOLD_LOW \
                    and detection.massZ < medianBodyHeight:
                # print(4)
                sapList.append(detection)

        return sapList

    def getSapDictionnary(self, tmin=0, tmax=None):
        """
        Creates a dictionnary with all the SAP events between tmin and tmax
        """
        bodyThreshold = self.getBodyThreshold()
        medianBodyHeight = self.getMedianBodyHeight()

        keyList = sorted(self.detectionDictionnary.keys())
        # Dax: Why is keyList, a list of times?

        if tmax is None:  # if no tmax enterer, tmax set to the last time point of the detection
            tmax = self.getMaxDetectionT()

        sapDictionnary = {}

        for key in keyList:
            if key <= tmin or key >= tmax:  # to be in the good time-window
                continue

            detection = self.detectionDictionnary.get(key)
            speed = self.getSpeed(key)

            if speed is None:
                continue

            if detection.getBodySize() >= bodyThreshold and speed < SPEED_THRESHOLD_LOW \
                    and detection.massZ < medianBodyHeight:
                """ 
                  Tests if the body size of the animal is bigger than its 'Threshold'
                    AND if speed is lower than 5cm/s
                    AND if the Z of center of mass is lower than the median body Height (low position)
                """
                sapDictionnary[key] = True

        return sapDictionnary

    def getCountFramesSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        """
        coordinates are in pixel
        """
        keyList = sorted(self.detectionDictionnary.keys())

        if tmax is None:
            tmax = self.getMaxDetectionT()

        count = 0

        for key in keyList:
            if key <= tmin or key >= tmax:
                continue
            detection = self.detectionDictionnary.get(key)
            if detection.massX < xa or detection.massX > xb or detection.massY < ya or detection.massY > yb:
                continue
            count += 1

        return count

    def plotDistance(self, color='k', show=True):
        print("Plot distance")
        keyList = sorted(self.detectionDictionnary.keys())

        tList = []
        distanceList = []

        totalDistance = 0
        for key in keyList:

            a = self.detectionDictionnary.get(key)
            b = self.detectionDictionnary.get(key + 1)

            if b is None:
                continue

            totalDistance += math.hypot(a.massX - b.massX, a.massY - b.massY)

            tList.append(key / 30 / 60)
            distanceList.append(totalDistance)

        # fig,ax = plt.subplots()
        plt.plot(tList, distanceList, color=color, linestyle='-', linewidth=2,
                 label="Cumulated distance of " + self.__str__())

        # formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm%Ss', time.gmtime(frame // 30)))
        # formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm', time.gmtime(frame // 30)))
        # ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(30*60))
        # ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(30*60*10))

        plt.legend()

        if show:
            plt.show(block=True)

    def getBinaryDetectionMask(self, t):
        """
        Returns the mask (shape of the animal) of a detection at a given T.
        """
        query = "SELECT DATA FROM DETECTION WHERE ANIMALID={} AND FRAMENUMBER={}".format(self.baseId, t)

        print("TEST")

        print(query)
        cursor = self.conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()
        cursor.close()

        if len(rows) != 1:
            print("unexpected number of row: ", str(len(rows)))
            return None

        row = rows[0]
        data = row[0]

        # print(data)

        x = 0
        y = 0
        w = 0
        h = 0
        boolMaskData = None

        tree = etree.fromstring(data)
        for user in tree.xpath("/root/ROI/boundsX"):
            x = int(user.text)
        for user in tree.xpath("/root/ROI/boundsY"):
            y = int(user.text)
        for user in tree.xpath("/root/ROI/boundsW"):
            w = int(user.text)
        for user in tree.xpath("/root/ROI/boundsH"):
            h = int(user.text)
        for user in tree.xpath("/root/ROI/boolMaskData"):
            boolMaskData = user.text

        mask = Mask(x, y, w, h, boolMaskData, self.getColor())

        '''
        <boundsX>119</boundsX><boundsY>248</boundsY><boundsW>37</boundsW><boundsH>29</boundsH>
        <boolMaskData>78:5e:bd:d3:4b:e:c0:20:8:4:d0:e9:fd:2f:dd:a0:56:11:87:cf:a2:91:a5:be:c:24:22:c0:ea:91:62:17:eb:ac:91:84:4d:13:84:29:e3:aa:cd:70:65:8:1b:8c:90:83:39:66:eb:59:30:2e:51:41:17:cc:7c:c2:a0:d7:9a:a8:82:42:33:da:e5:26:16:63:a2:3f:50:5f:d7:24:a9:82:be:bd:77:a3:a0:be:b:45:f6:37:11:64:9:60:d0:9:e4:44:23:2e:b4:f2:45:bf:91:b4:c8:bc:14:f1:2:7a</boolMaskData></ROI></
        '''

        return mask

        '''
        mask = Mask( x , y , binaryMask )
        
        return mask
        '''


class AnimalPool:
    """
    Manages a pool of animals.
    """

    def __init__(self):
        self.animalDictionnary = {}

    def getAnimalsDictionnary(self):
        """ Returns the dictionary of the animals of the database """
        return self.animalDictionnary

    def getAnimalWithId(self, id):
        """ Returns the details of 1 specified animal called "id" """
        return self.animalDictionnary[id]

    def getAnimalList(self):
        """ Returns the list of the animals in the dictionnary """
        animalList = []

        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            animalList.append(animal)

        return animalList

    def loadAnimals(self, conn):
        """ Loads the animals
        DAX ???
        """
        print("Loading animals.")

        cursor = conn.cursor()
        self.conn = conn

        # Check the number of rows available in base
        query = "SELECT * FROM ANIMAL"
        cursor.execute(query)
        field_names = [i[0] for i in cursor.description]
        print("Fields available in lmtanalysis: ", field_names)

        # build query
        query = "SELECT "
        nbField = len(field_names)
        if nbField == 3:
            query += "ID, RFID, NAME"
        elif nbField == 4:
            query += "ID, RFID, NAME, GENOTYPE"
        elif nbField == 5:
            query += "ID, RFID, NAME, GENOTYPE, IND"

        query += " FROM ANIMAL ORDER BY GENOTYPE"
        print("SQL Query: " + query)

        cursor.execute(query)
        rows = cursor.fetchall()  # fetchall() ==> List of Rows
        cursor.close()

        self.animalDictionnary.clear()

        for row in rows:
            animal = None
            if len(row) == 3:
                animal = Animal(row[0], row[1], name=row[2], conn=conn)
            if len(row) == 4:
                animal = Animal(row[0], row[1], name=row[2], genotype=row[3], conn=conn)
            if len(row) == 5:
                animal = Animal(row[0], row[1], name=row[2], genotype=row[3], user1=row[4], conn=conn)

            if animal is not None:
                self.animalDictionnary[animal.baseId] = animal
                print(animal)
            else:
                print("Animal loader : error while loading animal.")

    def loadDetection(self, start=None, end=None, lightLoad=False):
        """ Loads the detection for all the animals of the Animals Dictionnary """
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].loadDetection(start=start, end=end, lightLoad=lightLoad)

    def filterDetectionByInstantSpeed(self, minSpeed, maxSpeed):
        """ Filters the detection for all the animals of the Animals Dictionnary """
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByInstantSpeed(minSpeed, maxSpeed)

    def filterDetectionByArea(self, x1, y1, x2, y2):
        """
        Filters the detection for all the animals of the Animals Dictionnary
        => in centimeters !
        """
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByArea(x1, y1, x2, y2)

    def filterDetectionByEventTimeLine(self, eventTimeLine):
        """ Filters the detection for all the animals of the Animals Dictionnary """
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByEventTimeLine(eventTimeLine)

    def getGenotypeList(self):
        """ Returns the list of genotypes for all the animals of the Animals Dictionary """
        genotype = {}
        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            genotype[animal.genotype] = True
        return genotype.keys()

    def getAnimalsWithGenotype(self, genotype):
        """ Returns the list of animals with a specified genotype """
        resultList = []
        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k]
            if animal.genotype == genotype:
                resultList.append(animal)
        return resultList
        # return [x for x in self.animalDictionnary if x.genotype==genotype ]

    def getNbAnimals(self):
        """ Returns the number of animals in the animalsDictionnary """
        return len(self.animalDictionnary)

    def getMaxDetectionT(self):
        """ Returns the timepoint of the last detection of all animals """
        maxFrame = 0
        for animal in self.getAnimalList():
            maxFrame = max(maxFrame, animal.getMaxDetectionT())
        return maxFrame

    def plotTrajectory(self, show=True, maskingEventTimeLine=None, title=None, scatter=False, saveFile=None):
        """
        Plots the trajectory of all the animals from the dictionary of animals
        """

        print("AnimalPool: plot trajectory.")
        nbCols = len(self.getAnimalList()) + 1
        fig, axes = plt.subplots(nrows=1, ncols=nbCols, figsize=(nbCols * 4, 1 * 4), sharex='all', sharey='all')

        if title is None:
            title = "Trajectory of animals"

        # Draw all animals
        axis = axes[0]
        legendList = []
        for animal in self.getAnimalList():
            print("Compute trajectory of animal " + animal.name)
            xList, yList = animal.getTrajectoryData(maskingEventTimeLine)
            print("Draw trajectory of animal " + animal.name)
            if scatter is True:
                axis.scatter(xList, yList, color=animal.getColor(), s=1, linewidth=1, alpha=0.05, label=animal.RFID)
                legendList.append(mpatches.Patch(color=animal.getColor(), label=animal.RFID))
            else:
                axis.plot(xList, yList, color=animal.getColor(), linestyle='-', linewidth=1, alpha=0.5,
                          label=animal.RFID)

        axis.legend(handles=legendList, loc=1)
        axis.set_xlim(90, 420)
        axis.set_ylim(-370, -40)

        # Draw separated animals
        for animal in self.getAnimalList():
            axis = axes[self.getAnimalList().index(animal) + 1]

            legendList = []

            print("Compute trajectory of animal " + animal.name)
            xList, yList = animal.getTrajectoryData(maskingEventTimeLine)
            print("Draw trajectory of animal " + animal.name)
            if scatter is True:
                axis.scatter(xList, yList, color=animal.getColor(), s=1, linewidth=1, alpha=0.05, label=animal.RFID)
                legendList.append(mpatches.Patch(color=animal.getColor(), label=animal.RFID))
            else:
                axis.plot(xList, yList, color=animal.getColor(), linestyle='-', linewidth=1, alpha=0.5,
                          label=animal.RFID)

            axis.legend(handles=legendList, loc=1)

        fig.suptitle(title)

        if saveFile is not None:
            print("Saving figure : " + saveFile)
            fig.savefig(saveFile, dpi=100)

        if show:
            plt.show(block=True)
            # plt.pause(3)

        plt.close()

    def showMask(self, t):
        """
        Shows the mask of all the animals, at the timepoint 't', in a figure.
        """
        fig, ax = plt.subplots()
        ax.set_xlim(90, 420)
        ax.set_ylim(-370, -40)

        for animal in self.getAnimalList():
            mask = animal.getBinaryDetectionMask(t)
            mask.showMask(ax=ax)

        plt.show(block=True)

    def getParticleDictionnary(self, start, end):
        """
        Returns the number of particles per frame.
        (Dax: Particles are the bedding projections around a mouse?)
        """

        query = "SELECT * FROM FRAME WHERE FRAMENUMBER >= {} AND FRAMENUMBER <= {}".format(start, end)
        # Query in a SQL database: Select all in FRAME for: start < FRAMENUMBER < end
        # Dax: What is FRAMENUMBER ??

        print("SQL Query: " + query)

        cursor = self.conn.cursor()  # Creates the "cursor" database
        cursor.execute(query)  # Executes the previously defined "query" within the database session "cursor"
        rows = cursor.fetchall()  # Returns a list of tuples corresponding to the "query" in "rows"
        # Dax: What is in "rows" ?
        cursor.close()

        particleDictionnary = {}

        for row in rows:
            particleDictionnary[row[0]] = row[2]
            # Dax: What does it do ?? what's in row[0], row[2] ?

        return particleDictionnary
