#!/usr/bin/env python

from __future__ import division
import cv2
import random
import numpy as np

from FrameProcessor import FrameProcessor
from helpers import draw_rect, draw_str

'''
Activity Filter tries to detect periodic activity in each block and then remove that
window of video so it's not passed forward.

Use case:  Ignoring a fan in the background when processing video.
'''

class ActivityFilter( FrameProcessor ):

    # color of the filter and outlines
    _color = ( 200, 180, 255 )

    # 10 x 10 grid
    _X = 10    # 64 pixels
    _Y = 10    # 48 pixels
    _threshold = 0.05   # 5% value change - LOWER is more sensitive

    _threshold2 = 0.10  # 10% value change - HIGHER is more sensitive
    _timeSpan2 = 10 * 10 # 10 seconds, 30 frames
    _frameCount = 0     # always running frame count

    _countMovAvg = 0
    _lastAccum = 0

    # debug flags to add one square with generated noise
    # TODO: make this configurable in the GUI?
    _percentNoise = 1   # percentage of screen to cover with generated noise
    _debugRandomNoise = False
    _debugSteadyNoise = True
    _noiseBlock_x = 3
    _noiseBlock_y = 7

    def __init__( self ):
        super( ActivityFilter, self ).__init__()
        self._name = "Activity Filter"

        self._prev_frame_sum_of_values = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 4.2 bill
        self._histAccum = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 4.2 bill
        self._devAccum = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 4.2 bill
        self._mask = np.zeros( ( self._Y, self._X ), np.bool_ )

        random.seed( 1231 )

        self._enabled = False

        # frame that's processed but is hijacked to show a histogram instead of video
        # useful for debugging values and buffers
        self._watchFrame_enabled = False
        self._watchFrame = ( 0, 8 ) # Set the watch frame at cel x=8, y=0   NOTE: Order is Y, X

        self._graph_ringbuf_MovingAverage = np.zeros( 100, np.float32 )
        self._graph_ringbuf = np.zeros( 100, np.uint8 )
        self._maxhistAccum = 1  # use 1 to avoid divide by zero later

    def prop_ChangeThresh_set( self, thresh ):
        self._threshold = thresh / 1000

    def prop_ChangeThresh_get( self):
        return self._threshold * 1000

    def type_ChangeThresh( self ):
        return int

    def prop_Watch_set( self, val ):
        # TODO: error check
        self._watchFrame = tuple( val )[ :: -1 ]
        self._graph_ringbuf_MovingAverage = np.zeros( 100, np.float32 )
        self._graph_ringbuf = np.zeros( 100, np.uint8 )
        self._maxhistAccum = 1

    def prop_Watch_get( self):
        return self._watchFrame[ :: -1 ]

    def type_Watch( self ):
        return tuple

    def processFrame( self, frame_in ):
        # frame_in is BGR
        # frame_in.shape = ( 480, 640, 3 )
        self._frameCount += 1

        # divide the frame into X x Y grid
        yjump = int( 480 / self._Y )
        xjump = int( 640 / self._X )

        # brute force a background
        #draw_rect( frame_in, 0, 0, 640, 480, ( 0, 0, 0 ) )

        # inject random noise
        if self._debugRandomNoise == True:
            r = random.randint( 0, 255 )
            g = random.randint( 0, 255 )
            b = random.randint( 0, 255 )
            draw_rect( frame_in, ( self._noiseBlock_x * xjump ), ( self._noiseBlock_y * yjump ),
                                 ( ( self._noiseBlock_x + 1 ) * xjump - ( ( 1 - self._percentNoise ) * xjump ) - 1 ),
                                 ( ( self._noiseBlock_y + 1 ) * yjump - ( ( 1 - self._percentNoise ) * yjump ) - 1 ),
                                 ( r, g, b ) )

        # inject noise that follows a steady pattern
        if self._debugSteadyNoise == True:
            color = ( 255, 255, 0 )
            if self._frameCount % 9 == 0:
                color = ( 128, 255, 255 )
            elif self._frameCount % 8 == 0:
                color = ( 0, 128, 255 )
            elif self._frameCount % 7 == 0:
                color = ( 128, 255, 128 )
            elif self._frameCount % 6 == 0:
                color = ( 0, 0, 255 )
            elif self._frameCount % 5 == 0:
                color = ( 33, 255, 255 )
            elif self._frameCount % 4 == 0:
                color = ( 0, 33, 255 )
            elif self._frameCount % 3 == 0:
                color = ( 0, 0, 33 )
            elif self._frameCount % 2 == 0:
                color = ( 50, 50, 255 )
            draw_rect( frame_in, ( self._noiseBlock_x * xjump ), ( self._noiseBlock_y * yjump ),
                                 ( ( self._noiseBlock_x + 1 ) * xjump - ( ( 1 - self._percentNoise ) * xjump ) - 1 ),
                                 ( ( self._noiseBlock_y + 1 ) * yjump - ( ( 1 - self._percentNoise ) * yjump ) - 1 ),
                                 color )

        for y in range( 0, self._Y ):
            for x in range( 0, self._X ):

                # sum for each portion of the grid
                # TODO: change to count the number of pixels change to monitor a % of area changed
                #   sum is mixing both degree of change AND area changed
                sum_of_values = int( frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ].sum() )

                # calc a delta for each portion after Z # of frames - 1st derivitate, change over time
                dev_from_hist = abs( sum_of_values - self._prev_frame_sum_of_values[ y ][ x ] )

                if self._mask[ y ][ x ] == True:
                    frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ] = 128

                #if the | delta | < Threshold then blank out that sector
                nomotion = False
                if dev_from_hist < self._threshold * self._prev_frame_sum_of_values[ y ][ x ]:
                    nomotion = True

                    # if not already masked for some reason
                    #if self._mask[ y ][ x ] != True:
                    #    frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ] = 0

                # 2nd derivative - change of change over time
                self._devAccum[ y ][ x ] += dev_from_hist

                if self._watchFrame_enabled and self._watchFrame ==  ( y, x ):

                    self._graph_ringbuf = np.roll( self._graph_ringbuf, 1 )
                    self._graph_ringbuf[ 0 ] = yjump * dev_from_hist / 100000

                    # start with a clear image
                    #frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ] = 0
                    vis = frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ]

                    # plot the values
                    for xx in range( 1, xjump ):
                        cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf[ xx ] ) ), ( 255, 255, 0 ), 1 )
                        #cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf_MovingAverage[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf_MovingAverage[ xx ] ) ), ( 0, 25, 255 ), 2 )

                    if self._mask[ y ][ x ] == True:
                        cv2.circle( vis, ( xjump - 6, 4 ), 3, ( 0, 25, 255 ), -1 )

                    # show midway mark for refrence
                    cv2.line( vis, ( 0, yjump - int( yjump / 2 ) ), ( xjump - 1, yjump - int( yjump / 2 ) ), ( 128, 128, 128 ), 1 )

                    # plot the moving average
                    scaledMovingAvg = int( yjump * self._graph_ringbuf_MovingAverage[ 0 ] / self._maxhistAccum )
                    cv2.line( vis, ( 0, yjump - scaledMovingAvg ), ( xjump - 1, yjump - scaledMovingAvg ), ( 0, 25, 255 ), 2 )

                    scaledLastAccum = int( yjump * self._lastAccum / 1000000 )
                    cv2.line( vis, ( 0, yjump - scaledLastAccum ), ( xjump - 1, yjump - scaledLastAccum ), ( 255, 25, 0 ), 2 )

                #if self._watchFrame ==  ( y, x ):
                #    print( "%d\t%d\t%d\t%d" % ( sum_of_values, self._prev_frame_sum_of_values[ y ][ x ], dev_from_hist, self._devAccum[ y ][ x ] ) )

                # calculuate change over time
                if self._frameCount % self._timeSpan2 == 0:
                    if self._histAccum[ y ][ x ] > self._devAccum[ y ][ x ]:
                        accum = self._histAccum[ y ][ x ] - self._devAccum[ y ][ x ]
                    else:
                        accum = self._devAccum[ y ][ x ] - self._histAccum[ y ][ x ]

                    if accum < self._threshold2 *  self._histAccum[ y ][ x ] and nomotion == False:
                        self._mask[ y ][ x ] = True
                    else:
                        self._mask[ y ][ x ] = False

                    self._lastAccum = accum

                    if self._watchFrame ==  ( y, x ):
                        print( "accum: {0}\t\tdevAccum: {1}\t\thistAccum: {2}".format( accum, self._devAccum[ y ][ x ], self._histAccum[ y ][ x ] ) )

                        #self._graph_ringbuf_MovingAverage[ 0 ] = self.movingAverage( ( self._yjump * self._movingAverageSlidingWindow / self._maxhistAccum ), self._slidingWindow )

                        movingAverage = ( self._devAccum[ y ][ x ] + self._countMovAvg * self._graph_ringbuf_MovingAverage[ 0 ] ) / ( self._countMovAvg + 1 )
                        self._maxhistAccum = max( self._maxhistAccum, movingAverage )
                        if self._countMovAvg == 0:
                            self._maxhistAccum *= 0.25
                        elif self._countMovAvg == 1:
                            self._countMovAvg *= 0.50
                        elif self._countMovAvg == 2:
                            self._countMovAvg *= 0.75

                        print(  "MaxHistAccum: %d\t\tmovingAvg: %d" %( self._maxhistAccum, movingAverage ) )
                        self._graph_ringbuf_MovingAverage = np.roll( self._graph_ringbuf_MovingAverage, 1 )
                        self._graph_ringbuf_MovingAverage[ 0 ] = movingAverage
                        #self._graph_ringbuf_MovingAverage[ 0 ] = yjump * self._histAccum[ y ][ x ] / self._maxhistAccum # 1000000


                    #if self._watchFrame == ( y, x ):
                    #    print( "%d\t%d\t%d\t%d\t%s" % ( self._frameCount, self._devAccum[ self._watchFrame ], self._histAccum[ self._watchFrame ], accum, self._mask[ self._watchFrame ] ) )

                    self._histAccum[ y ][ x ] = self._devAccum[ y ][ x ]
                    self._devAccum[ y ][ x ] = 0

                self._prev_frame_sum_of_values[ y ][ x ] = sum_of_values
                last_X = x
            last_Y = y

        if self._frameCount % self._timeSpan2 == 0:
            self._countMovAvg += 1

        # return the processed frame to be either passed to the next filter
        # or displayed
        return frame_in

