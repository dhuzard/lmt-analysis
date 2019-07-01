"""
Created on 13 sept. 2017

@author: Fab
"""
from lmtanalysis.Point import Point

""" 
Factor to convert distances from pixels to cm:
Dax: 1 pixel = 10/57 = 0.17543859649 cm ?
and 1 cm = 5.7 pixels
"""
scaleFactor = 10/57

""" Speed Thresholds (in cm/s) """
SPEED_THRESHOLD_LOW = 5
SPEED_THRESHOLD_HIGH = 10

""" Slope of the body between the nose and the tail base """
BODY_SLOPE_THRESHOLD = 40

""" threshold for the maximum distance allowed between two points """
MAX_DISTANCE_THRESHOLD = 71/scaleFactor

""" Threshold: minimum time after a first rearing to detect the second rearing (in frames) """
SEQUENTIAL_REARING_MIN_TIME_THRESHOLD = 10

""" Threshold: maximum time after a first rearing to detect the second rearing (in frames) """
SEQUENTIAL_REARING_MAX_TIME_THRESHOLD = 30

""" threshold for the area around a reared animal for sequential rearing """
SEQUENTIAL_REARING_POSITION_THRESHOLD = 50

""" threshold for the presence in proximity to a Point (e.g. within the water zone) """
MAX_DISTANCE_TO_POINT = 14/scaleFactor

""" threshold to classify the detection as a rearing; height of the front point """
FRONT_REARING_THRESHOLD = 50

""" threshold to compute head-genital events """
MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD = 15

""" Conversions frames => seconds (30fps) """
oneFrame = 1
oneSecond = 30
oneMinute = 30*60
oneHour = 30*60*60
oneDay = 30*60*60*24
oneWeek = 30*60*60*24*7

""" time window at the end of an event to test overlap with another event (0.5 second) """
TIME_WINDOW_BEFORE_EVENT = 15*oneFrame

""" Cage center in 50x50cm area """
cageCenterCoordinates50x50Area = Point(256, 208)

""" 
Corner Coordinates in 50x50cm area 
A = (114,63), B = (398,63), C = (398,353), D = (114,353)
"""
cornerCoordinates50x50Area = [
                        (114, 63),
                        (398, 63),
                        (398, 353),
                        (114, 353)
                        ]


def second(s):
    return s * oneSecond


def day(d):
    return d * oneDay


def hour(h):
    return h * oneHour
