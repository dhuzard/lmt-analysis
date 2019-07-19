"""
Created on 29 May 2019

@author: Dax
"""

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
    """ flush event in database """
    deleteEventTimeLineInBase(connection, "Zone CenterFab")
    deleteEventTimeLineInBase(connection, "Zone CenterDax")
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
    Event Center:
    - the animal is in the center zone of the cage
    "centerFab" zone: xa=149, xb=363, ya=318, yb=98
    Dax: Use 'New' "centerDax": xa=185, xb=327, ya=280.5, yb=135.5 ?

    Event Periphery:
    - the animal is at the periphery of the cage (opposite event from Center)
    
    Event NW:
    - the animal is in the North-West zone of the cage: xa=0, xb=250, ya=0, yb=250
    
    Event NE:
    - the animal is in the North-East zone of the cage: xa=250, xb=500, ya=0, yb=250
    
    Event SW:
    - the animal is in the South-West zone of the cage: xa=0, xb=250, ya=250, yb=500
    
    Event SE:
    - the animal is in the South-East zone of the cage: xa=250, xb=500, ya=250, yb=500
    """

    for idAnimalA in pool.animalDictionnary.keys():
        print(pool.animalDictionnary[idAnimalA])

        eventNameCenterFab = "Zone CenterFab"
        print("Animal in the center zone (Fabrice version)")

        eventNameCenterDax = "Zone CenterDax"
        print("Animal in the center zone (Dax version)")

        eventNamePeripheryFab = "Zone Periphery Fab "
        print("Animal in the periphery zone (Fabrice version)")

        eventNamePeripheryDax = "Zone Periphery Dax "
        print("Animal in the periphery zone (Dax version)")

        eventNameNW = "Zone NW"
        print("Animal in the NW zone")

        eventNameNE = "Zone NE"
        print("Animal in the NE zone")

        eventNameSW = "Zone SW"
        print("Animal in the SW zone")

        eventNameSE = "Zone SE"
        print("Animal in the SE zone")

        centerFabZoneTimeLine = EventTimeLine(None, eventNameCenterFab, idAnimalA, None, None, None, loadEvent=False)
        centerDaxZoneTimeLine = EventTimeLine(None, eventNameCenterDax, idAnimalA, None, None, None, loadEvent=False)
        peripheryFabZoneTimeLine = EventTimeLine(None, eventNamePeripheryFab, idAnimalA, None, None, None, loadEvent=False)
        peripheryDaxZoneTimeLine = EventTimeLine(None, eventNamePeripheryDax, idAnimalA, None, None, None, loadEvent=False)
        NWZoneTimeLine = EventTimeLine(None, eventNameNW, idAnimalA, None, None, None, loadEvent=False)
        NEZoneTimeLine = EventTimeLine(None, eventNameNE, idAnimalA, None, None, None, loadEvent=False)
        SWZoneTimeLine = EventTimeLine(None, eventNameSW, idAnimalA, None, None, None, loadEvent=False)
        SEZoneTimeLine = EventTimeLine(None, eventNameSE, idAnimalA, None, None, None, loadEvent=False)
        NW2ZoneTimeLine = EventTimeLine(None, eventNameNW, idAnimalA, None, None, None, loadEvent=False)
        NE2ZoneTimeLine = EventTimeLine(None, eventNameNE, idAnimalA, None, None, None, loadEvent=False)
        SW2ZoneTimeLine = EventTimeLine(None, eventNameSW, idAnimalA, None, None, None, loadEvent=False)
        SE2ZoneTimeLine = EventTimeLine(None, eventNameSE, idAnimalA, None, None, None, loadEvent=False)

        resultCenterFab = {}
        resultCenterDax = {}
        resultPeripheryFab = {}
        resultPeripheryDax = {}
        resultNW = {}
        resultNE = {}
        resultSW = {}
        resultSE = {}
        resultNW2 = {}
        resultNE2 = {}
        resultSW2 = {}
        resultSE2 = {}

        animalA = pool.animalDictionnary[idAnimalA]
        # print ( animalA )
        dicA = animalA.detectionDictionnary

        for t in dicA.keys():
            if dicA[t].isInZone(xa=149, xb=363, ya=318, yb=98) is True:  # Check if animal is in Center (Fab version)?
                resultCenterFab[t] = True
            else:  # in Periphery ?
                resultPeripheryFab[t] = True

            if dicA[t].isInZone(xa=185, xb=327, ya=280.5, yb=135.5) is True:  # Check if animal in Center (Dax version)?
                resultCenterDax[t] = True
            else:  # in Periphery ?
                resultPeripheryDax[t] = True

            if dicA[t].isInZone(xa=0, xb=250, ya=250, yb=0) is True:  # in NW ?
                resultNW[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=250, yb=0) is True:  # in NE ?
                resultNE[t] = True
            elif dicA[t].isInZone(xa=0, xb=250, ya=500, yb=250) is True:  # in SW ?
                resultSW[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=500, yb=250) is True:  # in SE ?
                resultSE[t] = True

            if dicA[t].isInZone(xa=114, xb=256, ya=208, yb=63) is True:  # in NW ?
                resultNW2[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=250, yb=0) is True:  # in NE ?
                resultNE2[t] = True
            elif dicA[t].isInZone(xa=0, xb=250, ya=500, yb=250) is True:  # in SW ?
                resultSW2[t] = True
            elif dicA[t].isInZone(xa=250, xb=500, ya=500, yb=250) is True:  # in SE ?
                resultSE2[t] = True

        centerFabZoneTimeLine.reBuildWithDictionnary(resultCenterFab)
        centerFabZoneTimeLine.endRebuildEventTimeLine(connection)

        peripheryFabZoneTimeLine.reBuildWithDictionnary(resultPeripheryFab)
        peripheryFabZoneTimeLine.endRebuildEventTimeLine(connection)

        centerDaxZoneTimeLine.reBuildWithDictionnary(resultCenterDax)
        centerDaxZoneTimeLine.endRebuildEventTimeLine(connection)

        peripheryDaxZoneTimeLine.reBuildWithDictionnary(resultPeripheryDax)
        peripheryDaxZoneTimeLine.endRebuildEventTimeLine(connection)

        NWZoneTimeLine.reBuildWithDictionnary(resultNW)
        NWZoneTimeLine.endRebuildEventTimeLine(connection)
        print("resultNW: ", resultNW)

        NEZoneTimeLine.reBuildWithDictionnary(resultNE)
        NEZoneTimeLine.endRebuildEventTimeLine(connection)

        SWZoneTimeLine.reBuildWithDictionnary(resultSW)
        SWZoneTimeLine.endRebuildEventTimeLine(connection)

        SEZoneTimeLine.reBuildWithDictionnary(resultSE)
        SEZoneTimeLine.endRebuildEventTimeLine(connection)

        NW2ZoneTimeLine.reBuildWithDictionnary(resultNW2)
        NW2ZoneTimeLine.endRebuildEventTimeLine(connection)

        NE2ZoneTimeLine.reBuildWithDictionnary(resultNE2)
        NE2ZoneTimeLine.endRebuildEventTimeLine(connection)

        SW2ZoneTimeLine.reBuildWithDictionnary(resultSW2)
        SW2ZoneTimeLine.endRebuildEventTimeLine(connection)

        SE2ZoneTimeLine.reBuildWithDictionnary(resultSE2)
        SE2ZoneTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Center Fab Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Periphery Fab Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Center Dax Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event Periphery Dax Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NW Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NE Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SW Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SE Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NW2 Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event NE2 Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SW2 Zone", tmin=tmin, tmax=tmax)
    t.addLog("Build Event SE2 Zone", tmin=tmin, tmax=tmax)

    print("Rebuild event locations (center, periph, corners (NW...)) done.")
