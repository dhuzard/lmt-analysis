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
    for file in files:
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

        startInput = input("When do you want to start the data extraction ('YYYY-MM-DD hh:mm:ss')?")
        stopInput = input("When do you want to stop the data extraction ('YYYY-MM-DD hh:mm:ss')?")
        startFrame = recoverFrame(file, startInput)
        stopFrame = recoverFrame(file, stopInput)
        print("Those timings correspond to:")
        print("    - Start-Frame =", startFrame)
        print("    - Stop-Frame =", stopFrame)
