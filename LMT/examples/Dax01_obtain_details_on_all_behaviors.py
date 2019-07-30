import sqlite3

import matplotlib.pyplot as plt
import numpy as np

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Measure import *

if __name__ == '__main__':
    files = getFilesToProcess()

    """ DEFINE CONSTANTS """
    start = oneHour * 1
    stop = oneHour * 2
    nbTimebins = int((stop - start) / oneHour)  # For timebins of 1h
    print("There are", nbTimebins, "bins")

    for file in files:
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        animalNumber = animalPool.getNbAnimals()
        print("There are", animalNumber, "animals.")

        if animalNumber >= 1:
            behavioralEventsForOneAnimal = ["Move isolated", "Rearing", "Rear isolated", "Stop isolated", "WallJump",
                                            "SAP"]
            print("The behaviors extracted are:", behavioralEventsForOneAnimal)
        if animalNumber >= 2:
            behavioralEventsForTwoAnimals = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                "Side by side Contact, opposite way", "Social approach", "Social escape",
                                "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated",
                                "Train2", "Group2", "Move in contact", "Rear in contact"]
            print("and:", behavioralEventsForTwoAnimals)
        if animalNumber >= 3:
            behavioralEventsForThreeAnimals = ["Group3", "Group 3 break", "Group 3 make"]
            print("and:", behavioralEventsForThreeAnimals)
        if animalNumber >= 4:
            behavioralEventsForFourAnimals = ["Group4", "Group 4 break", "Group 4 make"]
            print("and:", behavioralEventsForFourAnimals)

        animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop

        """ plot and show original trajectory """
        # animalPool.plotTrajectory(show=True, title="Trajectories NOT filtered, scatter=True", scatter=True)
        # animalPool.plotTrajectory(show=True, title="Trajectories NOT filtered, scatter=False", scatter=False)

        """ ********* SORTING BY TIME BINS & EXCLUDE SPEED > 100cm/s *********** """
        """
        for i in range(nbTimebins):
            animalPool.loadDetection(start=start + i * oneHour, end=start + i * oneHour + oneHour)
            animalPool.filterDetectionByInstantSpeed(0, 100)  # Plot sorted by speed
            animalPool.plotTrajectory(title="Trajectories filtered by speed (0-100cm/s). Time bin #" + str(i + 1),
                                      scatter=True)
            
        animalPool.loadDetection(start=start, end=stop)  # Reload detections between start and stop
        """

        for animal in animalPool.getAnimalList():
            print("*** General parameters for each animal ***")
            print("Animal:", animal.RFID, "/ Animal Id:", animal.baseId)
            print("Animal name:", animal.name, "/ Animal genotype:", animal.genotype)
            nbOfDetectionFrames = len(animal.detectionDictionnary.keys())
            timeInSecond = nbOfDetectionFrames / 30  # 30 fps
            print("Total time spent in arena (s): ", timeInSecond)
            print("Total distance traveled in arena (cm): ", animal.getDistance())  # distance traveled

        allBehaviorsDico = {}
        # TODO: SEPARATE THE BEHAVIORS WITH ONE, TWO, THREE OR FOUR ANIMALS

        """ For ONE ANIMAL """
        for behavior in behavioralEventsForTwoAnimals:
            print("**** ", behavior, " ****")
            behavioralList = []

        """ FOR TWO ANIMALS """
        for behavior in behavioralEventsForTwoAnimals:
            print("**** ", behavior, " ****")
            behavioralList = []

            for a in animalPool.getAnimalsDictionnary():
                for b in animalPool.getAnimalsDictionnary():
                    if a == b:
                        continue
                    eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, minFrame=start, maxFrame=stop)
                    behavioralList.append(eventTimeLine)
                    # print(OralGenitalList[a])
            plotMultipleTimeLine(behavioralList, title=behavior)

            allBehaviorsDico[behavior] = behavioralList

            CI95 = []
            for beh in behavioralList:
                print("eventName :", beh.eventName)
                print("eventNameWithId :", beh.eventNameWithId)
                print("idA :", beh.idA)
                print("idB :", beh.idB)
                print("idC :", beh.idC)
                print("idD :", beh.idD)
                print("TotalLength :", beh.getTotalLength(), "frames.")
                print("MeanEventLength :", beh.getMeanEventLength())
                print("MedianEventLength :", beh.getMedianEventLength())
                print("NumberOfEvent :", beh.getNumberOfEvent())
                print("StandardDeviationEventLength :", beh.getStandardDeviationEventLength())

                if beh.getMedianEventLength() is None:
                    continue

                CI = 1.96 * beh.getStandardDeviationEventLength() / np.math.sqrt(beh.getNumberOfEvent())
                CI95.append([beh.getMeanEventLength() - CI, beh.getMeanEventLength() + CI])
                print("Confidence interval 95% => [", beh.getMeanEventLength() - CI, ",",
                      beh.getMeanEventLength() + CI, "].")

        print("!!! End of analysis !!!")
