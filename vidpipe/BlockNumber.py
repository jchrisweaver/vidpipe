#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np

from FrameProcessor import FrameProcessor
from helpers import draw_str, draw_rect

class BlockNumber( FrameProcessor ):

    # 10 x 10 grid
    _X = 10    # 64 pixels
    _Y = 10    # 48 pixels
    _frameCount = 0 # for adding noise

    def __init__( self ):
        super( BlockNumber, self ).__init__()
        self._name = "Block Number"

        # divide the frame into X x Y grid
        self._yjump = 480 / self._Y
        self._xjump = 640 / self._X

    def processFrame( self, frame_in ):
        # frame_in is BGR
        # frame_in.shape = ( 480, 640, 3 )
        self._frameCount += 1

        # brute force a background
        #draw_rect( frame_in, 0, 0, 640, 480, ( 0, 0, 0 ) )

        for y in range( 0, self._Y ):
            for x in range( 0, self._X ):
                # show the block number - (x, y)
                ptx = int( x * self._xjump + .25 * self._xjump )
                pty = int( y * self._yjump + .5 * self._yjump )
                draw_str( frame_in, ptx, pty, "(%d,%d)" % ( x, y ) )

        # return the processed frame to be either passed to the next filter
        # or displayed
        return frame_in

