"""
Created on 6 sept. 2017

@author: Fab
"""

import sqlite3
import unittest
from time import *
from lmtanalysis.Chronometer import Chronometer

import matplotlib.pyplot as plt
import numpy as np
import statistics as stat
from turtledemo.penrose import start
from lmtanalysis.Measure import *
import sys


class Event:
    """
    An event represents an interval of frames where the event is.
    """

    def __init__(self, startFrame, endFrame):
        self.startFrame = startFrame
        self.endFrame = endFrame

    def duration(self):  # Duration in frames
        return self.endFrame - self.startFrame + 1

    def contain(self, frameNumber):
        return self.startFrame <= frameNumber <= self.endFrame

    def overlapInT(self, start, end):
        """
        XXXX
          XXXX

         YYYY
        YYYYYY
        """
        if start <= self.endFrame and end >= self.startFrame:
            return True
        # if ( end <= self.endFrame and end >= self.startFrame ):
        #    return True
        # if ( start <= self.endFrame and start >= self.startFrame ):
        #    return True
        # case where the start and end are over boundaries of event
        # if ( start <= self.startFrame and end >= self.endFrame ):
        #    return True
        # return False

    def overlapEvent(self, eventCandidate):
        result = self.overlapInT(eventCandidate.startFrame, eventCandidate.endFrame)
        # print ( "Overlap debug: ( {} , {} ) - ( {} , {} ) : {}".format( self.startFrame, self.endFrame , eventCandidate.startFrame, eventCandidate.endFrame, result )  );
        return result

    def shift(self, nbFrame):
        """
        Shifts event of nbFrame
        """
        self.startFrame += nbFrame
        self.endFrame += nbFrame

    def numberOfFrameToEvent(self, eventCandidate):
        """
        provides the distance (in frame) to another event
        if the events do overlap, return 0
        """

        if self.overlapEvent(eventCandidate):
            return 0

        return min(abs(self.startFrame - eventCandidate.endFrame), abs(self.endFrame - eventCandidate.startFrame))

    def __str__(self):
        return "Event\tstart:\t" + str(self.startFrame) + "\tend:\t" + str(self.endFrame)


class EventTimeLine:
    """
    classdocs
    """

    def __init__(self, conn, eventName, idA=None, idB=None, idC=None, idD=None, loadEvent=True, minFrame=None,
                 maxFrame=None, inverseEvent=False, loadEventWithoutOverlapCheck=False):
        """
        Load events:
            where (minFrame <= t <= maxFrame) if applicable
            inverseEvent: inverse all timeline (used to make stop becomes move for instance)
        """

        # check id at 0 to transform them as None ( id will not be considered in query ) (added for USV support).

        if idA == 0:
            idA = None
        if idB == 0:
            idB = None
        if idC == 0:
            idC = None
        if idD == 0:
            idD = None

        # store parameters
        self.idA = idA
        self.idB = idB
        self.idC = idC
        self.idD = idD
        self.eventName = str(eventName)
        self.eventNameWithId = "{} idA:{} idB:{} idC:{} idD:{}".format(eventName, idA, idB, idC, idD)
        # build events
        self.eventList = []

        if loadEvent is False:
            print("Event " + str(eventName) + " created. eventNameWithId = " + str(
                self.eventNameWithId) + " loadEvent: False")
            return

        chrono = Chronometer("Load event " + str(self.eventName))
        c = conn.cursor()

        query = "SELECT * FROM EVENT WHERE NAME='{0}'".format(self.eventName);
        if idA is not None:
            query += " AND IDANIMALA={0}".format(idA)
        if idB is not None:
            query += " AND IDANIMALB={0}".format(idB)
        if idC is not None:
            query += " AND IDANIMALC={0}".format(idC)
        if idD is not None:
            query += " AND IDANIMALD={0}".format(idD)

        '''
        if ( minFrame != None ):
            query += " AND STARTFRAME>={0}".format( minFrame )

        if ( maxFrame != None ):
            query += " AND ENDFRAME<={0}".format( maxFrame )
        '''

        if minFrame is not None:
            query += " AND ENDFRAME>={0}".format(minFrame)
        if maxFrame is not None:
            query += " AND STARTFRAME<={0}".format(maxFrame)

        ''' print( query ) '''
        c.execute(query)
        all_rows = c.fetchall()

        if loadEventWithoutOverlapCheck is True:
            if inverseEvent is True:
                print("Warning: inverseEvent option not compatible in loadEventWithoutOverlapCheck")

            for row in all_rows:

                start = row[3]
                end = row[4]

                if minFrame is not None:
                    if start < minFrame or end < minFrame:
                        continue
                if maxFrame is not None:
                    if start > maxFrame or end > maxFrame:
                        continue
                self.eventList.append(Event(start, end))
        else:
            eventBool = {}

            for row in all_rows:
                start = row[3]
                end = row[4]
                for t in range(start, end + 1):

                    if minFrame is not None:
                        if t < minFrame:
                            continue
                    if maxFrame is not None:
                        if t > maxFrame:
                            continue

                    eventBool[t] = True

            if inverseEvent is True:

                if minFrame is None:
                    print("To inverse event, need a minFrame")
                    return
                if maxFrame is None:
                    print("To inverse event, need a maxFrame")
                    return

                for t in range(minFrame, maxFrame + 1):
                    if t in eventBool:
                        eventBool.pop(t)
                    else:
                        eventBool[t] = True

            self.reBuildWithDictionnary(eventBool)

        # keyList = sorted(eventBool.keys())

        # start = -1
        # for key in keyList:

        #    if ( start == -1 ):
        #        start = key

        #    if ( eventBool.get( key+1 ) == None ):
        #        self.eventList.append( Event( start, key ) )
        #        start = -1

        print(eventName, " Id(", idA, ",", idB, ",", idC, ",", idD, ") Min/maxFrame: (", minFrame, "/", maxFrame,
              ") Loaded (", len(self.eventList), " records loaded in ", chrono.getTimeInS(), "S )")

    def __str__(self):
        return self.eventName + " Id(" + str(self.idA) + "," + str(self.idB) + "," + str(self.idC) + "," + str(
            self.idD) + ")"

    def saveTimeLine(self, conn):
        c = conn.cursor()
        for event in self.eventList:
            query = "INSERT INTO EVENT (NAME, DESCRIPTION, STARTFRAME, ENDFRAME, IDANIMALA, IDANIMALB, IDANIMALC, IDANIMALD ) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}');".format(
                self.eventName, self.eventNameWithId, event.startFrame, event.endFrame, self.idA, self.idB, self.idC,
                self.idD)
            # print( query )
            c.execute(query)
        conn.commit()

    def addEvent(self, eventToAdd):
        self.eventList.append(eventToAdd)
        self.checkEventHole(eventToAdd.startFrame - 1)
        self.checkEventHole(eventToAdd.endFrame)

        # check merge with existing events
        for event in self.eventList[:]:
            if (event == eventToAdd):
                continue
            if (event.overlapEvent(eventToAdd)):
                self.mergeEvent(event, eventToAdd)

        # TODO: should also check if the new event overlap with existing events.

    def addPunctualEvent(self, frameNumber):
        '''
        Adds an event at frame frameNumber. If an event exists beside, extends it, else creates it.
        '''
        # check if event exists
        if (self.getEventAt(frameNumber) != None):
            return;

        for event in self.eventList[:]:
            if (event.endFrame == frameNumber - 1):
                event.endFrame = frameNumber
                self.checkEventHole(frameNumber)
                return

        for event in self.eventList[:]:
            if (event.startFrame == frameNumber + 1):
                event.startFrame = frameNumber
                self.checkEventHole(frameNumber - 1)
                return

        # create the event

        event = Event(frameNumber, frameNumber)
        self.eventList.append(event)

    def getEventAt(self, frameNumber):
        for event in self.eventList:
            if event.contain(frameNumber):
                return event
        return None

    def checkIfEventListIsOrdered(self):
        '''
        Checks if the eventlist is fully ordered
        '''
        cursor = -1
        previousEvent = None
        for event in self.eventList:
            if (event.startFrame > cursor):
                cursor = event.endFrame
            else:
                print("Check ordered list: problem in list:")
                print("previous event : ", previousEvent)
                print("next (non ordered) event event : ", event)
                return False
            previousEvent = event

        return True

    def getClosestEventFromFrame(self, frameNumber, optimizeAssumingOrderedList=False, constraint=None):
        '''
        returns the closest event from framenumber, and the distance (in frame) to it.
        assumes the eventList has been build by rebuildallevents, which makes them ordered.
        '''
        if (self.hasEvent(frameNumber)):
            # we do have an event for this frame so the distance is 0
            return None, 0

        listToSearchIn = self.eventList

        # pre-fetch events.
        if (optimizeAssumingOrderedList == True):
            listToSearchIn = []
            for event in self.eventList:
                if (event.startFrame < frameNumber):
                    continue
                # we just overtook the best match.
                # we put the current event and the previous one (if it exists) in the list
                currentIndex = self.eventList.index(event)
                listToSearchIn.append(event)
                if (currentIndex > 0):
                    listToSearchIn.append(self.eventList[currentIndex - 1])
                break

        if constraint == "after frame":
            # creates a new list where only events in the future are kept
            updatedList = []
            for event in listToSearchIn:
                if (event.startFrame > frameNumber):
                    updatedList.append(event)
            listToSearchIn = updatedList

        if constraint == "before frame":
            # creates a new list where only events in the past are kept
            updatedList = []
            for event in listToSearchIn:
                if (event.endFrame < frameNumber):
                    updatedList.append(event)
            listToSearchIn = updatedList

        closestEvent = None
        bestDistance = sys.maxsize

        for event in listToSearchIn:

            distanceToStart = abs(frameNumber - event.startFrame)
            distanceToEnd = abs(frameNumber - event.endFrame)
            best = min(distanceToStart, distanceToEnd)

            if (best < bestDistance):
                closestEvent = event
                bestDistance = best

        return closestEvent, bestDistance

    def hasEvent(self, frameNumber):  # Check if the timeline has an event at the frame number specified
        if self.getEventAt(frameNumber) is not None:
            return True
        return False

    def getNumberOfEvent(self, minFrame=None, maxFrame=None):  # Returns the number of events
        nbEvent = 0

        for event in self.eventList:
            takeEvent = True

            if minFrame is not None:
                if event.endFrame < minFrame:
                    takeEvent = False

            if maxFrame is not None:
                if event.startFrame > maxFrame:
                    takeEvent = False

            if takeEvent:
                nbEvent += 1

        return nbEvent

    def getTotalDurationEvent(self, tmin, tmax):
        """
        Returns the total duration between min and max t value.
        """
        duration = 0
        dicEvent = self.getDictionnary()
        for t in range(tmin, tmax + 1):
            if t in dicEvent:
                duration += 1
        return duration

    def getDurationEventInTimeBin(self, tmin=0, tmax=None, binSize=1 * oneMinute):
        '''
        compute the proportion of frames of an event within a given time bin, to calculate the density
        '''
        if (tmax == None):
            tmax = self.getMaxT()

        dicEvent = self.getDictionnary()

        durationEventInBinProportionList = []

        frame = tmin

        while frame < tmax:

            durationEventInBin = 0

            for t in range(frame, frame + binSize):
                if t in dicEvent.keys():
                    durationEventInBin = durationEventInBin + 1

            durationEventInBinProportion = durationEventInBin / binSize

            durationEventInBinProportionList.append(durationEventInBinProportion)

            frame = frame + binSize

        return durationEventInBinProportionList

    def getDictionnary(self, minFrame=None, maxFrame=None):
        frameDico = {}
        for event in self.eventList:
            for t in range(event.startFrame, event.endFrame + 1):
                frameDico[t] = True;

        if minFrame is not None:
            for key in dict(frameDico).keys():
                if key < minFrame:
                    frameDico.pop(key)
        if maxFrame is not None:
            for key in dict(frameDico).keys():
                if key > maxFrame:
                    frameDico.pop(key)

        return frameDico

    def reBuildWithDictionnary(self, eventBool):
        self.eventList.clear()  # Starts with empty eventList
        keyList = sorted(eventBool.keys())  # Key list of the event

        start = -1
        for key in keyList:  # for all events in the list
            if start == -1:
                start = key  # Sets the Start of an event

            if eventBool.get(key + 1) is None:  # the next key is not part of the event
                self.eventList.append(Event(start, key))  # Set the end of the event
                start = -1

    def checkEventHole(self, frameNumber):
        """
        Checks if an event end at a givenFrame, and if another one starts just after. Merge event if found.
        XXX
          T
           XXX
           ==> merge
        """
        eventA = self.getEventAt(frameNumber)
        eventB = self.getEventAt(frameNumber + 1)
        if eventA is None or eventB is None:
            return
        if eventA != eventB:
            self.mergeEvent(eventA, eventB)

    def mergeCloseEvents(self, numberOfFrameBetweenEvent):
        """
        Merges events if they are distant of less or equal than numberOfFrame
        """
        minT = self.getMinT()
        maxT = self.getMaxT()

        if self.getNbEvent() == 0:
            print("No event in timeLine")
            return

        eventDictionnary = self.getDictionnary(minT, maxT)

        nbFrameOutOfEvent = 0
        lastEventEndFrame = minT
        for t in range(minT, maxT + 1):
            # print( "t: " + str(t) )
            if t in eventDictionnary:

                if nbFrameOutOfEvent > 0:
                    if nbFrameOutOfEvent <= numberOfFrameBetweenEvent:
                        # fill
                        for tt in range(lastEventEndFrame, t):
                            # print( "filling " + str( tt ))
                            eventDictionnary[tt] = True

                nbFrameOutOfEvent = 0
                lastEventEndFrame = t
            else:
                nbFrameOutOfEvent += 1

        self.reBuildWithDictionnary(eventDictionnary)

    def mergeEvent(self, eventA, eventB):
        """
        If events are next to each other, merge them. (test A before B and B before A )
        """
        if eventA.endFrame == eventB.startFrame - 1:
            mergedEvent = Event(eventA.startFrame, eventB.endFrame)
            self.eventList.remove(eventA)
            self.eventList.remove(eventB)
            self.eventList.append(mergedEvent)
            return

        if eventB.endFrame == eventA.startFrame - 1:
            mergedEvent = Event(eventB.startFrame, eventA.endFrame)
            self.eventList.remove(eventA)
            self.eventList.remove(eventB)
            self.eventList.append(mergedEvent)
            return

        if (eventA.overlapEvent(eventB)):
            mini = min(eventA.startFrame, eventB.startFrame)
            maxi = max(eventA.endFrame, eventB.endFrame)
            # print ( "mini: " , mini )
            # print ( "maxi: " , maxi )
            mergedEvent = Event(mini, maxi)
            try:
                self.eventList.remove(eventA)
            except:
                pass
            try:
                self.eventList.remove(eventB)
            except:
                pass

            self.eventList.append(mergedEvent)
            return

    def getEventList(self):
        return self.eventList

    def removeEventsOverT(self, maxT):
        for event in self.eventList[:]:
            if event.startFrame > maxT:
                self.eventList.remove(event)

    def removeEventsBelowT(self, maxT):
        for event in self.eventList[:]:
            if event.endFrame < maxT:
                self.eventList.remove(event)

    def keepOnlyEventCommonWithTimeLine(self, timeLineAnd):
        """
        Performs a AND logic with the timeline 'timeLineAnd'
        """
        dico = self.getDictionnary()
        andDico = timeLineAnd.getDictionnary()
        andResult = {}

        for k in dico:
            if k in andDico:
                andResult[k] = True

        self.reBuildWithDictionnary(andResult)

    def removeEventOfTimeLine(self, timeLineToRemove):
        """
        Removes the events that match the timeline 'timeLineToRemove'
        """
        dico = self.getDictionnary()
        removeDico = timeLineToRemove.getDictionnary()

        for k in removeDico:
            dico.pop(k, None)

        self.reBuildWithDictionnary(dico)

    def removeEventsBelowLength(self, maxLen):
        """
        Removes events shorter that 'maxLen'
        """
        for event in self.eventList[:]:
            if event.duration() < maxLen:
                self.eventList.remove(event)

    def printEventList(self):
        print("Event list of {} / {} / nbEvent: {}".format(self.eventName, self.eventNameWithId, len(self.eventList)))
        i = 0
        for event in self.eventList:
            print("[{}] Event ({},{})".format(i, event.startFrame, event.endFrame))
            i += 1

    def getMaxT(self):
        maxT = None
        for event in self.eventList:
            if maxT is None:
                maxT = event.endFrame
            maxT = max(maxT, event.endFrame)
        return maxT

    def getMinT(self):
        minT = None
        for event in self.eventList:
            if minT is None:
                minT = event.startFrame
            minT = min(minT, event.startFrame)
        return minT

    def getNbEvent(self):
        nb = 0
        for _ in self.eventList:
            nb += 1
        return nb

    def getMeanEventLength(self):
        nb = 0
        sum = 0
        for event in self.eventList:
            nb += 1
            sum += event.duration()

        if nb == 0:
            return None
        else:
            return sum / nb

    def getMedianEventLength(self):
        nb = 0
        eventsDurationList = []
        for event in self.eventList:
            nb += 1
            eventsDurationList.append(event.duration())

        if nb == 0:
            return None
        else:
            return stat.median(eventsDurationList)

    def getEventDurationList(self):
        """ Dax (20190724):
        Returns a list with the duration of the events """
        nb = 0
        eventsDurationList = []
        for event in self.eventList:
            nb += 1
            eventsDurationList.append(event.duration())

        if nb == 0:
            return None
        else:
            return eventsDurationList

    def getStandardDeviationEventLength(self):
        durationList = []
        for event in self.eventList:
            durationList.append(event.duration())

        sd = np.std(durationList)
        return sd

    def getMaxEventLength(self):
        maxi = 0
        for event in self.eventList:
            maxi = max(maxi, event.duration())
        return maxi

    def getMinEventLength(self):
        mini = 3 * oneDay
        for event in self.eventList:
            mini = min(mini, event.duration())
        return mini

    def getTotalLength(self):
        sum = 0
        for event in self.eventList:
            sum += event.duration()
        return sum

    def plotEventDurationDistributionHist(self, nbBin=10, title=""):
        data = []
        for event in self.eventList:
            data.append(event.duration())

        plt.figure()
        # ax = plt.subplots()
        plt.hist(data, nbBin)
        plt.xlabel("Event duration (in frames)")
        plt.ylabel("Number of events")

        if title is not None:
            plt.title(title)
        else:
            plt.title(". Hist. of duration of the event: {}".format(self.eventName))

        plt.figtext(.5, .85, "Number of bin: {}".format(nbBin), fontsize=10, ha='center')
        plt.show()

    def plotEventDurationDistributionBar(self, minDuration=None, maxDuration=None, title=""):
        data = []

        for event in self.eventList:
            if minDuration is not None:
                if event.duration() < minDuration:
                    continue
            if maxDuration is not None:
                if event.duration() > maxDuration:
                    continue
            data.append(event.duration())

        # plt.figure()

        data = sorted(data)
        fig, ax = plt.subplots()
        indexes = np.arange(len(data))
        plt.bar(indexes, data, 1)
        # plt.bar( 3,11,1 )

        plt.xlabel("Events (sorted by duration)")
        plt.ylabel("Duration (in frames)")

        if title is not None:
            plt.title(title)
        else:
            plt.title("Duration of events")

        plt.figtext(.5, .85,
                    "Number of events: {} (minDuration={}, maxDuration={})".format(len(data), minDuration, maxDuration),
                    fontsize=10, ha='center')
        plt.show()

    def plotTimeLine(self):
        y = []
        start = []
        end = []

        longestEvent = None

        for event in self.eventList:
            y.append(1)
            start.append(event.startFrame)
            end.append(event.endFrame)

            if longestEvent is None:
                longestEvent = event

            if event.duration() > longestEvent.duration():
                longestEvent = event

        # plt.figure()

        fig, ax = plt.subplots()
        ax.hlines(y, start, end, 'b', lw=4)
        ax.text(0, 1.01, "TimeLine of {}".format(self.eventNameWithId), fontsize=10, ha='left')

        if longestEvent is not None:
            ax.annotate('Longest event ({})'.format(longestEvent.duration()), xy=(longestEvent.startFrame, 1),
                        xytext=(longestEvent.startFrame, 0.95), arrowprops=dict(facecolor='black', shrink=0.05))
        # fig.show()
        plt.show()

    def endRebuildEventTimeLine(self, connection, deleteExistingEvent=False):
        '''
        delete the old event timeline and save the new calculated one in the lmtanalysis
        '''
        if len(self.eventList) == 0:
            print("no event")
        else:
            print("Number of event: ", len(self.eventList))
            print("Mean length of event: ", self.getMeanEventLength())
            print("first event frame: ", self.eventList[0].startFrame)

        if deleteExistingEvent:
            print("Delete old entry in base: " + self.eventName)
            deleteEventTimeLineInBase(connection, self.eventName, self.idA, self.idB, self.idC, self.idD)
        else:
            print("Keep previous entry.")

        print("Saving timeLine: " + self.eventName + " ( " + str(len(self.eventList)) + " events )")
        self.saveTimeLine(connection)

    def deleteEventTimeLineInBase(self, connection):
        deleteEventTimeLineInBase(connection, self.eventName, self.idA, self.idB, self.idC, self.idD)

    def getDensityEventInTimeBin(self, tmin=0, tmax=None, binSize=1 * oneMinute):
        '''
        compute the proportion of frames within the time bin that are included in one event type
        '''
        if tmax is None:
            tmax = self.getMaxT()

        dicEvent = self.getDictionnary()
        densityEventInBinList = []
        frame = tmin

        while frame <= tmax:
            durationEventInBin = 0

            for t in range(frame, frame + binSize):
                if t in dicEvent.keys():
                    durationEventInBin = durationEventInBin + 1

            densityEventInBin = durationEventInBin / binSize
            densityEventInBinList.append(densityEventInBin)
            frame = frame + binSize

        return densityEventInBinList

    def shiftInTime(self, nbFrame):
        '''
        Shifts all events of nbFrames
        '''
        for event in self.eventList:
            event.shift(nbFrame)

    def getLengthDistanceWithTimeLine(self, timeLineCandidate):

        '''
        provides correlation of current event considering overlap with candidate event.
        '''

        foundEventList = []

        print("correlation started")
        chrono = Chronometer("getLengthDistanceWithTimeLine " + timeLineCandidate.eventName)

        maxT = self.getMaxT()
        dico = self.getDictionnary(0, maxT)
        dicoCandidate = timeLineCandidate.getDictionnary(0, maxT)

        mergedDico = {}

        for k in dico.keys():
            if k in dicoCandidate:
                mergedDico[k] = True

        mergedTimeLine = EventTimeLine(None, eventName="Merged", loadEvent=False)
        mergedTimeLine.reBuildWithDictionnary(mergedDico)

        nbEvent = len(self.getEventList())
        # nbMatch = len( newEvent.getEventList() )

        relativityDico = {}  # relativity provide an histogram of the relative location of the even compared to the candidate. 0 is beginning, 1 is end
        for i in range(100):  # zero fill
            relativityDico[i] = 0

        nbMatch = 0
        for event in self.eventList:
            for eventCandidate in mergedTimeLine.eventList:
                if event.overlapEvent(eventCandidate):
                    nbMatch += 1
                    meanEventT = event.startFrame + (event.endFrame - event.startFrame) / 2
                    foundEvent = timeLineCandidate.getEventAt(meanEventT)
                    if foundEvent is not None:
                        foundEventList.append(foundEvent)

                        if foundEvent.duration() > event.duration() * 2:
                            try:
                                a = (meanEventT - foundEvent.startFrame) / foundEvent.duration()
                                a = int(a * 100)
                                if a in relativityDico:
                                    relativityDico[a] += 1
                                else:
                                    relativityDico[a] = 1

                            except:
                                pass

                    break

        print("NB match with " + timeLineCandidate.eventName + " " + str(nbMatch) + " / " + str(
            nbEvent) + " time to compute: " + str(chrono.getTimeInMS()))

        v = 0

        if nbMatch != 0:
            v = nbMatch / nbEvent

        return [v, foundEventList, relativityDico]


def deleteEventTimeLineInBase(connection, eventName, idA=None, idB=None, idC=None, idD=None):
    """
    delete an event in dataBase
    """

    cursor = connection.cursor()
    print("Deleting event {} (idA:{},idB:{},idC:{},idD:{}) from base...".format(eventName, idA, idB, idC, idD))
    query = "DELETE FROM EVENT WHERE NAME=\"{0}\"".format(eventName)
    if idA is not None:
        query += " AND IDANIMALA={0}".format(idA)

    if idB is not None:
        query += " AND IDANIMALB={0}".format(idB)

    if idC is not None:
        query += " AND IDANIMALC={0}".format(idC)

    if idD is not None:
        query += " AND IDANIMALD={0}".format(idD)

    print(query)

    cursor.execute(query)
    connection.commit()
    print("Number of event deleted: {} ".format(cursor.rowcount))


def plotMultipleTimeLine(timeLineList, colorList=None, show=True, minValue=0, title=None):
    """
    Plot multiple timeLines
    """

    yOffset = len(timeLineList) - 1
    maxX = 0

    plt.figure(figsize=(10, yOffset / 2))

    for timeLine in timeLineList:
        start = []
        end = []
        y = []
        if timeLine is not None:
            for event in timeLine.eventList:
                y.append(1 + yOffset)
                start.append(event.startFrame)
                end.append(event.endFrame)
                plt.Rectangle((event.startFrame, 1 + yOffset), event.duration(), 1)
                if event.endFrame > maxX:
                    maxX = event.endFrame

            color = "k"
            if colorList is not None:
                color = colorList[timeLineList.index(timeLine)]

            plt.hlines(y, start, end, color, lw=20)
            plt.text(minValue, 1.0 + yOffset, "{}   ".format(timeLine.eventNameWithId), fontsize=9, ha='right',
                     va='center', label='test')

        yOffset -= 1

        # plt.annotate('Longest event ({})'.format( longestEvent.duration()), xy=( longestEvent.startFrame, 1), xytext=(longestEvent.startFrame, 0.95), arrowprops=dict(facecolor='black', shrink=0.05))

        # ax = plt.gca()
        # ax.relim()

    plt.grid(True, axis='x')
    marginTop = 0.3
    plt.ylim((0 + marginTop, len(timeLineList) + 1 - marginTop))

    # Previous line:
    # plt.axes().get_yaxis().set_visible(False)
    # New line:
    # plt.gca().get_yaxis().set_visible(False)

    plt.subplots_adjust(left=0.2)

    if title is None:
        plt.title("Timeline of an event")
    else:
        plt.title(title)
    # plt.legend()

    if show:
        plt.show(block=True)


class TestEventTimeLine(unittest.TestCase):
    def test_MergeCloseEvents(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(50, 55))
        myEventTimeLine.addEvent(Event(60, 65))

        myEventTimeLine.addEvent(Event(150, 155))
        myEventTimeLine.addEvent(Event(160, 165))

        myEventTimeLine.addEvent(Event(250, 255))
        myEventTimeLine.addEvent(Event(261, 265))
        # xxxxxXooooX
        # 5    5    6
        # 0    5    0
        myEventTimeLine.mergeCloseEvents(4)
        myEventTimeLine.printEventList()
        print("---")

        result = (myEventTimeLine.getNbEvent() == 4)
        self.assertEqual(result, True)

    def test_PuntualEvent(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addPunctualEvent(500)
        myEventTimeLine.printEventList()

        result = (myEventTimeLine.getMinT() == 500 and myEventTimeLine.getMaxT() == 500)
        self.assertEqual(result, True)

    def test_PuntualEvent2(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(51, 99))
        myEventTimeLine.addPunctualEvent(100)
        myEventTimeLine.addPunctualEvent(50)

        myEventTimeLine.printEventList()
        result = (myEventTimeLine.getMinT() == 50 and myEventTimeLine.getMaxT() == 100)
        self.assertEqual(result, True)

    def test_PuntualEvent3(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(100, 200))
        myEventTimeLine.addEvent(Event(50, 99))

        myEventTimeLine.printEventList()
        result = (myEventTimeLine.getMinT() == 50 and myEventTimeLine.getMaxT() == 200)
        self.assertEqual(result, True)

    def test_PuntualEvent4(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(100, 200))
        myEventTimeLine.addEvent(Event(201, 300))

        myEventTimeLine.printEventList()
        result = (myEventTimeLine.getMinT() == 100 and myEventTimeLine.getMaxT() == 300)
        self.assertEqual(result, True)

    def test_PuntualEvent5(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(100, 200))
        # print("test overlap")
        myEventTimeLine.addEvent(Event(150, 250))
        myEventTimeLine.addEvent(Event(50, 160))
        myEventTimeLine.addEvent(Event(50, 400))

        myEventTimeLine.printEventList()
        result = (myEventTimeLine.getMinT() == 50 and myEventTimeLine.getMaxT() == 400 and len(
            myEventTimeLine.eventList) == 1)
        self.assertEqual(result, True)

    def test_PuntualEvent6(self):
        myEventTimeLine = EventTimeLine(None, "testEvent", 1, 2, loadEvent=False)
        myEventTimeLine.addEvent(Event(100, 200))
        # print("test overlap")
        myEventTimeLine.addEvent(Event(202, 300))
        myEventTimeLine.addPunctualEvent(201)

        myEventTimeLine.printEventList()
        result = (myEventTimeLine.getMinT() == 100 and myEventTimeLine.getMaxT() == 300 and len(
            myEventTimeLine.eventList) == 1)
        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()
