"""
Created on 20 May 2019

@author: Dax
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Animal import Animal
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.Util import convert_to_d_h_m_s
from lmtanalysis.Util import d_h_m_s_toText
from lmtanalysis.Measure import oneDay

#Import widgets tk and ttk
import tkinter as tk
from tkinter import ttk
from tkinter import *

import ipywidgets as widgets
from IPython.display import display
from IPython.core.display import HTML

# ********** DEFINE FUNCTIONS ********************************************************

# TODO: OFFRIR CHIRURGIE ESTHETIQUE A LOLO

def getAllEvents(file):
    print("Loading events...")
    connection = sqlite3.connect(file)
    query = "select name from event group by name"
    c = connection.cursor()
    c.execute(query)
    all_rows = c.fetchall()
    header = ["Name"]
    data = []
    for row in all_rows:
        data.append(row[0])
    return data


def printBold(txt, color="black"):
    display(HTML("<font color={}><h1>{}</h1></font>".format(color, txt)))


# def isInvolved(animal):
#     """ Check if the animal is involved in the current query """
#     for k in animalWidget:
#         id = getAnimalBaseIdFromWidget(animalWidget[k].value)
#         if id == animal.baseId:
#             return True
#     return False


def getAnimalIdFromString(value):
    if "Id:1" in value:
        return 1
    if "Id:2" in value:
        return 2
    if "Id:3" in value:
        return 3
    if "Id:4" in value:
        return 4
    return None


def getAnimalBaseIdFromWidget(value):
    if type(value) is Animal:
        return value.baseId
    return None


def click_me():  # Event handler = Start when button is clicked
    actionChoice.configure(text="Clicked !!")
    clickLabel.configure(foreground='red', text='Analysis started...')
    print("The event chosen is = ", eventChosen.get())
    print("Mouse A chosen = ", mouseAChosen.get())
    print("Mouse B chosen = ", mouseBChosen.get())
    print("Mouse C chosen = ", mouseCChosen.get())
    print("Mouse D chosen = ", mouseDChosen.get())

    """
    if startFrameWidget.get() is None:
        minFrame = 0
    else:
        minFrame = int(startFrameWidget.get())*30

    if stopFrameWidget.get() is None:
        maxFrame = animalPool.getMaxDetectionT()
    else:
        maxFrame = int(stopFrameWidget.get())*30
    """

    if len(startFrameWidget.get()) == 0:
        minFrame = 0
    else:
        minFrame = int(startFrameWidget.get()) * 30

    if len(stopFrameWidget.get()) == 0:
        maxFrame = 6 * oneDay
    else:
        maxFrame = int(stopFrameWidget.get()) * 30

    print("Start Time is: ", minFrame/30, " seconds => ", minFrame, " frames")
    print("Stop Time is: ", maxFrame/30, " seconds => ", maxFrame, " frames")

    idA = getAnimalIdFromString(mouseAChosen.get())
    idB = getAnimalIdFromString(mouseBChosen.get())
    idC = getAnimalIdFromString(mouseCChosen.get())
    idD = getAnimalIdFromString(mouseDChosen.get())

    print("idA number: ", idA)
    print("idB number: ", idB)
    print("idC number: ", idC)
    print("idD number: ", idD)

    """ Do EventTimeLine for the specified timebins """

    if len(timebinWidget.get()) == 0: # if not timebin is entered
        timebin = 0
        print("No time bin entered!")
        timebinNumber = 1

        print("Number of time bins: ", timebinNumber)
        print("Start frame is: ", minFrame)
        print("Stop frame is: ", maxFrame)

        eventTimeLine1 = EventTimeLine(connection, eventChosen.get(),
                                       idA=idA, idB=idB, idC=idC, idD=idD,
                                       minFrame=minFrame, maxFrame=maxFrame)

        print("eventTimeLine: ", eventTimeLine1)

        # display number of events:
        print("Number of events : " + str(eventTimeLine1.getNumberOfEvent()))

        # display events in the timeline
        data = []

        for event in eventTimeLine1.eventList:
            data.append([event.startFrame, event.endFrame, event.duration(), event.duration() / 30])
            # print( event.startFrame, event.endFrame, event.duration() )

        df = pd.DataFrame(data=np.array(data), columns=["Start frame", "End frame",
                                                        "Duration (in frames)", "Duration (in seconds)"])
        print(df)

        eventTimeLine1.plotEventDurationDistributionBar()
        print("Distribution of duration of events: Plotted.")
        eventTimeLine1.plotEventDurationDistributionHist()
        print("Distribution of duration of events in bins: Plotted.")
        eventTimeLine1.plotTimeLine()
        print("Timeline of events: Plotted.")

        # Show location of events
        animalPool.loadDetection(start=minFrame, end=maxFrame)
        animalPool.filterDetectionByEventTimeLine(eventTimeLine1)

        if idA is not None:
            animalPool.getAnimalsDictionnary()[idA].plotTrajectory(show=True, title="Animal A, ", color="red")
        if idB is not None:
            animalPool.getAnimalsDictionnary()[idB].plotTrajectory(show=True, title="Animal B, ", color="blue")
        if idC is not None:
            animalPool.getAnimalsDictionnary()[idC].plotTrajectory(show=True, title="Animal C, ", color="green")
        if idD is not None:
            animalPool.getAnimalsDictionnary()[idD].plotTrajectory(show=True, title="Animal D, ", color="orange")

    else:
        timebin = int(timebinWidget.get())*30
        print("The timebin is: ", timebin / 30, " seconds => ", timebin, " frames")
        timebinNumber = int((maxFrame-minFrame)/timebin)
        eventTimeLine = [None] * timebinNumber

        print("Number of time bins: ", timebinNumber)
        print("eventTimeLine is: ", eventTimeLine)

        for i in range(timebinNumber):
            print("Iteration #", i+1)

            startBin = minFrame + i * timebin
            stopBin = minFrame + timebin + i * timebin

            print("Start frame is: ", startBin)
            print("Stop frame is: ", stopBin)

            eventTimeLine[i] = EventTimeLine(connection, eventChosen.get(),
                                             idA=idA, idB=idB, idC=idC, idD=idD,
                                             minFrame=startBin,
                                             maxFrame=stopBin)

            # eventTimeLine = EventTimeLine(connection, eventChosen.get(),
            #                              idA=idA, idB=idB, idC=idC, idD=idD,
            #                             minFrame=minFrame, maxFrame=maxFrame)

            print("eventTimeLine: ", eventTimeLine[i])

            # display number of events:
            print("Number of events : " + str(eventTimeLine[i].getNumberOfEvent()))

            # display events in the timeline
            data = []

            for event in eventTimeLine[i].eventList:
                data.append([event.startFrame, event.endFrame, event.duration(), event.duration()/30])
                # print( event.startFrame, event.endFrame, event.duration() )

            df = pd.DataFrame(data=np.array(data), columns=["Start frame", "End frame",
                                                            "Duration (in frames)", "Duration (in seconds)"])
            print(df)

            eventTimeLine[i].plotEventDurationDistributionBar()
            print("Distribution of duration of events: Plotted.")

            eventTimeLine[i].plotEventDurationDistributionHist()
            print("Distribution of duration of events in bins: Plotted.")

            eventTimeLine[i].plotTimeLine()
            print("Timeline of events: Plotted.")

            # Show location of events
            animalPool.loadDetection(start=minFrame, end=maxFrame)
            animalPool.filterDetectionByEventTimeLine(eventTimeLine[i])

            # for animalKey in animalPool.getAnimalDictionnary():
            #     animal = animalPool.getAnimalDictionnary()[animalKey]
            #
            #     if isInvolved(animal):
            #         print(animal, " involved in ", eventChosen.get())
            #     else:
            #         print(animal, " NOT involved in chosen event")
            #
            #     animal.plotTrajectory()

            if idA is not None:
                animalPool.getAnimalsDictionnary()[idA].plotTrajectory(show=True, title="Animal A, ", color="red")
            if idB is not None:
                animalPool.getAnimalsDictionnary()[idB].plotTrajectory(show=True, title="Animal B, ", color="blue")
            if idC is not None:
                animalPool.getAnimalsDictionnary()[idC].plotTrajectory(show=True, title="Animal C, ", color="green")
            if idD is not None:
                animalPool.getAnimalsDictionnary()[idD].plotTrajectory(show=True, title="Animal D, ", color="orange")


# ********** Select file / Prepare Animals **************
files = getFilesToProcess() #ask for database to process

file = files[0] #Select first database
eventList = getAllEvents(file)
print("The list of events is: ", eventList)

connection = sqlite3.connect(file)
animalPool = AnimalPool()
animalPool.loadAnimals(connection)

#CREATE list of animal IDs
animalList = []
animalList.append(0)
animalIdList = []
animalIdList.append("No animal")

for animalKey in animalPool.getAnimalsDictionnary():
    print("animal key :", animalKey)
    animal = animalPool.getAnimalsDictionnary()[animalKey]
    animalList.append(animal)
    animalIdList.append(animalList[animalKey].baseId)
    print("animal list :", animalList[animalKey])
    print("animal baseID :", animalIdList[animalKey])

# *********** WIDGET ************
widget = tk.Tk() #Create widget
widget.title("Widget: Choose mice and Event to display")

#widget: Choose Event
ttk.Label(widget, text="Choose an event:").grid(row=0, column=0)
#eventWidget = tk.StringVar()
eventChosen = ttk.Combobox(widget, width=30, state='readonly')
eventChosen['values'] = eventList
eventChosen.grid(row=0, column=1)
eventChosen.current(0)

#widgets: Choose between mice
# for mouse in range(4):
#     letter = ['A','B','C','D']
#     ttk.Label(widget, text = "Mouse " + letter[mouse] + ":").grid(row=1+mouse, column=0)
#     miceWidget = tk.StringVar()
#     mouseChosen = ttk.Combobox(widget, width=12, textvariable=eventWidget,
#                            state='readonly')
#     mouseChosen['values'] = (animalIdList)
#     mouseChosen.grid(row=1+mouse, column=1)
#     mouseChosen.current(0)

# widgets of 4 mice manually:
# ttk.Label(widget, text = "Mouse A:").grid(row=1, column=0)
# mice1Widget = tk.StringVar()
# mouse1Chosen = ttk.Combobox(widget, width=60, textvariable= mice1Widget, state='readonly')
# mouse1Chosen['values'] = (animalIdList)
# mouse1Chosen.grid(row=1, column=1)
# mouse1Chosen.current(0)

ttk.Label(widget, text="Mouse A:").grid(row=1, column=0)
mouseAChosen = ttk.Combobox(widget, width=60, state='readonly', values=animalList)
mouseAChosen.grid(row=1, column=1)
mouseAChosen.current(0)

ttk.Label(widget, text="Mouse B:").grid(row=2, column=0)
mouseBChosen = ttk.Combobox(widget, width=60, state='readonly', values=animalList)
mouseBChosen.grid(row=2, column=1)
mouseBChosen.current(0)

ttk.Label(widget, text="Mouse C:").grid(row=3, column=0)
mouseCChosen = ttk.Combobox(widget, width=60, state='readonly', values=animalList)
mouseCChosen.grid(row=3, column=1)
mouseCChosen.current(0)

ttk.Label(widget, text="Mouse D:").grid(row=4, column=0)
mouseDChosen = ttk.Combobox(widget, width=60, state='readonly', values=animalList)
mouseDChosen.grid(row=4, column=1)
mouseDChosen.current(0)

# widget: Choose Start & Stop frames
startFrameValue = StringVar()
ttk.Label(widget, text="Start time in seconds (5min=300s | 1h=3600s):").grid(row=5, column=0)
# textTimeStart = ttk.Label(widget, text="..frf65ed.", textvariable=startFrameValue).grid(row=5, column=3)
startFrameWidget = ttk.Entry(widget)
startFrameWidget.grid(row=5, column=1)
ttk.Label(widget, textvariable="reminder: 30fps").grid(row=5, column=2)

ttk.Label(widget, text="Stop time in seconds (5min=300s | 1h=3600s):").grid(row=6, column=0)
stopFrameWidget = ttk.Entry(widget)
stopFrameWidget.grid(row=6, column=1)

TimebinValue = StringVar()
ttk.Label(widget, text="Timebin (in seconds):").grid(row=7, column=0)
timebinWidget = ttk.Entry(widget)
timebinWidget.grid(row=7, column=1)

# Widget: Choice/validation button
clickLabel = ttk.Label(widget, text="Click to validate =>")
clickLabel.grid(row=8, column=0)
actionChoice = ttk.Button(widget, text="Validate choice", command=click_me)
actionChoice.grid(row=8, column=1)

# ***** Start WIDGET GUI **********
widget.mainloop()
# **********************************
