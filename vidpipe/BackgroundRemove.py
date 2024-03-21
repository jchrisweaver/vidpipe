#!/usr/bin/env python

from __future__ import division

import cv2
import numpy as np
from FrameProcessor import FrameProcessor

'''
Still in progress....

Filter to remove the background and only keep the parts of the video that are
actively changing.
'''

class BackgroundRemove( FrameProcessor ):

    def __init__ ( self ):
        super( BackgroundRemove, self ).__init__()
        self._name = "Background Remove"

        self._speed = 0.01
        self._avg = None

        self._fgbg = cv2.BackgroundSubtractorMOG()

    def prop_AdaptSpeed_set( self, val ):
        self._speed = float( val / 100 )
        print( self._speed )

    def prop_AdaptSpeed_get( self):
        return int( self._speed * 100 )

    def type_AdaptSpeed( self ):
        return int

    #def prop_AlgorithmV_get( self ):
    #    pass

    def processFrame( self, frame_in ):
        # version 1 - moving average
        if self._avg == None:
            self._avg = np.float32( frame_in )
        cv2.accumulateWeighted( frame_in, self._avg, self._speed )
        background = cv2.convertScaleAbs( self._avg )
        active_area = cv2.absdiff( frame_in, background )

        #version 2 - MOG - Gausian Mixture-based Background/Foreground Segmentation Algorithm
        fgmask = self._fgbg.apply( frame_in ,learningRate = 0.01 )
        #active_area = cv2.bitwise_and( frame_in, frame_in, mask = fgmask )

        return fgmask

