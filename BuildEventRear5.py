'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from LMT.lmtanalysis.Chronometer import Chronometer
from LMT.lmtanalysis.Animal import *
from LMT.lmtanalysis.Detection import *
from LMT.lmtanalysis.Measure import *
import numpy as np
from LMT.lmtanalysis.Event import *
from LMT.lmtanalysis.Measure import *
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from LMT.lmtanalysis.EventTimeLineCache import EventTimeLineCached


def flush(connection):
    """
    flush events in database
    """
    deleteEventTimeLineInBase(connection, "Rear isolated")
    deleteEventTimeLineInBase(connection, "Rear in contact")
    deleteEventTimeLineInBase(connection, "Rearing") # Delete the "Rearing" from LMT java code


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    """ use the pool provided or create it """
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    """
    Event Rear5:
    - the animal is rearing
    - distinction between 'rearing in contact' (with one or several animals) and 'rearing isolated' from the others
    """

    contact = {}

    for idAnimalA in pool.animalDictionnary.keys():
        print("animal dico:")
        print(pool.animalDictionnary[idAnimalA])

        contact[idAnimalA] = EventTimeLineCached(connection, file, "Contact", idAnimalA, minFrame=tmin, maxFrame=tmax)
        contactDico = contact[idAnimalA].getDictionnary()

        eventName1 = "Rear isolated"
        eventName2 = "Rear in contact"
        # print("A rears")

        rearSocialTimeLine = EventTimeLine(None, eventName2, idAnimalA, None, None, None, loadEvent=False)
        rearIsolatedTimeLine = EventTimeLine(None, eventName1, idAnimalA, None, None, None, loadEvent=False)

        resultSocial = {}
        resultIsolated = {}

        animalA = pool.animalDictionnary[idAnimalA]
        # print(animalA)
        dicA = animalA.detectionDictionnary

        for t in dicA.keys():
            slope = dicA[t].getBodySlope()

            if slope is None:
                continue

            if abs(slope) < BODY_SLOPE_THRESHOLD:
                continue

            print("At t=", t, " , the slope of the animal is: ", slope)

            if t in contactDico.keys():
                # print("social")
                resultSocial[t] = True

            else:
                # print("isolated")
                resultIsolated[t] = True

        rearSocialTimeLine.reBuildWithDictionnary(resultSocial)
        rearIsolatedTimeLine.reBuildWithDictionnary(resultIsolated)

        rearSocialTimeLine.endRebuildEventTimeLine(connection)
        rearIsolatedTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from LMT.lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Rear5", tmin=tmin, tmax=tmax)

    print("Rebuild event Rear5 finished.")
