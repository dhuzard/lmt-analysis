"""
Created on 6 sept. 2017

@author: Fab
"""

import math


class Rectangle:

    def __init__(self, pA, pB):
        self.pA = pA
        self.pB = pB

    def isPointInside(self, p):
        if self.pA.x <= p.x <= self.pB.x and self.pA.y <= p.y <= self.pB.y:
            return True
        return False
