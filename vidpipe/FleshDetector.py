#!/usr/bin/env python


# http://bytefish.de/blog/opencv/skin_color_thresholding/
# http://spottrlabs.blogspot.com/2012/01/super-simple-skin-detector-in-opencv.html
# http://movidius.tumblr.com/post/3763161383/realtime-skin-detector-in-opencv

import cv2
import numpy as np

from FrameProcessor import FrameProcessor

from helpers import combine

class FleshDetector( FrameProcessor ):

    _color = ( 128, 255, 128 )
    _version = 1    # setup for differnt algorithms

    #_lower = [ 0, 48, 80 ]
    #_upper = [ 20, 255, 255 ]

    _lower = [ 120, 30, 100 ]
    _upper = [ 255, 140, 150 ]

    # works better for brown skin
    #_lower = [ 0, 50, 80 ]
    #_upper = [ 18, 255, 255 ]

    _decayTime = 20
    _decayCntr = 0

    def prop_AlgVersion_set( self, val ):
        # TODO: error check
        self._version = val # only version 1 and 2 are valid, see processFrame

    def prop_AlgVersion_get( self):
        return self._version

    def type_AlgVersion( self ):
        return int

    def prop_LowerBound_set( self, val ):
        # TODO: error check
        self._lower = val
        self.lower = np.array( self._lower, dtype = "uint8" )

    def prop_LowerBound_get( self):
        return self._lower

    def type_LowerBound( self ):
        return tuple

    def prop_UpperBound_set( self, val ):
        # TODO: error check
        self._upper = val
        self.upper = np.array( self._upper, dtype = "uint8" )

    def prop_UpperBound_get( self):
        return self._upper

    def type_UpperBound( self ):
        return tuple

    def __init__( self ):
        super( FleshDetector, self ).__init__()
        self._name = "Flesh Detector"

        self.lower = np.array( self._lower, dtype = "uint8" )
        self.upper = np.array( self._upper, dtype = "uint8" )

        # YCrCb
        #self.lower = np.array( [ 0, 133, 77 ], dtype = "uint8" )
        #self.upper = np.array( [ 255, 173, 127 ], dtype = "uint8" )

    def processFrame( self, frame_in ):
        self._activeRects = []
        self._boundingBox = []

        # error check, just in case
        if self._version < 1 or self._version > 2:
            return frame_in

        #converted = cv2.cvtColor( frame_in, cv2.COLOR_BGR2YCR_CB )

        # version 1
        if self._version == 1:
            converted = cv2.cvtColor( frame_in, cv2.COLOR_BGR2HSV )
            skinMask = cv2.inRange( converted, self.lower, self.upper )

        # version 2 NOTE: this version is exactly the same process, just done differently
        if self._version == 2:
            converted = cv2.cvtColor( frame_in, cv2.COLOR_BGR2HSV )
            h, w, _ = converted.shape
            hue = np.zeros( ( h, w ), np.uint8 )
            sat = np.zeros( ( h, w ), np.uint8 )
            val = np.zeros( ( h, w ), np.uint8 )
            hue[ :, : ] = converted[ :, :, 0 ]
            sat[ :, : ] = converted[ :, :, 1 ]
            val[ :, : ] = converted[ :, :, 2 ]

            # assume that skin has a Hue between 0 to 18 (out of 180), and Saturation above 50, and Brightness above 80.
            hueMask = cv2.inRange( hue, 0, 18 )
            satMask = cv2.inRange( sat, 50, 255 )
            valMask = cv2.inRange( val, 80, 255 )

            skinMask = cv2.bitwise_and( hueMask, satMask )
            skinMask = cv2.bitwise_and( valMask, skinMask )

        # draw edges on main image
        color = self._color
        pen_thickness = 1
        ( _, cnts, _ ) = cv2.findContours( skinMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        cnts = sorted( cnts, key = cv2.contourArea, reverse = True )[ : 20 ]
        cv2.drawContours( frame_in, cnts, -1, color, pen_thickness )

        # draw bounding boxes
        for r in cnts:
            rect = cv2.boundingRect( r )    # rect is x, y, w, h
            self._activeRects.append( rect )

            cv2.rectangle( frame_in, ( rect[ 0 ], rect[ 1 ] ), ( rect[ 0 ] + rect[ 2 ], rect[ 1 ] + rect[ 3 ] ), ( 0, 255, 255 ), 1 )

        self._boundingBox = combine( self._activeRects )

        #return skinMask # return the mask created that shows the skin - TODO: push this to the GUI
        return frame_in


