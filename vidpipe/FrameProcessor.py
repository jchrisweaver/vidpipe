#!/usr/bin/env python

import numpy as np

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

class FrameProcessor( QObject ):
    propStartsWith = "prop_"
    propEndsWithSetter = "_set"
    propEndsWithGetter = "_get"
    propTypeStartsWith = "type_"

    _activeRects = []
    _boundingBox = []

    _color = ( 255, 255, 255 )

    def __init__ ( self ):
        super( FrameProcessor, self ).__init__()
        self._name = "Frame Processor"
        self._enabled = False

    def loadConfig( self, config ):
        print( ">>>>>>>>>>>TODO: Load configuration" )

    def saveConfig( self, config ):
        print( ">>>>>>>>>>>TODO: Save configuration" )

    def color( self ):
        return self._color

    @property
    def name( self ):
        return self._name

    def processFrame( self, frame_in ):
        return frame_in

    def prop_Enabled_get( self ):
        return self._enabled

    def prop_Enabled_set( self, value ):
        if type( value ) != bool and value != True and value != False:
            raise TypeError( "Enabled must be either True or False" )
        self._enabled = value
        print( "Setting %s to %s" % ( self.name, value ) )

    def type_Enabled( self ):
        return bool

    def getBoundingBox( self ):
        return self._boundingBox # CAREFUL!!: returns (x1, y1, x2, y2) NOT x, y, w, h

    def getRects( self ):
        return self._activeRects

# Ignore below.  Only test code follows.....
if __name__ == '__main__':
    import inspect
    print( "Testing...." )

    fp = FrameProcessor()

    print( "Name is %s" % fp.name )

    try:
        fp.enabled = 1
    except TypeError:
        print( "Caught ValueError exception on setting to int" )

    try:
        fp.enabled = "True"
    except TypeError:
        print( "Caught ValueError exception on setting to string" )

    fp.enabled = True
    print( "Setting to true. Did it work?: %s" % ( fp.enabled == True ) )

    fp.enabled = False
    print( "Setting to false. Did it work?: %s" % ( fp.enabled == False ) )

    print( "Getting options:" )
    attribs = [ funct.replace( FrameProcessor.propStartsWith, "" ) for funct in dir( fp ) if callable( getattr( fp, funct ) ) and funct.startswith( FrameProcessor.propStartsWith ) ]
    print( "\t", [ ftn.replace( FrameProcessor.propEndsWithSetter, "" ) for ftn in attribs if ftn.endswith( FrameProcessor.propEndsWithSetter ) ] )
    print( "\t", [ ftn.replace( FrameProcessor.propEndsWithGetter, "" ) for ftn in attribs if ftn.endswith( FrameProcessor.propEndsWithGetter ) ] )

    print( "Finished" )

