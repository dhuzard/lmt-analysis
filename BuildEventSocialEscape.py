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
from LMT.lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Social escape")


def reBuildEvent(connection, file, tmin=None, tmax=None, pool=None):
    print("STARTING SOCIAL ESCAPE")
    
    ''' use the pool provided or create it'''
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)
    
    nbAnimal = pool.getNbAnimals()

    # loading all the escapes of animals
    getAwayDico = {}
    for idAnimalA in range(1, nbAnimal + 1):
        for idAnimalB in range(1, nbAnimal + 1):
            if idAnimalA == idAnimalB:
                continue
            
            getAwayDico[idAnimalA, idAnimalB] = EventTimeLineCached(connection, file, "Get away",
                                                                    idAnimalA, idAnimalB,
                                                                    minFrame=tmin, maxFrame=tmax)

    #cache mean body len
    twoMeanBodyLen = {}
    for idAnimal in range(1, nbAnimal + 1):
        
        meanBodyLength = pool.animalDictionnary[idAnimal].getMeanBodyLength()
        # init value
        twoMeanBodyLen[idAnimal] = None
        # set value
        if meanBodyLength is not None:
            twoMeanBodyLen[idAnimal] = 2 * meanBodyLength

    for idAnimalA in range(1, nbAnimal + 1):
        for idAnimalB in range(1, nbAnimal + 1):
            if idAnimalA == idAnimalB:
                continue
            
            eventName = "Social escape"        
            print(eventName)
            
            socEscTimeLine = EventTimeLine(None, eventName, idAnimalA, idAnimalB, None, None, loadEvent=False)
                           
            result = {}
            
            dicA = getAwayDico[idAnimalA, idAnimalB].getDictionnary()
            
            twoMeanBodyLengthB = twoMeanBodyLen[idAnimalB]
            
            for t in dicA.keys():
                dist = pool.animalDictionnary[idAnimalA].getDistanceTo(t, pool.animalDictionnary[idAnimalB])
                
                if dist is None:
                    continue
                    
                if 0 <= dist <= twoMeanBodyLengthB:
                    result[t] = True

            socEscTimeLine.reBuildWithDictionnary(result)
            
            socEscTimeLine.endRebuildEventTimeLine(connection)
        
    # log process
    from LMT.lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog("Build Event Social Escape", tmin=tmin, tmax=tmax)

             
    print( "Rebuild Social Escape events finished." )
