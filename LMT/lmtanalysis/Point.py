"""
Created on 6 sept. 2017

@author: Fab
"""

import math


class Point:
    """
    Defines a point with X and Y as coordinates
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distanceTo(self, p):
        return math.hypot(self.x-p.x, self.y-p.y)
