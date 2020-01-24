"""
Created on 20 August 2019

@author: Dax
"""

import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Measure import *


def computeBehaviorsData(behavior, show=False):
    """ Computes the details (Mean, Nb, Std, CI95...) of a behavior."""

    name = behavior.eventName
    nameAndIds = behavior.eventNameWithId
    idA = behavior.idA
    idB = behavior.idB
    idC = behavior.idC
    idD = behavior.idD
    totalLength = behavior.getTotalLength()
    meanLength = behavior.getMeanEventLength()
    numberOfEvents = behavior.getNumberOfEvent()
    stdLength = behavior.getStandardDeviationEventLength()

    if behavior.getMedianEventLength() is not None:
        medianLength = behavior.getMedianEventLength()
    else:
        medianLength = None

    CI95 = [None]*2
    if meanLength is not None:
        CI = 1.96 * behavior.getStandardDeviationEventLength() / np.math.sqrt(behavior.getNumberOfEvent())
        CI95[0] = meanLength - CI
        CI95[1] = meanLength + CI
    else:
        meanLength = None

    returnedBehaviors = {
        "name": name,
        "idA": idA,
        "idB": idB,
        "idC": idC,
        "idD": idD,
        "totalLength": totalLength,
        "meanLength": meanLength,
        "medianLength": medianLength,
        "numberOfEvents": numberOfEvents,
        "stdLength": stdLength,
        "CI95_low": CI95[0],
        "CI95_up": CI95[1]
    }

    # print(f"{nameAndIds}")
    # print(f"   -TotalLength: {totalLength} frames.")
    # print(f"   -MeanEventLength: {meanLength}")
    # print(f"   -MedianEventLength: {medianLength}")
    # print(f"   -NumberOfEvent: {numberOfEvents}")
    # print(f"   -StandardDeviationEventLength: {stdLength}")
    # print(f"   -The confidence interval (95%) is [{CI95[0]},{CI95[1]}].")

    # if show:
        # beh.plotEventDurationDistributionHist(nbBin=30, title="Timebin #"+str(bin) + " / " + beh.eventNameWithId)
        # beh.plotEventDurationDistributionBar(title="Timebin #"+str(bin) + " / " + beh.eventNameWithId)

    # TODO: Show the histogram of events, with a 'show' parameter, with one subplot per behavior

    return returnedBehaviors


if __name__ == '__main__':
    files = getFilesToProcess()
    filenames = [os.path.basename(files[x]) for x in range(0, len(files))]

    for numFile in range(0, len(files)):
        print(f"{files[numFile]} => {filenames[numFile]}")

    ### DEFINE CONSTANTS ###
    # start = {}
    # stop = {}
    timeBinsDuration = int(input("Enter the TIMEBIN for ALL the files (1min =  1800 frames / 1h = 108000 frames):"))

    if len(files) == 0:
        print("NO FILE TO PROCESS !!!!!")
    # if len(files) >= 1:
        # for filename in filenames:
        #     start[filename] = int(input(f"Enter the STARTING frame for {filename}:"))
        #     stop[filename] = int(input(f"Enter the ENDING frame for {filename}:"))
        # # filename = input("Enter the filename for the .csv")
        #
        #     nbTimebins = int((stop[filename] - start[filename]) / timeBinsDuration)
        #     print(f"There are {nbTimebins} timebins of {timeBinsDuration} frames (= {timeBinsDuration/30/60} minutes) "
        #           f"between frames: Start={start[filename]} and Stop={stop[filename]}].")

    timingInFrames = open("start-times-data-extraction_in-frames - Cages 4,7,10,11.txt", "r")  # OPEN the txt file with start and stop frames
    lines = timingInFrames.readlines()  # Call the lines of the file with lines[x]

    count = 0
    countLines = 0

    for file in files:
        print("******")
        print(f"The current Count is : {count}")
        print(f"The file path is: {file.title()}")
        filename = filenames[count]
        print(f"The file name is: {filename}")
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        animalNumber = animalPool.getNbAnimals()
        print(f"There are {animalNumber} animals.")

        countLines += 1
        print(f"CountLines={countLines}")
        start = [int(s) for s in lines[countLines].split() if s.isdigit()][0]
        print(f"Start frame is {start}")
        countLines += 1
        print(f"CountLines={countLines}")
        stop = [int(s) for s in lines[countLines].split() if s.isdigit()][0]
        print(f"Start frame is {stop}")
        countLines += 1

        nbTimebins = int((stop - start) / timeBinsDuration)
        print(f"There are {nbTimebins} timebins of {timeBinsDuration} frames (= {timeBinsDuration / 30 / 60} minutes) "
              f"between frames: Start={start} and Stop={stop}].")

        if animalNumber >= 1:
            behavioralEventsForOneAnimal = ["Move", "Move isolated", "Rearing", "Rear isolated",
                                            "Stop isolated", "WallJump", "SAP"]
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

        # if animalNumber >= 1:
        #     behavioralEvents = ["Move", "Move isolated", "Rearing", "Rear isolated", "Stop isolated", "WallJump",
        #                         "SAP"]
        # if animalNumber >= 2:
        #     behavioralEvents.append("Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
        #                             "Side by side Contact, opposite way", "Social approach", "Social escape",
        #                             "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated",
        #                             "Train2", "Group2", "Move in contact", "Rear in contact")
        # if animalNumber >= 3:
        #     behavioralEvents.append("Group3", "Group 3 break", "Group 3 make")
        # if animalNumber >= 4:
        #     behavioralEvents.append("Group4", "Group 4 break", "Group 4 make")
        # print("The behaviors extracted are:", behavioralEvents)

        # animalPool.loadDetection(start=start, end=stop)  # load the detection between Start and Stop
        # print("*** General parameters for the animals *** ")
        # for animal in animalPool.getAnimalList():
        #     print("******")
        #     print("Animal RFID:", animal.RFID, "/ Animal Id:", animal.baseId)
        #     print("Animal name:", animal.name, "/ Animal genotype:", animal.genotype)
        #     nbOfDetectionFrames = len(animal.detectionDictionnary.keys())
        #     timeInSecond = nbOfDetectionFrames / 30  # 30 fps
        #     print("Detection time: ", timeInSecond, "seconds.")
        #     print("Distance traveled in arena (cm): ", animal.getDistance(tmin=start, tmax=stop))  # distance traveled

        # Keep the behavioral dictionaries in a list:
        allBehaviorsDico = {}
        listOfBehDicos = []

        # Export the Infos (Mean, Std, ...) of the Behaviors for each timebin:
        dicoOfBehInfos = {
            "start_frame": None,
            "stop_frame": None,
            "name": None,
            "idA": None,
            "idB": None,
            "idC": None,
            "idD": None,
            "totalLength": None,
            "meanLength": None,
            "medianLength": None,
            "numberOfEvents": None,
            "stdLength": None,
            "CI95_low": None,
            "CI95_up": None
        }

        allBehaviorsInfo = {}
        listOfBehInfos = [None]*nbTimebins
        dfOfBehInfos = pd.DataFrame()
        listOfBehInfosDico = []

        for bin in range(nbTimebins):
            startBin = start + bin * timeBinsDuration
            stopBin = startBin + timeBinsDuration
            print(f"************* Loading data for bin #{bin} *************")
            now = datetime.datetime.now()
            print("Current date and time : ")
            print(now.strftime("%Y-%m-%d %H:%M:%S"))
            print(f"*** Start frame = {startBin} // Stop frame = {stopBin} ***")
            animalPool.loadDetection(start=startBin, end=stopBin)  # load the detection for the different bins

            listOfBehDicos.append([startBin, stopBin])
            listOfBehInfos[bin] = [startBin, stopBin]
            dicoOfBehInfos["start_frame"] = startBin
            dicoOfBehInfos["stop_frame"] = stopBin

            #### For 1+ ANIMAL ####
            if animalNumber >= 1:
                for behavior in behavioralEventsForOneAnimal:
                    print("**** ", behavior, " ****")
                    behavioralList1 = []

                    for a in animalPool.getAnimalsDictionnary():
                        eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin, maxFrame=stopBin)
                        behavioralList1.append(eventTimeLine)
                        # behavioralList1.append(animalPool.getAnimalWithId(a).RFID)
                        # print(animalPool.getAnimalWithId(a).RFID)

                        listOfBehDicos.extend(behavioralList1)  # List of Behavioral dictionaries with the different timebins

                        behavioralData = computeBehaviorsData(eventTimeLine)
                        dicoOfBehInfos.update(behavioralData)

                        # Creates a dataFrame with the behavioral Infos from the dictionary:
                        index = [0]
                        dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                        dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                        listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins

                    # plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)

                    allBehaviorsDico[behavior] = behavioralList1

                    listOfBehInfosDico.append(dfOfBehInfosTemp)
                    # dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

            #### FOR 2+ ANIMALS ####
            if animalNumber >= 2:
                for behavior in behavioralEventsForTwoAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList2 = []

                    for a in animalPool.getAnimalsDictionnary():
                        if behavior == "Move in contact" or behavior == "Rear in contact":  # Just idA in those behaviors
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a,
                                                          minFrame=startBin, maxFrame=stopBin)
                            behavioralList2.append(eventTimeLine)
                            # behavioralList2.append(animalPool.getAnimalWithId(a).RFID)
                            listOfBehDicos.extend(behavioralList2)

                            behavioralData = computeBehaviorsData(eventTimeLine)
                            dicoOfBehInfos.update(behavioralData)

                            # Creates a dataFrame with the behavioral Infos from the dictionary:
                            index = [0]
                            dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                            dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                            listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins

                        else:
                            for b in animalPool.getAnimalsDictionnary():
                                if a == b:
                                    continue
                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b,
                                                              minFrame=startBin, maxFrame=stopBin)
                                behavioralList2.append(eventTimeLine)
                                # behavioralList2.append(animalPool.getAnimalWithId(a).RFID)

                                listOfBehDicos.extend(behavioralList2)  # List of Behavioral dicos with the different timebins

                                behavioralData = computeBehaviorsData(eventTimeLine)
                                dicoOfBehInfos.update(behavioralData)

                                # Creates a dataFrame with the behavioral Infos from the dictionary:
                                index = [0]
                                dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                                dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                                listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins

                    allBehaviorsDico[behavior] = behavioralList2
                    listOfBehInfosDico.append(dfOfBehInfosTemp)

            #### FOR 3+ ANIMALS ####
            if animalNumber >= 3:
                for behavior in behavioralEventsForThreeAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList3 = []

                    for a in animalPool.getAnimalsDictionnary():
                        # There is ONLY ONE animal making or braking a group of 3 or 4 mice
                        if behavior == "Group 3 make" or behavior == "Group 3 break":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin, maxFrame=stopBin)
                            behavioralList3.append(eventTimeLine)
                            # behavioralList3.append(animalPool.getAnimalWithId(a).RFID)

                            listOfBehDicos.extend(behavioralList3) # List of Behavioral dicos with the different timebins

                            behavioralData = computeBehaviorsData(eventTimeLine)
                            dicoOfBehInfos.update(behavioralData)

                            # Creates a dataFrame with the behavioral Infos from the dictionary:
                            index = [0]
                            dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                            dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                            listOfBehInfos[bin].extend(behavioralData.items())  # listOfBehInfos[bin].extend(behavioralData.items())

                        else:
                            for b in animalPool.getAnimalsDictionnary():
                                if a == b:
                                    continue
                                for c in animalPool.getAnimalsDictionnary():
                                    if a == c or b == c:
                                        continue
                                    eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c,
                                                                  minFrame=startBin, maxFrame=stopBin)
                                    behavioralList3.append(eventTimeLine)

                                    listOfBehDicos.extend(behavioralList3)  # List of Behavioral dicos with the different timebins

                                    behavioralData = computeBehaviorsData(eventTimeLine)
                                    dicoOfBehInfos.update(behavioralData)

                                    # Creates a dataFrame with the behavioral Infos from the dictionary:
                                    index = [0]
                                    dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                                    dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                                    listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins

                    allBehaviorsDico[behavior] = behavioralList3
                    listOfBehInfosDico.append(dfOfBehInfosTemp)
                    # dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

            #### FOR 4 ANIMALS ####
            if animalNumber >= 4:
                for behavior in behavioralEventsForFourAnimals:
                    print("**** ", behavior, " ****")
                    behavioralList4 = []

                    for a in animalPool.getAnimalsDictionnary():
                        # There is ONLY ONE animal making or braking a group of 3 or 4 mice
                        if behavior == "Group 4 make" or behavior == "Group 4 break":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin, maxFrame=stopBin)
                            behavioralList4.append(eventTimeLine)
                            # behavioralList4.append(animalPool.getAnimalWithId(a).RFID)

                            listOfBehDicos.extend(behavioralList4) # List of Behavioral dicos with the different timebins

                            behavioralData = computeBehaviorsData(eventTimeLine)
                            dicoOfBehInfos.update(behavioralData)

                            # Creates a dataFrame with the behavioral Infos from the dictionary:
                            index = [0]
                            dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                            dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                            listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins
                        else:
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
                                                                      minFrame=startBin, maxFrame=stopBin)
                                        behavioralList4.append(eventTimeLine)

                                        listOfBehDicos.extend(behavioralList4)  # List of Behavioral dicos with the different timebins:

                                        behavioralData = computeBehaviorsData(eventTimeLine)
                                        dicoOfBehInfos.update(behavioralData)

                                        # Creates a dataFrame with the behavioral Infos from the dictionary:
                                        index = [0]
                                        dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                                        dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                                        listOfBehInfos[bin].extend(behavioralData.items())  # List of Behavioral infos with the different timebins

                    allBehaviorsDico[behavior] = behavioralList4

                    listOfBehInfosDico.append(dfOfBehInfosTemp)
                    # dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)
        count += 1

        dfOfBehInfos.to_csv(f"{filename}.csv")
        print("CSV File Created !")

    # Say it's done !
    print("!!! End of analysis !!!")