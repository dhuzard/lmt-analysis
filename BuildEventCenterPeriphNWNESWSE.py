'''
Created on 29 May 2019

@author: Dax
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


def flush(connection):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Zone Center ")
    deleteEventTimeLineInBase(connection, "Zone Periphery")
    deleteEventTimeLineInBase(connection, "Zone NW")
    deleteEventTimeLineInBase(connection, "Zone NE")
    deleteEventTimeLineInBase(connection, "Zone SW")
    deleteEventTimeLineInBase(connection, "Zone SE")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    """ use the pool provided or create it """
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)
    """
    Event Center
    - the animal is in the center zone of the cage
    center zone: xa=149, xb=363, ya=318, yb=98

    Event Periphery
    - the animal is at the periphery of the cage (opposite event from Center)
    
    Event NW
    - the animal is in the North-West zone of the cage: xa=0, xb=250, ya=0, yb=250
    
    Event NE
    - the animal is in the North-East zone of the cage: xa=250, xb=500, ya=0, yb=250
    
    Event SW
    - the animal is in the South-West zone of the cage: xa=0, xb=250, ya=250, yb=500
    
    Event SE
    - the animal is in the South-East zone of the cage: xa=250, xb=500, ya=250, yb=500
    """

    for idAnimalA in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalA])

        eventNameCenter = "Zone Center"
        print("Animal in the center zone")

        eventNamePeriphery = "Zone Periphery "
        print("Animal in the periphery zone")

        eventNameNW = "Zone NW"
        print("Animal in the NW zone")

        eventNameNE = "Zone NE"
        print("Animal in the NE zone")

        eventNameSW = "Zone SW"
        print("Animal in the SW zone")

        eventNameSE = "Zone SE"
        print("Animal in the SE zone")

        centerZoneTimeLine = EventTimeLine(None, eventNameCenter, idAnimalA, None, None, None, loadEvent=False)
        peripheryZoneTimeLine = EventTimeLine(None, eventNamePeriphery, idAnimalA, None, None, None, loadEvent=False)
        NWZoneTimeLine = EventTimeLine(None, eventNameNW, idAnimalA, None, None, None, loadEvent=False)
        NEZoneTimeLine = EventTimeLine(None, eventNameNE, idAnimalA, None, None, None, loadEvent=False)
        SWZoneTimeLine = EventTimeLine(None, eventNameSW, idAnimalA, None, None, None, loadEvent=False)
        SEZoneTimeLine = EventTimeLine(None, eventNameSE, idAnimalA, None, None, None, loadEvent=False)

        resultCenter = {}
        resultPeriphery = {}
        resultNW = {}
        resultNE = {}
        resultSW = {}
        resultSE = {}

        animalA = pool.animalDictionnary[idAnimalA]
        # print ( animalA )
        dicA = animalA.detectionDictionnary

        for t in dicA.keys():

            if dicA[t].isInZone(xa=149, xb=363, ya=318, yb=98) is True: # in Center?
                resultCenter[t] = True
            else: # in Periph ?
                resultPeriphery[t] = True

            if dicA[t].isInZone(xa=0, xb=250, ya=250, yb=0) is True: # in NW ?
                resultNW[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=250, yb=0) is True: # in NE ?
                resultNE[t] = True
            elif dicA[t].isInZone(xa=0, xb=250, ya=500, yb=250) is True: # in SW ?
                resultSW[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=500, yb=250) is True: # in SE ?
                resultSE[t] = True

        centerZoneTimeLine.reBuildWithDictionnary(resultCenter)
        centerZoneTimeLine.endRebuildEventTimeLine(connection)

        peripheryZoneTimeLine.reBuildWithDictionnary(resultPeriphery)
        peripheryZoneTimeLine.endRebuildEventTimeLine(connection)

        NWZoneTimeLine.reBuildWithDictionnary(resultNW)
        NWZoneTimeLine.endRebuildEventTimeLine(connection)
        print("resultNW: ", resultNW)
        NEZoneTimeLine.reBuildWithDictionnary(resultNE)
        NEZoneTimeLine.endRebuildEventTimeLine(connection)

        SWZoneTimeLine.reBuildWithDictionnary(resultSW)
        SWZoneTimeLine.endRebuildEventTimeLine(connection)

        SEZoneTimeLine.reBuildWithDictionnary(resultSE)
        SEZoneTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Center Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Periphery Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NW Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NE Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SW Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SE Zone", tmin=tmin, tmax=tmax)

    print("Rebuild event locations (center, periph, NW...) done.")
