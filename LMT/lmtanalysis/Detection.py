"""
Created on 12 sept. 2017

@author: Fab
"""

import math
from lmtanalysis.Measure import *
from lmtanalysis.Point import Point


class Detection:
    """
    Describes the different detection features of an animal:
    "mass" = center of mass of the animal
    "front" or "back" = nose and tail base
    Each have X,Y,Z coordinates.
    """

    def __init__(self, massX, massY, massZ=None, frontX=None, frontY=None, frontZ=None, backX=None, backY=None,
                 backZ=None, rearing=None, lookUp=None, lookDown=None):

        self.massX = massX
        self.massY = massY
        self.massZ = massZ
        self.massPoint = Point(massX, massY)

        self.frontX = frontX
        self.frontY = frontY
        self.frontZ = frontZ
        self.frontPoint = Point(frontX, frontY)

        self.backX = backX
        self.backY = backY
        self.backZ = backZ
        self.backPoint = Point(backX, backY)

        self.rearing = rearing
        self.lookUp = lookUp
        self.lookDown = lookDown

    def isHeadAndTailDetected(self):
        """ Tells if an animal is properly detected """
        if self.frontX == -1 or self.frontY == -1 or self.backX == -1 or self.backY == -1:
            return False
        return True

    def getBodySize(self):
        """ returns the length of the body
        Dax: = elongation ?
        """
        return math.hypot(self.frontX-self.backX, self.frontY-self.backY)

    def getBodySlope(self):
        """
        Calculate the instantaneous slope of the animal between nose ('front') and tail ('back')
        """

        if self.frontZ == 0 or self.backZ == 0:
            return None
        else:
            bodySlope = self.frontZ - self.backZ

        return bodySlope

    def getDirection(self):
        """
        determines the direction of the animal using the head and the center of mass
        """
        angleDir = math.atan2(self.frontY-self.massY, self.frontX-self.massX)
        return angleDir

    def getDistanceTo(self, detectionB):
        """
        Determines the distance between the focal animal and animalB at one specified time point t.
        It checks first that both animals are detected at this time point
        """
        distanceTo = None

        if detectionB is None:
            return None

        if detectionB.massX is None:
            return None

        if math.hypot(self.massX - detectionB.massX, self.massY - detectionB.massY) > MAX_DISTANCE_THRESHOLD:
            # if the distance calculated between the two individuals is too large, discard
            print("WARNING: Detection.getDistanceTo : Distance Max reached. returning None")
            return None

        else:
            distanceTo = math.hypot(self.massX - detectionB.massX, self.massY - detectionB.massY)
            return distanceTo

    def getDistanceToPoint(self, xPoint, yPoint):
        """
        Determine the distance between the focal animal and a specific point in the arena
        """
        distanceToPoint = math.hypot(self.massX - xPoint, self.massY - yPoint)
        return distanceToPoint

    def isInZone(self, xa=149, xb=363, ya=318, yb=98):
        """
        Check whether a detection of animal A is located in the specified zone of the cage.
        The default zone is the center: xa=149, xb=363, ya=318, yb=98
        """

        if xa < self.massX < xb and yb < self.massY < ya:
            return True

        return False

    def isRearing(self):
        """
        Determines whether the animal is rearing at this detection.
        """
        if self.getBodySlope() is None:
            return False

        if -BODY_SLOPE_THRESHOLD < self.getBodySlope() < BODY_SLOPE_THRESHOLD:
            return False

        else:
            return True

    def isRearingZ(self):
        """
        Determines whether the animal is rearing at this detection, using the old criteria from the first version
        """
        if self.frontZ is None:
            return False

        if self.frontZ < FRONT_REARING_THRESHOLD:
            return False

        else:
            return True
