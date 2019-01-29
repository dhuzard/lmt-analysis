'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from database.Chronometer import Chronometer
from database.Animal import *
from database.Detection import *
from database.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from database.Event import *
from database.Measure import *

def reBuildEvent( connection, tmin=None, tmax=None ):
    
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    
    contact = {}
    for idAnimalA in range( 1 , 5 ):
        for idAnimalB in range( 1 , 5 ):
            if ( idAnimalA == idAnimalB ):
                continue
            contact[idAnimalA, idAnimalB] = EventTimeLine( connection, "Contact", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ) #fait une matrice de tous les contacts à deux possibles

    for idAnimalA in range( 1 , 5 ):
        
        for idAnimalB in range( 1 , 5 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            for idAnimalC in range( 1 , 5 ):
                if( idAnimalA == idAnimalC ):
                    continue
                if( idAnimalB == idAnimalC ):
                    continue
                
                for idAnimalD in range( 1 , 5 ):
                    if( idAnimalA == idAnimalD ):
                        continue
                    if( idAnimalB == idAnimalD ):
                        continue
                    if( idAnimalC == idAnimalD ):
                        continue
                
                    eventName = "Group3"        
                    print ( eventName )
                    
                    groupTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , idAnimalC , None , loadEvent=False )
                    
                    result={}
                    
                    dicAB = contact[ idAnimalA , idAnimalB ].getDictionnary()
                    dicAC = contact[ idAnimalA , idAnimalC ].getDictionnary()
                    dicAD = contact[ idAnimalA , idAnimalD ].getDictionnary()
                    dicBC = contact[ idAnimalB , idAnimalC ].getDictionnary()
                    dicBD = contact[ idAnimalB , idAnimalD ].getDictionnary()
                    dicCD = contact[ idAnimalC , idAnimalD ].getDictionnary()
                    
                    for t in dicAB.keys():
                        if ( t in dicAC or t in dicBC ):
                            if ( t in dicAD or t in dicBD or t in dicCD ):
                                continue
                            else:
                                result[t]=True
                    
                    for t in dicAC.keys():   
                        if ( t in dicBC ):
                            if ( t in dicAD or t in dicBD or t in dicCD ):
                                continue
                            else:
                                result[t]=True
                    
                groupTimeLine.reBuildWithDictionnary( result )
                
                groupTimeLine.endRebuildEventTimeLine(connection)
                    
        
    # log process
    from database.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Nest3" , tmin=tmin, tmax=tmax )
               
                    
    print( "Rebuild event finished." )
        
    