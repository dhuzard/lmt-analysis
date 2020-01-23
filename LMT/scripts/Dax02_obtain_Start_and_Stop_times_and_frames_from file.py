"""
Created on 26 August 2019

@author: Dax
"""

import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Util import getStartInDatetime, getEndInDatetime, getDatetimeFromFrame, getNumberOfFrames, recoverFrame
from lmtanalysis.Measure import *

if __name__ == '__main__':
    files = getFilesToProcess()

    timingFile = open("start-times-data-extraction.txt", "r")  # OPEN the txt file with dates and times
    lines = timingFile.readlines()

    exportFile = open("start-times-data-extraction_in-frames.txt", "w")  # Exported File with frames

    counter = 1
    for file in files:
        print("***********")
        print(file)
        print(f"counter = {counter}")

        connection = sqlite3.connect(file)  # connect to database

        startTime = getStartInDatetime(file)
        stopTime = getEndInDatetime(file)
        numberOfFrames = getNumberOfFrames(file)

        print("The SQLlite database starts on", startTime, "and finishes on", stopTime, ".")
        print("There are", numberOfFrames, "frames in the recording.")

        """        
        frame = recoverFrame(file, "2019-08-07 15:55:55")  # The datetime must have this format: "YYYY-MM-DD hh:mm:ss"
        print(frame)
        print(getDatetimeFromFrame(file, frame))
        """

        currentLine = lines[counter]
        # print(currentLine)
        exportFile.write(f"{file.title()}\n")
        # startTemp2 = recoverFrame(file, "2019-08-12 19:00:00")
        startTemp = recoverFrame(file, currentLine.strip())  # .strip() REMOVE THE \n !
        exportFile.write(f"start-frame: {startTemp}\n")

        counter += 1
        print(f"counter = {counter}")
        currentLine = lines[counter]
        stopTemp = recoverFrame(file, currentLine.strip())
        exportFile.write(f"stop-frame: {stopTemp}\n")

        counter += 2
        print(f"counter = {counter}")

        # for x in timingFile:  # Reads the timingFile, line by line
        #     print(x)
        #     Frame = recoverFrame(file, x)

        # startInput = input("When do you want to start the data extraction ('YYYY-MM-DD hh:mm:ss')?")
        # stopInput = input("When do you want to stop the data extraction ('YYYY-MM-DD hh:mm:ss')?")
        # startFrame = recoverFrame(file, startInput)
        # stopFrame = recoverFrame(file, stopInput)
        # print("Those timings correspond to:")
        # print("    - Start-Frame =", startFrame)
        # print("    - Stop-Frame =", stopFrame)

    timingFile.close()
    exportFile.close()
