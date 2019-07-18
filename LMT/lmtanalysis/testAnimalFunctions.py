"""
Created on June 2019

@author: Dax
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

import sqlite3
import csv
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy

if __name__ == '__main__':
    files = getFilesToProcess()

    for file in files:

        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals
        # animalPool.loadDetection()  # load the detection of the animals for all the time of the recording

        # ***Plot and show original trajectory***
        # animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=True", scatter=True)
        # animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=False", scatter=False)

        #bins = [[0, 1], [0, 2], [0, 5], [1, 5], [2, 5], [5, 10], [5, 20], [5, 30]]  # Creates list of speed bins
        bins = [[0, 2], [2, 12]]  # Creates list of speed bins
        names = ["meanBodySize", "medianBodySize", "meanBodyHeight", "medianBodyHeight", "meanBodySlope",
                 "medianBodySlope", "meanFrontZ", "meanSpeed", "medianSpeed", "meanVerticalSpeed",
                 "medianVerticalSpeed", "bodyThreshold", "massHeightThreshold", "numberOfDetections"]  # list of names

        """ Dax: Use of a dictionary ??
        measures = {'bin': [[0, 1], [0, 2], [0, 5], [1, 5], [2, 5], [5, 10], [5, 20], [5, 30]],
                    'name': ["meanBodySize", "medianBodySize", "meanBodyHeight", "medianBodyHeight", "meanBodySlope",
                             "medianBodySlope", "meanFrontZ", "meanSpeed", "medianSpeed", "meanVerticalSpeed",
                             "medianVerticalSpeed", "bodyThreshold", "massHeightThreshold", "numberOfDetections"
                             ]
                    } 
        """

        measures = [bins, names, [], []]  # starts to create the measures list with the speed bins and measure names
        print("measures:")
        print(measures)

        # count = 2

        # Start by loading the detection on the animalPool for the different speed bins
        for bin in measures[0]:  # start iteration on the bins
            print("Loading detections of AnimalPool for speed", bin[0], "-", bin[1], "cm/s:")
            animalPool.loadDetection()  # Loads all the animals, Dax: Better here than before or after ?

            for animal in animalPool.getAnimalList():  # Iteration in the list of animals (1 animal at a time)
                print("baseID +1  = ", animal.baseId+1)
                print("Animal RFID #", animal.RFID)
                # measures.append(animal.RFID)
                numberOfFrame = len(animal.detectionDictionnary.keys())
                timeInSecond = numberOfFrame / 30  # 30 fps
                print("Time detected (s): ", timeInSecond)
                print("Distance traveled (cm): ", animal.getDistance())  # distance traveled

                measuresTemp = {}

                # animal.loadDetection()
                # measuresTemp[val] = animal.getMeasures(speedmin=measures[0][val][0], speedmax=measures[0][val][1])
                measures[animal.baseId + 1].append(animal.getMeasures(speedmin=bin[0], speedmax=bin[1]))

            # measures[count] = measuresTemp
            # count += 1
        print("measures:")
        print(measures)

            # frame = pd.DataFrame(measures, columns=['0', '1', '2', '3'])
            # print("frame:")
            # print(frame)
            # measures.to_csv('measures.csv')
            # How to export a dictionary ?
