#!/usr/bin/env python

import cv2
from FrameProcessor import FrameProcessor
from helpers import combine

class EdgeDetector( FrameProcessor ):

    _color = ( 25, 100, 200 )

    _lower_thresh = 10.0   # good starting point is 10
    _upper_thresh = 200.0  # good starting point is 200

    def __init__( self ):
        super( EdgeDetector, self ).__init__()
        self._name = "Edge Detector"
        self._testBool = False

    def prop_ThreshLower_set( self, thresh ):
        self._lower_thresh = thresh

    def prop_ThreshLower_get( self):
        return self._lower_thresh

    def prop_ThreshUpper_set( self, thresh ):
        self._upper_thresh = thresh

    def prop_ThreshUpper_get( self ):
        return self._upper_thresh

    def type_ThreshUpper( self ):
        return int

    def type_ThreshLower( self ):
        return int

    def processFrame( self, frame_in ):
        self._activeRects = []
        self._boundingBox = []

        gray = cv2.cvtColor( frame_in, cv2.COLOR_BGR2GRAY )
        gray = cv2.equalizeHist( gray )
        edged_g = cv2.Canny( gray, self._lower_thresh, self._upper_thresh )

        # draw edges on main image
        color = self._color
        pen_thickness = 4
        ( contours, _ ) = cv2.findContours( edged_g.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        cv2.drawContours( frame_in, contours, -1, color, pen_thickness )

        # draw a bounding box
        # NOTE: skip the bounding box since it's not very useful
        '''
        contours = sorted( contours, key = cv2.contourArea, reverse = True )#[ : 20 ]
        for r in contours:
            rect = cv2.boundingRect( r )    # rect is x, y, w, h
            self._activeRects.append( rect )

            cv2.rectangle( frame_in, ( rect[ 0 ], rect[ 1 ] ), ( rect[ 0 ] + rect[ 2 ], rect[ 1 ] + rect[ 3 ] ), ( 0, 255, 255 ), 1 )

        self._boundingBox = combine( self._activeRects )
        '''
        return frame_in


