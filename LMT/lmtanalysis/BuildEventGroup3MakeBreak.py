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
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached


def flush(connection):
    """ flush event in database """
    deleteEventTimeLineInBase(connection, "Group 3 make")
    deleteEventTimeLineInBase(connection, "Group 3 break")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    pool = AnimalPool()
    pool.loadAnimals(connection)
    # pool.loadDetection(start = tmin, end = tmax)

    ''' load contact matrix '''
    contact = {}
    group3In = {}
    group3Out = {}

    for idAnimalA in range(1, 5):
        contact[idAnimalA] = EventTimeLineCached(connection, file, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax)
        group3In[idAnimalA] = EventTimeLine(connection, "Group 3 make", idAnimalA, loadEvent=False)
        group3Out[idAnimalA] = EventTimeLine(connection, "Group 3 break", idAnimalA, loadEvent=False)

    ''' process group '''
    for idAnimalA in range(1, 5):
        for idAnimalB in range(1, 5):
            for idAnimalC in range(1, 5):

                ''' check impossible combination (avoid 2 animals with same id) '''
                test = {idAnimalA: True, idAnimalB: True, idAnimalC: True}
                if not len(test.keys()) == 3:
                    continue

                group3 = EventTimeLineCached(connection, file,
                                             "Group3", idAnimalA, idAnimalB, idAnimalC,
                                             minFrame=tmin, maxFrame=tmax)

                eventList = group3.getEventList()

                for event in eventList:
                    t = event.startFrame - 1

                    if not contact[idAnimalA].hasEvent(t):
                        group3In[idAnimalA].addPunctualEvent(t)

                    if not contact[idAnimalB].hasEvent(t):
                        group3In[idAnimalB].addPunctualEvent(t)

                    if not contact[idAnimalC].hasEvent(t):
                        group3In[idAnimalC].addPunctualEvent(t)

                    t = event.endFrame + 1

                    if not contact[idAnimalA].hasEvent(t):
                        group3Out[idAnimalA].addPunctualEvent(t)

                    if not contact[idAnimalB].hasEvent(t):
                        group3Out[idAnimalB].addPunctualEvent(t)

                    if not contact[idAnimalC].hasEvent(t):
                        group3Out[idAnimalC].addPunctualEvent(t)

    ''' save all '''
    for idAnimal in range(1, 5):
        group3In[idAnimal].endRebuildEventTimeLine(connection)
        group3Out[idAnimal].endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Group3 Make Break", tmin=tmin, tmax=tmax)

    print("Rebuild event finished.")
