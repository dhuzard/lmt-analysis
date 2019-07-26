import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv

import sqlite3

from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine

if __name__ == '__main__':
    files = getFilesToProcess()

    """ DEFINE CONSTANTS """
    start = oneHour * 7
    stop = oneHour * 9
    nbTimebins = int((stop - start) / oneHour)  # Do timebins of 1h
    print("There are", nbTimebins, "bins")

    for file in files:
        plt.interactive(False)
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals
        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop

        """ plot and show original trajectory """
        # animalPool.plotTrajectory(show=True, title="Trajectories NOT filtered, scatter=True", scatter=True)
        # animalPool.plotTrajectory(show=True, title="Trajectories NOT filtered, scatter=False", scatter=False)

        """ ********* SORTING BY TIME BINS & EXCLUDE SPEED > 100cm/s *********** """

        for i in range(nbTimebins):

            animalPool.loadDetection(start=start + i * oneHour, end=start + i * oneHour + oneHour)
            animalPool.filterDetectionByInstantSpeed(0, 100)  # Plot sorted by speed
            animalPool.plotTrajectory(title="Trajectories filtered by speed (0-100cm/s). Time bin #" + str(i+1),
                                      scatter=True)

        """ *********SORTING BY SPEED*********** """
        """
        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop
        animalPool.filterDetectionByInstantSpeed(0, 60)  # filter detection by animalSpeed: 0-60cm/s
        animalPool.plotTrajectory(show=True, title="Trajectories filtered by speed (0-60cm/s)")

        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop
        animalPool.filterDetectionByInstantSpeed(60, 5000000000000)  # speed > 60cm/s = TRAJECTORIES DUE TO ERROR TRACK
        animalPool.plotTrajectory(title="Trajectories filtered by speed (>60cm/s)")

        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop
        animalPool.filterDetectionByInstantSpeed(5, 20)  # filter detection by animalSpeed: 5-20cm/s
        #animalPool.plotTrajectory(title="Trajectories filtered by speed (5-20cm/s)")

        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop
        animalPool.filterDetectionByInstantSpeed(40, 50)  # filter detection by animalSpeed: 40-50cm/s
        #animalPool.plotTrajectory(title="Trajectories filtered by speed (40-50cm/s)")
        """

        animalPool.loadDetection(start=start, end=stop)  # Reload detections between start and stop
        
        print("ALL TRAJECTORIES")
        for animal in animalPool.getAnimalList():
            print("Animal: ", animal.RFID)
            nbOfDetectionFrames = len(animal.detectionDictionnary.keys())
            timeInSecond = nbOfDetectionFrames / 30  # there are 30 frames per second
            print("Total time spent in arena (s): ", timeInSecond)
            print("Total distance traveled in arena (cm): ", animal.getDistance())  # distance traveled

        # DEFINE ZONES/CORNERS
        # NorthWest = [0, 0, 25, 25]
        # NorthEast = [25, 0, 50, 25]
        # SouthWest = [0, 25, 25, 50]
        # SouthEast = [25, 25, 50, 50]
        # CornersName = ['NorthWest', 'NorthEast', 'SouthWest', 'SouthEast']

        """ DEFINE a Dictionary of ZONES/CORNERS """
        Corners = {'NorthWest': [0, 0, 25, 25],
                   'NorthEast': [25, 0, 50, 25],
                   'SouthWest': [0, 25, 25, 50],
                   'SouthEast': [25, 25, 50, 50]
                   }

        """ *** PLOT THE 4 CORNERS SEQUENTIALLY **** """
        plt.figure()
        for cornerName in Corners.keys():
            animalPool.loadDetection(start=start, end=stop)
            animalPool.filterDetectionByArea(Corners.get(cornerName)[0], Corners.get(cornerName)[1],
                                             Corners.get(cornerName)[2], Corners.get(cornerName)[3])
            for animal in animalPool.getAnimalList():  # loop over all animals
                print("In corner: ", cornerName)
                print("Animal: ", animal.RFID)  # print RFID
                numberOfFrame = len(animal.detectionDictionnary.keys())
                timeInSecond = numberOfFrame / 30  # there are 30 frames per second
                print("Time spent in area (in second): ", timeInSecond)  # time in area
                print("Distance traveled in area (in centimeter): ", animal.getDistance())  # distance traveled
                # animal.plotTrajectory(title="Trajectories in Corner ")
            plt.subplot()
            animalPool.plotTrajectory(title="Trajectories in Corner ", scatter=True)

        # **** Extract Behaviors ***
        """
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
        """
        print("!!! End of analysis !!!")
