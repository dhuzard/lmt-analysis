"""
Created on 13 sept. 2017

@author: Fab
"""
from lmtanalysis.Point import Point

""" 
Factor to convert distances from pixels to cm:
Dax: 1 pixel = 10/57 = 0.17543859649 cm ?
X axis: 1 pxl = 0.1761 cm / Y axis: 1 pxl = 0.1724 cm
and 1 cm = 5.7 pixels
"""
scaleFactor = 10/57  # 0.1754 cm (?)

""" Speed Thresholds (in cm/s) """
SPEED_THRESHOLD_LOW = 5
SPEED_THRESHOLD_HIGH = 10

""" Slope of the body between the nose and the tail base 
    Dax: is it an angle, 40° ? """
BODY_SLOPE_THRESHOLD = 40

""" threshold for the maximum distance allowed between two points """
MAX_DISTANCE_THRESHOLD = 71/scaleFactor  # 71/10/57 = 71*57/10 = 404.7 cm

""" Threshold: minimum time after a first rearing to detect the second rearing (in frames) """
SEQUENTIAL_REARING_MIN_TIME_THRESHOLD = 10
""" Threshold: maximum time after a first rearing to detect the second rearing (in frames) """
SEQUENTIAL_REARING_MAX_TIME_THRESHOLD = 30
""" threshold for the area around a reared animal for sequential rearing """
SEQUENTIAL_REARING_POSITION_THRESHOLD = 50

""" threshold to classify the detection as a rearing; height of the front point """
FRONT_REARING_THRESHOLD = 50

""" Max distance threshold for the presence in proximity to a Point (e.g. within the water zone) """
MAX_DISTANCE_TO_POINT = 14/scaleFactor  # 14/10/57 = 14*57/10 = 79.8 cm

""" threshold to compute head-genital events """
MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD = 15

""" Conversions frames => seconds (30fps) """
oneFrame = 1
oneSecond = 30  # 30 fps
oneMinute = 30*60  # 1'800 frames
oneHour = 30*60*60  # 108'000 frames
oneDay = 30*60*60*24  # 2'592'000 frames
oneWeek = 30*60*60*24*7  # 18'144'000 frames

""" time window at the end of an event to test overlap with another event (0.5 second) """
TIME_WINDOW_BEFORE_EVENT = 15*oneFrame

""" Cage center point in 50x50cm area """
cageCenterCoordinates50x50Area = Point(256, 208)

""" Dax: Cage center zone coordinates in 50x50cm area """
cageCenterZone50x50Area = [
                          (185, 135.5),
                          (327, 135.5),
                          (327, 280.5),
                          (185, 280.5)
                          ]

""" 
Corner Coordinates (in pixels) in the 50x50cm area:
A = (114,63), B = (398,63), C = (398,353), D = (114,353)
"""
cornerCoordinates50x50Area = [
                             (114, 63),
                             (398, 63),
                             (398, 353),
                             (114, 353)
                             ]

""" Dax:
Corner zones coordinates (in pixels) in the 50x50cm area:
NW = A(114, 63), B(256, 208)
NE = A(256, 63), B(398, 208)
SE = A(256, 208), B(398, 353)
SW = A(114, 208), B(256, 353)
"""
cornerZonesCoordinates50x50Area = {
                                 "NW": [(114, 63), (256, 208)],
                                 "NE": [(256, 63), (398, 208)],
                                 "SE": [(256, 208), (398, 353)],
                                 "SW": [(114, 208), (256, 353)]
                             }


def second(s):
    return s * oneSecond


def day(d):
    return d * oneDay


def hour(h):
    return h * oneHour
