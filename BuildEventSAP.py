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
import matplotlib.pyplot as plt
import numpy as np
from LMT.lmtanalysis.Event import *
from LMT.lmtanalysis.Measure import *

from LMT.lmtanalysis.Animal import AnimalPool
from LMT.lmtanalysis.Event import EventTimeLine


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

        #f = animal.getCountFramesSpecZone( start , start+oneMinute*30 , xa=143, ya=190, xb=270, yb=317 )
        result = animal.getSapDictionnary(tmin, tmax)
            
        SAPTimeLine.reBuildWithDictionnary(result)
        SAPTimeLine.endRebuildEventTimeLine(connection)
        #animal.clearDetection()

    # log process
    from LMT.lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event SAP", tmin=tmin, tmax=tmax)
               
    print("Rebuild SAP events finished.")
