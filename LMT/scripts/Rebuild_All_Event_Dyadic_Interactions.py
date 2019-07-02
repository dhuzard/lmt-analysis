"""
Created on 13 sept. 2017

@author: Fab
"""

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis import BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, \
    BuildEventFloorSniffing, BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact, \
    BuildEventOralOralContact, BuildEventApproachRear, BuildEventGroup2, BuildEventOralGenitalContact, BuildEventStop, \
    BuildEventWaterPoint, BuildEventMove, BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP, BuildEventOralSideSequence, BuildEventFight, \
    BuildEventGetAway, BuildEventRearCenterPeriphery, BuildEventCenterPeripheryLocation

from tkinter.filedialog import askopenfilename

if __name__ == '__main__':

    print("Code launched.")

    """ Displays a GUI window to select file(s) """

    files = askopenfilename(title="Choose a set of file to process", multiple=1)

    maxT = 3*oneDay
    '''oneMinute*240'''

    for file in files:
        print(file)
        connection = sqlite3.connect(file)

        BuildDataBaseIndex.buildDataBaseIndex(connection)

        BuildEventDetection.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventOralOralContact.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventOralGenitalContact.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventSideBySide.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventSideBySideOpposite.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventTrain2.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventMove.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventFollowZone.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventRear5.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventSocialApproach.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventSocialEscape.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventApproachRear.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventGroup2.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventStop.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventFloorSniffing.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventWaterPoint.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventApproachContact.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventWallJump.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventSAP.reBuildEvent(connection,  file, tmin=0, tmax=maxT)

        BuildEventOralSideSequence.reBuildEvent(connection, file, tmin=0, tmax=maxT)

        BuildEventFight.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventGetAway.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventRearCenterPeriphery.reBuildEvent(connection, file, tmin=0, tmax=maxT)
        BuildEventCenterPeripheryLocation.reBuildEvent(connection, file, tmin=0, tmax=maxT)

    print("****** ALL JOBS DONE !!! ******")
