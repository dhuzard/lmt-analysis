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


def distHeadHead(detA, detB):
    """ Returns the distance between the Head of 2 animals """
    hx = detA.frontX
    hy = detA.frontY
    bx = detB.frontX
    by = detB.frontY

    if hx == -1 or hy == -1 or bx == -1 or by == -1:
        return 100000

    return math.hypot(hx - bx, hy - by)  # Euclidean distance


def flush(connection):
    """ flush event in database """
    deleteEventTimeLineInBase(connection, "Oral-oral Contact")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    """ use the pool provided or create it """
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    ''' deleteEventTimeLineInBase(connection, "Oral-oral Contact" ) '''

    '''
    contactDico = {}
    approachDico = {}
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( idAnimalA == idAnimalB ):
                continue
            
            contactDico[idAnimalA, idAnimalB] = EventTimeLine( connection, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax )
            approachDico[idAnimalA, idAnimalB] = EventTimeLine( connection, "Social approach", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de toutes les aproches à deux possibles
    '''

    for idAnimalA in range(1, pool.getNbAnimals() + 1):
        for idAnimalB in range(1, pool.getNbAnimals() + 1):
            if idAnimalA == idAnimalB:
                continue

            ''' MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD '''

            eventName = "Oral-oral Contact"
            print(eventName)

            result = {}
            animalA = pool.animalDictionnary.get(idAnimalA)
            animalB = pool.animalDictionnary.get(idAnimalB)

            OralOralTimeLine = EventTimeLine(None, eventName, idAnimalA, idAnimalB, loadEvent=False)

            for t in animalA.detectionDictionnary.keys():
                if t in animalB.detectionDictionnary:
                    detA = animalA.detectionDictionnary[t]
                    detB = animalB.detectionDictionnary[t]

                    if distHeadHead(detA, detB) < MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD:
                        result[t] = True

            OralOralTimeLine.reBuildWithDictionnary(result)
            OralOralTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Build Event Oral Oral Contact", tmin=tmin, tmax=tmax)

    print("Rebuild Oral-Oral contact event finished.")
