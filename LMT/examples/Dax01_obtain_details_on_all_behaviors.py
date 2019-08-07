import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Measure import *


def computeBehaviorsData(behaviorList):
    CI95 = []
    for beh in behaviorList:
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


if __name__ == '__main__':
    files = getFilesToProcess()

    """ DEFINE CONSTANTS """
    start = oneHour * 1
    stop = oneHour * 2
    timeBinsDuration = 10*oneMinute
    nbTimebins = int((stop - start) / timeBinsDuration)
    print("There are", nbTimebins, "bins of ", timeBinsDuration, "frames (", timeBinsDuration/30/60,
          "minutes) between frames [", start, "-", stop, "].")

    for file in files:
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        animalNumber = animalPool.getNbAnimals()
        print("There are", animalNumber, "animals.")

        if animalNumber >= 1:
            behavioralEventsForOneAnimal = ["Move", "Move isolated", "Rearing", "Rear isolated", "Stop isolated", "WallJump",
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

        for animal in animalPool.getAnimalList():
            print("*** General parameters for /", animal, "/ ***")
            print("Animal RFID:", animal.RFID, "/ Animal Id:", animal.baseId)
            print("Animal name:", animal.name, "/ Animal genotype:", animal.genotype)
            nbOfDetectionFrames = len(animal.detectionDictionnary.keys())
            timeInSecond = nbOfDetectionFrames / 30  # 30 fps
            print("Detection time: ", timeInSecond, "seconds.")
            print("Distance traveled in arena (cm): ", animal.getDistance(tmin=start, tmax=stop))  # distance traveled

        listOfBehDicos = []
        allBehaviorsDico = {}

        for bin in range(nbTimebins):
            """ For 1+ ANIMAL """
            if animalNumber >= 1:
                for behavior in behavioralEventsForOneAnimal:
                    print("**** ", behavior, " ****")
                    behavioralList = []

                    for a in animalPool.getAnimalsDictionnary():
                        eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=start, maxFrame=stop)
                        behavioralList.append(eventTimeLine)

                    plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)
                    allBehaviorsDico[behavior] = behavioralList
                    computeBehaviorsData(behavioralList)  # Function defined before __main__

            """ FOR 2+ ANIMALS """
            if animalNumber >= 2:
                for behavior in behavioralEventsForTwoAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList = []

                    for a in animalPool.getAnimalsDictionnary():
                        if behavior == "Move in contact" or behavior == "Rear in contact":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=start, maxFrame=stop)
                            behavioralList.append(eventTimeLine)
                            continue
                        for b in animalPool.getAnimalsDictionnary():
                            if a == b:
                                continue
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, minFrame=start, maxFrame=stop)
                            behavioralList.append(eventTimeLine)
                            # print(OralGenitalList[a])

                    plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)
                    allBehaviorsDico[behavior] = behavioralList
                    computeBehaviorsData(behavioralList)  # Function defined before __main__

            """ FOR 3+ ANIMALS """
            if animalNumber >= 3:
                for behavior in behavioralEventsForThreeAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList = []

                    for a in animalPool.getAnimalsDictionnary():
                        if behavior == "Group 3 make" or behavior == "Group 3 break":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=start, maxFrame=stop)
                            behavioralList.append(eventTimeLine)
                            continue
                        for b in animalPool.getAnimalsDictionnary():
                            if a == b:
                                continue
                            for c in animalPool.getAnimalsDictionnary():
                                if a == c or b == c:
                                    continue

                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c,
                                                              minFrame=start, maxFrame=stop)
                                behavioralList.append(eventTimeLine)

                    plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)
                    allBehaviorsDico[behavior] = behavioralList
                    computeBehaviorsData(behavioralList)  # Function defined before __main__

            """ FOR 4 ANIMALS """
            if animalNumber >= 4:
                for behavior in behavioralEventsForFourAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList = []

                    for a in animalPool.getAnimalsDictionnary():
                        for b in animalPool.getAnimalsDictionnary():
                            if a == b:
                                continue
                            for c in animalPool.getAnimalsDictionnary():
                                if a == c or b == c:
                                    continue
                                for d in animalPool.getAnimalsDictionnary():
                                    if a == d or b == d or c == d:
                                        continue

                                    eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c, idD=d,
                                                                  minFrame=start, maxFrame=stop)
                                    behavioralList.append(eventTimeLine)

                    plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)
                    allBehaviorsDico[behavior] = behavioralList
                    computeBehaviorsData(behavioralList)  # Function defined before __main__

            listOfBehDicos.append(allBehaviorsDico)

        # TODO: Create a DataFrame with the Dictionary of all the behaviors ('allBehaviorsDico') ?

        """ Say it's done ! """
        print("!!! End of analysis !!!")