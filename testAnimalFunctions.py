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

if __name__ == '__main__':
    files = getFilesToProcess()

    for file in files:

        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals
        animalPool.loadDetection()  # load the detection of the animals for all the time of the recording

        # ***Plot and show original trajectory***
        # animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=True", scatter=True)
        # animalPool.plotTrajectory(title="Trajectories NOT filtered, scatter=False", scatter=False)

        measures = {0: [[0, 1], [0, 2], [0, 5], [1, 5], [2, 5], [5, 10], [5, 20], [5, 30]],
                    1: ["meanBodySize", "medianBodySize", "meanBodyHeight", "medianBodyHeight", "meanBodySlope",
                        "medianBodySlope", "meanFrontZ", "meanSpeed", "medianSpeed", "meanVerticalSpeed",
                        "medianVerticalSpeed", "bodyThreshold", "massHeightThreshold", "numberOfDetections"
                        ]
                    }

        """
        meanBodySize, medianBodySize, meanBodyHeight, medianBodyHeight, meanBodySlope, medianBodySlope, \
               meanFrontZ,meanSpeed, medianSpeed, meanVerticalSpeed, medianVerticalSpeed, bodyThreshold, \
               massHeightThreshold, numberOfDetections
        """
        count = 2

        for animal in animalPool.getAnimalList():
            print("count = ", count)
            print("Animal RFID #", animal.RFID)
            numberOfFrame = len(animal.detectionDictionnary.keys())
            timeInSecond = numberOfFrame / 30  # 30 fps
            print("Time spent in area (s): ", timeInSecond)
            print("Distance traveled in area (cm): ", animal.getDistance())  # distance traveled

            measuresTemp = {}

            for i in range(8):
                print("i =", i)
                print("For speed", measures[0][i][0], "-", measures[0][i][1], "cm/s:")
                animal.loadDetection()
                measuresTemp[i] = animal.getMeasures(speedmin=measures[0][i][0], speedmax=measures[0][i][1])

                threshold = animal.getBodyThreshold()
                print("Body threshold is: ", threshold)
                # measuresTemp[i][13] = threshold
                """ PROBLEME: TypeError: 'tuple' object does not support item assignment
                Comment ajouter le threshold a la list des measures ?
                Et peut-on faire plus proprement? (calculer les measures au meme endroit?)
                Probleme: utiliser le for key in keylist le moins possible... (long calcul)"""

            measures[count] = measuresTemp
            count += 1

        # measures.to_csv('measures.csv')
        # How to export a dictionary ?

        """
        measures_05 = {}
        measures_010 = {}
        measures_020 = {}
        measures_030 = {}
        measures_510 = {}
        measures_1020 = {}
        measures_2030 = {}
        measures_3040 = {}
        measures_40more = {}

        measures_05[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                          "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                          "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_010[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                           "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                           "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_020[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                           "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                           "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_030[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                           "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                           "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_510[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                           "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                           "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_1020[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                            "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                            "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_2030[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                            "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                            "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_3040[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                            "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                            "meanVerticalSpeed", "medianVerticalSpeed"]
        measures_40more[0] = ["meanBodySize", "medianBodySize", "meanMassZ", "medianMassZ", "meanFrontZ", "meanBodySlope",
                              "medianBodySlope", "meanBodyHeight", "medianBodyHeight", "meanSpeed", "medianSpeed",
                              "meanVerticalSpeed", "medianVerticalSpeed"]
        """

"""
print("For speed 0-10 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=0, speedmax=10)
print("For speed 0-20 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=0, speedmax=20)
print("For speed 0-30 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=0, speedmax=30)
print("For speed 5-10 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=5, speedmax=10)
print("For speed 10-20 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=10, speedmax=20)
print("For speed 20-30 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=20, speedmax=30)
print("For speed 30-40 cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=30, speedmax=40)
print("For speed 40-++ cm/s:")
animal.loadDetection()
measures[i][count] = animal.getMeasures(speedmin=40, speedmax=1000000000)
"""


