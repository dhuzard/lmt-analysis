"""
Created on 6 sept. 2017

@author: Fab
"""

import math
import sqlite3
import time
import datetime


def level(data):
    """ similar to level in R """
    dico = {}
    for entry in data:
        dico[entry] = True
    return sorted(dico.keys())


def pixelToCm(nbPixel):
    return nbPixel * 10 / 57


def getMinTMaxTAndFileNameInput():
    tmin = int(input("tMin : "))
    tmax = int(input("tMax : "))
    text_file_name = input("File name : ")
    text_file_name = text_file_name + ".txt"
    text_file = open(text_file_name, "w")

    return tmin, tmax, text_file


def getFileNameInput():
    text_file_name = input("File name : ")
    text_file_name = text_file_name + ".txt"
    text_file = open(text_file_name, "w")

    return text_file


def convert_to_d_h_m_s(frames):
    """ Return the tuple of days, hours, minutes and seconds. """
    # seconds = frames / 30
    seconds, f = divmod(frames, 30)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds, f


def d_h_m_s_toText(t):
    """ Return the d h m s f as text"""
    return "{} days {} hours {} minutes {} seconds {} frames".format(t[0], t[1], t[2], t[3], t[4])


def getDistanceBetweenPointInPx(x1, y1, x2, y2):
    """ return the distance between two points in pixel """
    distance = math.hypot(x1 - x2, y1 - y2)
    return distance


def getNumberOfFrames(file):
    """ Returns the number of frames for a given experiment (a SQLite file) """
    connection = sqlite3.connect(file)
    c = connection.cursor()
    query = "SELECT MAX(FRAMENUMBER) FROM FRAME";
    c.execute(query)
    numberOfFrames = c.fetchall()

    return int(numberOfFrames[0][0])


def getStartInDatetime(file):
    """ Returns the start of a given experiment in a datetime format """
    connection = sqlite3.connect(file)
    c = connection.cursor()
    query = "SELECT MIN(TIMESTAMP) FROM FRAME";
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        start = datetime.datetime.fromtimestamp(row[0] / 1000)

    return start


def getEndInDatetime(file):
    """ Returns the end of a given experiment in a datetime format """
    connection = sqlite3.connect(file)
    c = connection.cursor()
    query = "SELECT MAX(TIMESTAMP) FROM FRAME";
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        end = datetime.datetime.fromtimestamp(row[0] / 1000)

    return end


def getDatetimeFromFrame(file, frame):
    """ Return a datetime from a given frame """
    connection = sqlite3.connect(file)
    c = connection.cursor()
    query = "SELECT TIMESTAMP FROM FRAME WHERE FRAMENUMBER = {}".format(frame);
    # print(query)
    c.execute(query)
    rows = c.fetchall()
    # print(len(rows))
    if len(rows) <= 0:
        print("The entered framenumber is out of range")
        targetDate = 0

    else:
        for row in rows:
            targetDate = datetime.datetime.fromtimestamp(row[0] / 1000)

    return targetDate


def recoverFrame(file, MyDatetime):
    """
    Return the closest FRAMENUMBER from a given datetime
    The datetime must have this format: dd-mm-YYYY hh:mm:ss
    """
    connection = sqlite3.connect(file)
    c = connection.cursor()

    # get datetime of 1st and last frames
    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER=1";
    c.execute(query)
    all_rows = c.fetchall()
    startTS = int(int(all_rows[0][1]) / 1000)
    startDate = datetime.datetime.fromtimestamp(startTS).strftime('%d-%m-%Y %H:%M:%S')

    query = "SELECT max(FRAMENUMBER) FROM FRAME";
    c.execute(query)
    all_rows = c.fetchall()
    maxFrame = all_rows[0][0]

    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE FRAMENUMBER={}".format(maxFrame);
    c.execute(query)
    all_rows = c.fetchall()
    endTS = int(int(all_rows[0][1]) / 1000)
    endDate = datetime.datetime.fromtimestamp(endTS).strftime('%d-%m-%Y %H:%M:%S')

    # print ( file )
    # print ( "Start date of record : " + startDate )
    # print ( "End date of record : " + endDate )

    # print(datetime.utcfromtimestamp(startTS).strftime('%Y/%m/%d %H:%M:%S'))
    print(MyDatetime)

    timeStamp = time.mktime(datetime.datetime.strptime(MyDatetime, "%Y-%m-%d %H:%M:%S").timetuple()) * 1000

    print("TimeStamp * 1000 is : " + str(timeStamp))
    print("Searching closest frame in database....")
    query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME WHERE TIMESTAMP>{} AND TIMESTAMP<{}".format(timeStamp - 10000,
                                                                                                  timeStamp + 10000);

    c.execute(query)
    all_rows = c.fetchall()

    closestFrame = 0
    smallestDif = 100000000

    for row in all_rows:
        ts = int(row[1])
        dif = abs(ts - timeStamp)
        if dif < smallestDif:
            smallestDif = dif
            closestFrame = int(row[0])

    print("Closest Frame in selected database is: " + str(closestFrame))
    print("Distance to target: " + str(smallestDif) + " milliseconds")
    return closestFrame
