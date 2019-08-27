'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached


class Train2:
    def __init__(self, idA, idB):
        self.idA = idA
        self.idB = idB


def flush(connection):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Train3")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    ''' use pool cache if available '''
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    '''
    three animals are following each others with nose-to-anogenital contacts
    animals are moving
    
    this is a combination of Train2 events (train2 events must be calculated before this event)
    '''

    # deleteEventTimeLineInBase(connection, "Train3" )

    ''' build a list of train 2 for each time point '''

    time = {}
    train3 = {}

    for idAnimalA in range(1, 5):
        for idAnimalB in range(1, 5):
            if (idAnimalA == idAnimalB):
                continue
            train2TimeLine = EventTimeLineCached(connection, file, "Train2", idAnimalA, idAnimalB, minFrame=tmin,
                                                 maxFrame=tmax)
            for t in train2TimeLine.getDictionnary():
                train = Train2(idAnimalA, idAnimalB)

                if (not t in time):
                    time[t] = []

                # print ( t , ":" , train.idA , " -> ", train.idB , "*" )
                time[t].append(train)

    for t in time:
        trainList = time[t]

        for trainSource in trainList:
            for trainTarget in trainList:
                if (trainSource == trainTarget):
                    continue

                isValid = ""
                ''' test chain link between train2 events '''

                if trainSource.idB == trainTarget.idA:

                    id1 = trainSource.idA
                    id2 = trainSource.idB
                    id3 = trainTarget.idB

                    if not (id1, id2, id3) in train3:
                        train3[id1, id2, id3] = {}

                    train3[id1, id2, id3][t] = True

                    isValid = ": validated train 3"
                # print ( t , ":" , trainSource.idA , " -> ", trainSource.idB, "--->", trainTarget.idA , " -> ", trainTarget.idB , isValid )

    ''' save data '''

    for idAnimalA in range(1, 5):
        for idAnimalB in range(1, 5):
            for idAnimalC in range(1, 5):
                if (idAnimalA, idAnimalB, idAnimalC) in train3:
                    trainTimeLine = EventTimeLine(None, "Train3", idAnimalA, idAnimalB, idAnimalC, loadEvent=False)

                    trainTimeLine.reBuildWithDictionnary(train3[idAnimalA, idAnimalB, idAnimalC])
                    # trainTimeLine.removeEventsBelowLength( 5 )
                    trainTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Train3", tmin=tmin, tmax=tmax)

    print("Rebuild event finished.")

    return
