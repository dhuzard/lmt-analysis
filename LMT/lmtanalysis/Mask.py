'''
Created on 12 sept. 2017

@author: Fab
'''

import math
from lmtanalysis.Measure import *
import zlib

# matplotlib fix for mac
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


class Mask:
    """
    Binary mask of an animal at a given t.
    """

    def __init__(self, x, y, w, h, maskDataZipped, color):

        self.pointsY = []
        self.pointsX = []
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.unzip(maskDataZipped)
        self.color = color

    def showMask(self, color=None, ax=None):
        """
        show the mask in a figure
        """
        if color is None:
            color = self.color

        if ax is None:
            fig, ax = plt.subplots()
            ax.scatter(self.pointsX, self.pointsY, c=color)
            plt.show()
        else:
            ax.scatter(self.pointsX, self.pointsY, c=color)

    def unzip(self, maskDataZipped):
        # re fill 0 and put space instead of : separator    
        s = maskDataZipped.split(":")
        s2 = ""
        for value in s:
            if len(value) == 1:
                s2 += "0"
            s2 += value + " "

        # print ( s2 )
        # print ("************")
        b = bytearray.fromhex(s2)

        # print("uncompressed: ")
        uncompressed = zlib.decompress(b)

        index = 0
        for y in range(self.y, self.y + self.height):
            for x in range(self.x, self.x + self.width):

                if uncompressed[index] == 1:
                    self.pointsX.append(x)
                    self.pointsY.append(-y)

                index += 1
