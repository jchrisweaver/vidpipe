#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np

from FrameProcessor import FrameProcessor
from helpers import draw_rect, combine

class SimpleMotionDetection( FrameProcessor ):

    _color = ( 200, 80, 80 )

    # 10 x 10 grid
    _X = 10    # 64 pixels
    _Y = 10    # 48 pixels
    _threshold = 0.05   # 5% value change - LOWER is more sensitive
    # the percence difference between this frame and the prev frame that counts as motion

    _scale = 100000

    _frameCount = 0     # always running frame count

    def __init__( self ):
        super( SimpleMotionDetection, self ).__init__()
        self._name = "SimpleMotion Filter"

        self._prev_frame_sum_of_values = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 4.2 bill

        self._enabled = False
        self._watchFrame_enabled = False
        self._watchFrame = ( 0, 8 ) # NOTE: Order is Y, X

        self._graph_ringbuf_MovingAverage = np.zeros( 100, np.float32 )
        self._graph_ringbuf = np.zeros( 100, np.uint8 )

    def prop_ChangeThresh_set( self, thresh ):
        self._threshold = thresh / 1000

    def prop_ChangeThresh_get( self):
        return self._threshold * 1000

    def type_ChangeThresh( self ):
        return int

    def prop_Scale_set( self, scale ):
        self._scale = scale
        self._graph_ringbuf = np.zeros( 100, np.uint8 )
        self._frameCount = 0

    def prop_Scale_get( self):
        return self._scale

    def type_Scale( self ):
        return int

    def prop_Watch_set( self, val ):
        # TODO: error check
        self._watchFrame = tuple( val )[ :: -1 ]
        self._graph_ringbuf_MovingAverage = np.zeros( 100, np.float32 )
        self._graph_ringbuf = np.zeros( 100, np.uint8 )
        self._frameCount = 0

    def prop_Watch_get( self):
        return self._watchFrame[ :: -1 ]

    def type_Watch( self ):
        return tuple

    def processFrame( self, frame_in ):
        # frame_in is BGR
        # frame_in.shape = ( 480, 640, 3 )

        self._activeRects = []
        self._boundingBox = []

        # divide the frame into X x Y grid
        yjump = int( 480 / self._Y )
        xjump = int( 640 / self._X )

        # brute force a background
        #draw_rect( frame_in, ( 0, 0 ), ( 640, 480 ), ( 0, 0, 0 ) )

        for y in range( 0, self._Y ):
            for x in range( 0, self._X ):

                # sum for each portion of the grid
                # TODO: change to count the number of pixels change to monitor a % of area changed
                #   sum is mixing both degree of change AND area changed
                sum_of_values = int( frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ].sum() )

                # calc a delta for each portion after Z # of frames - 1st derivitate, change over time
                dev_from_hist = abs( sum_of_values - self._prev_frame_sum_of_values[ y ][ x ] )

                #if the | delta | < Threshold then blank out that sector
                if dev_from_hist < self._threshold * self._prev_frame_sum_of_values[ y ][ x ]:
                    frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ] = 0
                else:
                    self._activeRects.append( ( x * xjump, y * yjump, xjump, yjump ) )

                if self._watchFrame_enabled and self._watchFrame == ( y, x ):
                    self._graph_ringbuf = np.roll( self._graph_ringbuf, 1 )
                    graphValue = yjump * dev_from_hist / self._scale
                    self._graph_ringbuf[ 0 ] = graphValue

                    movAverage = ( graphValue + self._frameCount * self._graph_ringbuf_MovingAverage[ 0 ] ) / ( self._frameCount + 1 )
                    self._graph_ringbuf_MovingAverage = np.roll( self._graph_ringbuf_MovingAverage, 1 )
                    self._graph_ringbuf_MovingAverage[ 0 ] = movAverage

                    vis = frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ]

                    # plot the values and the moving average
                    for xx in range( 1, xjump ):
                        cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf[ xx ] ) ), ( 255, 255, 0 ), 1 )
                        #cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf_MovingAverage[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf_MovingAverage[ xx ] ) ), ( 0, 25, 255 ), 2 )

                    # show midway mark for refrence
                    cv2.line( vis, ( 0, yjump - int( yjump / 2 ) ), ( xjump - 1, yjump - int( yjump / 2 ) ), ( 128, 128, 128 ), 1 )
                    cv2.line( vis, ( 0, yjump - int( self._graph_ringbuf_MovingAverage[ 0 ] ) ), ( xjump - 1, yjump - int( self._graph_ringbuf_MovingAverage[ 0 ] ) ), ( 0, 25, 255 ), 2 )

                self._prev_frame_sum_of_values[ y ][ x ] = sum_of_values
                last_X = x
            last_Y = y

        self._boundingBox = combine( self._activeRects )

        # return the processed frame to be either passed to the next filter
        # or displayed
        self._frameCount += 1
        return frame_in

