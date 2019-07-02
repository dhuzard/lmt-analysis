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

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine


def flush( connection ):
    """ flush event in database """
    deleteEventTimeLineInBase(connection, "SAP")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None, showGraph=False):
    """ use the pool provided or create it"""
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    for idAnimalA in pool.animalDictionnary:
        animal = pool.animalDictionnary[idAnimalA]
        SAPTimeLine = EventTimeLine(connection, "SAP", idAnimalA, minFrame=tmin, maxFrame=tmax, loadEvent=False)

        # f = animal.getCountFramesSpecZone( start , start+oneMinute*30 , xa=143, ya=190, xb=270, yb=317 )
        result = animal.getSapDictionnary(tmin, tmax)

        SAPTimeLine.reBuildWithDictionnary(result)
        SAPTimeLine.endRebuildEventTimeLine(connection)
        # animal.clearDetection()

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event SAP", tmin=tmin, tmax=tmax)

    print("Rebuild SAP events finished.")
