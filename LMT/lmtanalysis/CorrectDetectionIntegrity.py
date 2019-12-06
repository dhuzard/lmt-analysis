"""
@author: Fab

In case of a nest, for instance, 2 animals can be seen as one detection. Which is wrong.
In that case, only one animal is observed and this should not be considered in other labeling.

The purpose of this code is to remove those faulty situations by switching the identity of animals involved in
such situation to 'anonymous'.

This script should not be ran if there is occlusion in the scene and if it is normal to loose the detection
of an animal from time to time. This script assumes that all animals should be detected all the time.

WARNING: 
This script alters the lmtanalysis:
After running this script, all detections at which all identities are not recognized will be switched to anonymous !
"""

import sqlite3
from time import *

from psutil import virtual_memory

from EventTimeLineCache import disableEventTimeLineCache, flushEventTimeLineCache
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.FileUtil import getFilesToProcess


def loadDetectionMap(connection, idAnimalA, start=None, end=None):
    chrono = Chronometer("Correct detection integrity: Load detection map")
    print("processing animal ID: {}".format(idAnimalA))

    result = {}

    cursor = connection.cursor()
    query = "SELECT FRAMENUMBER FROM DETECTION WHERE ANIMALID={}".format(idAnimalA)

    if start is not None:
        query += " AND FRAMENUMBER>={}".format(start)
    if end is not None:
        query += " AND FRAMENUMBER<={}".format(end)

    print("The SQLite query is:", query)
    cursor.execute(query)

    rows = cursor.fetchall()
    cursor.close()

    for row in rows:
        frameNumber = row[0]
        result[frameNumber] = True

    print(" detections loaded in {} seconds.".format(chrono.getTimeInS()))

    return result


def correct(connection, tmin=None, tmax=None):
    pool = AnimalPool()
    pool.loadAnimals(connection)
    # pool.loadDetection(start=tmin, end=tmax)

    c = connection.cursor()
    if tmin is None:
        query = "SELECT MIN(FRAMENUMBER) FROM FRAME"
        c.execute(query)
        minFrames = c.fetchall()
        for minFrame in minFrames:
            tmin = minFrame[0]

    if tmax is None:
        query = "SELECT MAX(FRAMENUMBER) FROM FRAME"
        c.execute(query)
        maxFrames = c.fetchall()
        for maxFrame in maxFrames:
            tmax = maxFrame[0]

    """ Get the number of expected animals.
    If there is not all detections expected, switch all to anonymous """
    validDetectionTimeLine = EventTimeLine(None, "IDs integrity ok", None, None, None, None, loadEvent=False)
    validDetectionTimeLineDictionnary = {}

    detectionTimeLine = {}
    for idAnimal in pool.getAnimalsDictionnary():
        detectionTimeLine[idAnimal] = loadDetectionMap(connection, idAnimal, tmin, tmax)

    for t in range(tmin, tmax + 1):
        valid = True
        for idAnimal in detectionTimeLine.keys():
            if not (t in detectionTimeLine[idAnimal]):
                valid = False
        if valid:
            validDetectionTimeLineDictionnary[t] = True
    # The 'validDetectionTimeLineDictionnary' contains all the times when the detection is valid!

    """ Rebuild detection set """
    cursor = connection.cursor()
    for idAnimal in detectionTimeLine.keys():
        for t in range(tmin, tmax + 1):
            if t in detectionTimeLine[idAnimal]:
                if not (t in validDetectionTimeLineDictionnary):  # If t is not valid
                    # Dax: ANIMALID is set to NULL (=> 'Anonymous')
                    query = "UPDATE `DETECTION` SET `ANIMALID`=NULL WHERE `FRAMENUMBER`='{}';".format(t)
                    # print("Rebuild detection Query:", query)
                    cursor.execute(query)

    connection.commit()
    cursor.close()
    validDetectionTimeLine.reBuildWithDictionnary(validDetectionTimeLineDictionnary)
    validDetectionTimeLine.endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Correct detection integrity", tmin=tmin, tmax=tmax)

    print("Correct detection finished.")


if __name__ == '__main__':
    files = getFilesToProcess()

    for file in files:
        print("Processing file", file)
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        correct(connection)

    print("******* ALL JOBS DONE !!! *******")