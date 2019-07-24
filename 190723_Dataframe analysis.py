import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('tkAgg')
import csv

import sqlite3

from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine


if __name__ == '__main__':
    """ behavioralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                        "Side by side Contact, opposite way", "Social approach", "Social escape", "Approach contact",
                        "Approach rear", "Break contact", "Get away", "FollowZone Isolated", "Train2", "Group2",
                        "Group3", "Group 3 break", "Group 3 make", "Group4", "Group 4 break", "Group 4 make",
                        "Huddling", "Move isolated", "Move in contact", "Nest3", "Nest4", "Rearing", "Rear isolated",
                        "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "USV seq"] """

    files = getFilesToProcess()

    for file in files:
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        animalNumber = animalPool.getNbAnimals()
        print("There are", animalNumber, "animals.")

        if animalNumber == 4:
            behavioralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                "Side by side Contact, opposite way", "Social approach", "Social escape",
                                "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated",
                                "Train2", "Group2", "Group3", "Group 3 break", "Group 3 make", "Group4",
                                "Group 4 break", "Group 4 make", "Move isolated", "Move in contact",
                                "Nest3", "Nest4", "Rearing",  "Rear isolated", "Rear in contact", "Stop isolated",
                                "WallJump", "Water Zone", "USV seq"]
        if animalNumber == 3:
            behavioralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                "Side by side Contact, opposite way", "Social approach", "Social escape",
                                "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated",
                                "Train2", "Group2", "Group3", "Group 3 break", "Group 3 make",
                                "Move isolated", "Move in contact", "Rearing", "Rear isolated",
                                "Rear in contact", "Stop isolated", "WallJump", "Water Zone", "USV seq"]
        if animalNumber == 2:
            behavioralEvents = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                "Side by side Contact, opposite way", "Social approach", "Social escape",
                                "Approach contact", "Approach rear", "Break contact", "Get away", "FollowZone Isolated",
                                "Train2", "Group2", "Move isolated", "Move in contact", "Rearing",
                                "Rear isolated", "Rear in contact", "Stop isolated", "WallJump", "Water Zone"]
        if animalNumber == 1:
            behavioralEvents = ["Move isolated", "Rearing", "Rear isolated", "Stop isolated", "WallJump", "Water Zone"]

        animalPool.loadDetection(start=0, end=None)  # load the detection within the time specified
        animalPool.filterDetectionByInstantSpeed(0, 60)  # filter detection by animalSpeed: 0-60cm/s

    for animal in animalPool.animalDictionnary.keys():
        print("Animal ", animal, ":")
        for event in behavioralEvents:
            # print("Event:", event)
            eventTimeLine = EventTimeLine(connection, event, idA=animal)

            eventDurationList = eventTimeLine.getEventDurationList()
            numberOfEvents = eventTimeLine.getNumberOfEvent(minFrame=None, maxFrame=None)
            nbEvents = eventTimeLine.getNbEvent()
            maxEventLength = eventTimeLine.getMaxEventLength()
            minEventLength = eventTimeLine.getMinEventLength()
            minT = eventTimeLine.getMinT()
            maxT = eventTimeLine.getMaxT()
            meanEventLength = eventTimeLine.getMeanEventLength()
            # medianEventLength = eventTimeLine.getMedianEventLength()
            standardDeviationEventLength = eventTimeLine.getStandardDeviationEventLength()
            # totalDurationEvent = eventTimeLine.getTotalDurationEvent(tmin=minT, tmax=maxT)
            totalLength = eventTimeLine.getTotalLength()

            if nbEvents == 0:
                print("NO", event, "for animal", animal, "!!!")
                print("********")
            else:
                print("eventTimeLine:", eventTimeLine)
                # print("numberOfEvents:", numberOfEvents)
                print("nbEvents:", nbEvents)
                print("maxEventLength:", maxEventLength)
                print("minEventLength:", minEventLength)
                print("minT:", minT)
                print("maxT:", maxT)
                print("meanEventLength:", meanEventLength)
                print("standardDeviationEventLength:", standardDeviationEventLength)
                # print("totalDurationEvent:", totalDurationEvent)
                print("totalLength:", totalLength)

                print("********")
                print(event, "duration list:")
                print(eventDurationList)
                print("********")
