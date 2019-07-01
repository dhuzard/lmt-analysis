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

            # Export a dictionary to .csv
            print("export .csv for animal", animal)
            w = csv.writer(open("output_%d.csv" % count, "w"))
            for key, val in measures[count].items():
                print("key is: ", key, ", and val is: ", val)
                w.writerow([key, val])

            count += 1
