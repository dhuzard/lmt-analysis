"""
Created on 08 July 2019

@author: Dax

import a database a play with data in the python console ?!
ADAPTED FROM THE __init__ function
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

import sqlite3

from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine

file = getFilesToProcess()  # Select ONE file

connection = sqlite3.connect(file)  # connect to database
animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
animalPool.loadAnimals(connection)  # load infos about the animals
animalPool.loadDetection(start=0, end=oneMinute * 5)  # load the detection within the time specified

# plot and show original trajectory
# animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=True", scatter=True)
# animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=False", scatter=False)

# *********SORTING BY TIME BINS***********
"""
for i in range(5):
    # classic plots
    animalPool.loadDetection(start=i * 1800, end=oneMinute + i * 1800)  # 1800 frames in 1 minute
    animalPool.plotTrajectory(title=i, scatter=True)

    # Plot sorted by speed
    animalPool.filterDetectionByInstantSpeed(0, 100)
    animalPool.plotTrajectory(title="Trajectories filtered by speed (0-100cm/s)")
"""

# *********SORTING BY SPEED***********
# animalPool.loadDetection(start=0, end=oneMinute * 5)

# filter detection by animalSpeed: 0-5cm/s
# animalPool.filterDetectionByInstantSpeed(0, 5)
#animalPool.plotTrajectory(title="Trajectories filtered by speed (0-5cm/s)")

# filter detection by animalSpeed: 5-20cm/s
# animalPool.loadDetection(start=0, end=oneMinute * 5)
# animalPool.filterDetectionByInstantSpeed(5, 20)
# animalPool.plotTrajectory(title="Trajectories filtered by speed (5-20cm/s)")

# filter detection by animalSpeed: 40-50cm/s
# animalPool.loadDetection(start=0, end=oneMinute * 5)
# animalPool.filterDetectionByInstantSpeed(40, 50)
# animalPool.plotTrajectory(title="Trajectories filtered by speed (40-50cm/s)")

# filter detection by animalSpeed: 0-50cm/s
# animalPool.loadDetection(start=0, end=oneMinute * 5)
# animalPool.filterDetectionByInstantSpeed(00, 50)
# animalPool.plotTrajectory(title="Trajectories filtered by speed (0-50cm/s)")

# filter detection by animalSpeed: 50-5000000cm/s
# animalPool.loadDetection(start=0, end=oneMinute * 5)
# animalPool.filterDetectionByInstantSpeed(50, 50000000000) #TRAJECTORIES DUE TO TRACKING ISSUE
# animalPool.plotTrajectory(title="Trajectories filtered by speed (>50cm/s)")

# Reload all detection
# animalPool.loadDetection(start=0, end=oneMinute * 5)

# PLOT ALL TRAJECTORIES
# print("ALL TRAJECTORIES")

"""
for animal in animalPool.getAnimalList():
    print("Animal: ", animal.RFID)
    numberOfFrame = len(animal.detectionDictionnary.keys())
    timeInSecond = numberOfFrame / 30  # there are 30 frames per second
    print("Time spent in area (s): ", timeInSecond)
    print("Distance traveled in area (cm): ", animal.getDistance())  # distance traveled
"""

#DEFINE ZONES/CORNERS
# NorthWest = [0, 0, 25, 25]
# NorthEast = [25, 0, 50, 25]
# SouthWest = [0, 25, 25, 50]
# SouthEast = [25, 25, 50, 50]
CornersName = ['NorthWest', 'NorthEast', 'SouthWest', 'SouthEast']

# DEFINE a Dictionnary of ZONES/CORNERS
cornersInCm = {'NorthWest': [0, 0, 25, 25],
               'NorthEast': [25, 0, 50, 25],
               'SouthWest': [0, 25, 25, 50],
               'SouthEast': [25, 25, 50, 50]
               }

# *** PLOT THE 4 CORNERS SEQUENTIALLY ****

for corner in CornersName:
    animalPool.loadDetection(start=0, end=5*oneMinute)
    animalPool.filterDetectionByArea(cornersInCm.get(corner)[0], cornersInCm.get(corner)[1],
                                     cornersInCm.get(corner)[2], cornersInCm.get(corner)[3])
    for animal in animalPool.getAnimalList():  # loop over all animals
        print("In corner: ", corner)
        print("Animal: ", animal.RFID)  # print RFID
        numberOfFrame = len(animal.detectionDictionnary.keys())
        timeInSecond = numberOfFrame / 30  # there are 30 frames per second
        print("Time spent in area (in second): ", timeInSecond)  # time in area
        print("Distance traveled in area (in centimeter): ", animal.getDistance())  # distance traveled
    # animalPool.plotTrajectory(title="Trajectories in Corner ")

# **** Extract Behaviors ***

# Rearings of ALL Rats
RearingList = []
for a in animalPool.getAnimalsDictionnary():
    RearingList.append(EventTimeLine(connection, "Rearing", idA=a, minFrame=0, maxFrame=oneHour))
plotMultipleTimeLine(RearingList)

# Oral-genital contacts between ALL ANIMALS (FOR LOOP)
OralGenitalList = []
for a in animalPool.getAnimalsDictionnary():
    for b in animalPool.getAnimalsDictionnary():
        if a == b:
            continue
        OralGenitalList.append(EventTimeLine(connection, "Oral-genital Contact", idA=a,
                                             idB=b, minFrame=0, maxFrame=oneHour))
        print(OralGenitalList)
plotMultipleTimeLine(OralGenitalList)

# *** Create Event list of Moving ***
movingList = []
for a in animalPool.getAnimalsDictionnary():
    movingList.append(EventTimeLine(connection, "Move", idA=a, minFrame=0, maxFrame=oneHour))

print("Event list for label ", movingList[0].eventNameWithId)
print("for animal 1:", animalPool.getAnimalsDictionnary()[1].RFID)
# print("for animal 2:", animalPool.getAnimalsDictionnary()[2].RFID)
print("Number of events:", len(movingList[0].getEventList()))

plotMultipleTimeLine(movingList)

data = []

for event in movingList[0].eventList:
    data.append([event.startFrame, event.endFrame, event.duration(), event.duration() / 30])

df = pd.DataFrame(data=np.array(data), columns=["Start frame", "End frame", "Duration (frames)", "Duration (sec)"])
print(df)

df.to_csv('moving.csv')

# **** Print and Export X,Y,Z Coordinates ****
animalPool.loadDetection(start=0, end=oneHour/12)

print("******")
print(animal)
print("Position coordinates:")

positions = []
for animal in animalPool.getAnimalList():
    print("Test Animal: ", animal)
    for detectionKey in animal.detectionDictionnary:
        detection = animal.detectionDictionnary[detectionKey]
        subject = animal
        t = detectionKey
        x = detection.massX
        y = detection.massY
        z = detection.massZ
        positions.append([subject, t, x, y, z])

dataFrame = pd.DataFrame(data=np.array(positions), columns=["Subject", "frame number", "x", "y", "z"])

print(dataFrame)
dataFrame.to_csv('positions.csv')
