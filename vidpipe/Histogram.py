#!/usr/bin/env python

from __future__ import division

import math  # for sin, remove after testing
# remove later
import random

import cv2
import numpy as np
from FrameProcessor import FrameProcessor
from helpers import draw_str


class HistogramFilter( FrameProcessor ):
    _color = ( 80, 180, 80 )

    # 10 x 10 grid
    _X = 10    # 64 pixels
    _Y = 10    # 48 pixels

    _deltaT = 1    # time, in frame count-ish
    _depth = 30     # depth of the histograph
    _threshold = 0.05   # 5% value change - LOWER is more sensitive

    _frameCount = 0     # always running frame count
    _Counter = 0

    _total = 0  # used to calc average
    _last = 0   # last value stored
    _count = 0  # how many values in the histagram so far

    ringlen = 500
    _graph_ringbuf = np.zeros( ringlen, np.uint8 )
    _maxScale = 1
    _scale = 100000

    _enableDumpFile = False
    _fileDataDumpName = "histogram.txt"
    _fileDataDump = None

    _countCumulativeAverage = 0

    def __init__( self ):
        super( HistogramFilter, self ).__init__()
        self._name = "Histogram Filter"

        self._prevFrameSigma = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 18446744073709551615
        self._SigmaDeltaAccumulator = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 18446744073709551615
        self._SigmaDelta = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 18446744073709551615
        self._timeSpan2Mask = np.zeros( ( self._Y, self._X ), np.bool_ )

        self._slidingWindow = 30
        self._movingAverageSlidingWindow = np.zeros( self._slidingWindow, np.uint64 )
        self._graph_ringbuf_MovingAverage = np.zeros( self.ringlen, np.uint8 )

        self._enabled = False
        self._watchFrame = ( 0, 9 ) # top right

        if self._enableDumpFile:
            self._fileDataDump = open( self._fileDataDumpName, 'w' )

        self._cumulativeAverage = np.zeros( ( self._Y, self._X ), np.uint64 )   # max of 18446744073709551615

    def prop_Watch_set( self, val ):
        # TODO: error check
        self._watchFrame = tuple( val )[ :: -1 ]
        self._movingAverageSlidingWindow = np.zeros( self._slidingWindow, np.uint64 )
        self._graph_ringbuf_MovingAverage = np.zeros( self.ringlen, np.uint8 )

    def prop_Watch_get( self):
        return self._watchFrame[ :: -1 ]

    def type_Watch( self ):
        return tuple

    def prop_Scale_set( self, scale ):
        self._scale = scale

    def prop_Scale_get( self):
        return self._scale

    def type_Scale( self ):
        return int

    def movingAverage( self, values, window ):
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(values, weights, 'valid')
        return sma

    def processFrame( self, frame_in ):
        # frame_in is BGR
        # frame_in.shape = ( 480, 640, 3 )

        self._frameCount += 1

        # get the size of the frame
        h, w, _ = frame_in.shape

        # divide the frame into X x Y grid
        yjump = int( h / self._Y )
        xjump = int( w / self._X )
        yjump = yjump
        xjump = xjump

        # for spiting out data
        outBuffer = ""

        # brute force a background
        #draw_rect( frame_in, ( 0, 0 ), ( 640, 480 ), ( 0, 0, 0 ) )

        for y in range( 0, self._Y ):
            for x in range( 0, self._X ):

                # F1 sigma - sum for each portion of the grid
                # TODO: change to count the number of pixels change to monitor a % of area changed
                #   sum is mixing both degree of change AND area changed
                single_frame_sum = int( frame_in[ int( y * yjump ) : int( ( y + 1 ) * yjump ), int( x * xjump ) : int( ( x + 1 ) * xjump ) ].sum() )

                # Fdelta - calc a delta for each portion after Z # of frames - 1st derivitate, change over time
                frame2frame_difference = abs( single_frame_sum - self._prevFrameSigma[ y ][ x ] )

                if self._timeSpan2Mask[ y ][ x ] == True:
                    frame_in[ int( y * yjump ) : int( ( y + 1 ) * yjump ), int( x * xjump ) : int( ( x + 1 ) * xjump ) ] = 255

                if self._watchFrame == ( y, x ):
                    # start with a clear image
                    #frame_in[ y * yjump : ( y + 1 ) * yjump, x * xjump : ( x + 1 ) * xjump ] = 0
                    vis = frame_in[ int( y * yjump ) : int( ( y + 1 ) * yjump ), int( x * xjump ) : int( ( x + 1 ) * xjump ) ]

                    # show midway mark for refrence
                    cv2.line( vis, ( 0, yjump - int( yjump / 2 ) ), ( xjump - 1, yjump - int( yjump / 2 ) ), ( 128, 128, 128 ), 1 )

                    # plot the values and the moving average
                    for xx in range( 1, xjump ):
                        cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf[ xx ] ) ), ( 255, 255, 0 ), 1 )
                        cv2.line( vis, ( xx - 1, yjump - int( self._graph_ringbuf_MovingAverage[ xx - 1 ] ) ), ( xx, yjump - int( self._graph_ringbuf_MovingAverage[ xx ] ) ), ( 0, 25, 255 ), 2 )

                    if self._timeSpan2Mask[ y ][ x ] == True:
                        cv2.circle( vis, ( xjump - 6, 4 ), 3, ( 0, 25, 255 ), -1 )

                # running calculation for Sigma Delta
                self._SigmaDeltaAccumulator[ y ][ x ] += frame2frame_difference

                # at time trigger Delta Sigma Delta calcuation
                if self._frameCount % ( self._deltaT * 15 ) == 0:

                    if self._SigmaDeltaAccumulator[ y ][ x ] > self._SigmaDelta[ y ][ x ]:
                        delta_sigma_delta = self._SigmaDeltaAccumulator[ y ][ x ] - self._SigmaDelta[ y ][ x ]
                    else:
                        delta_sigma_delta = self._SigmaDelta[ y ][ x ] - self._SigmaDeltaAccumulator[ y ][ x ]

                    #outBuffer += "{0}:{1}:{2}\t".format( x, y, delta_sigma_delta )
                    outBuffer += "{0}\t".format( delta_sigma_delta )

                    if self._countCumulativeAverage > 1: # skip two times
                        self._cumulativeAverage[ y ][ x ] = ( delta_sigma_delta + ( self._countCumulativeAverage * self._cumulativeAverage[ y ][ x ] ) ) / ( self._countCumulativeAverage + 1 )

                    diff = 0
                    if delta_sigma_delta > self._cumulativeAverage[ y ][ x ]:
                        diff = delta_sigma_delta - self._cumulativeAverage[ y ][ x ]
                    else:
                        diff = self._cumulativeAverage[ y ][ x ] - delta_sigma_delta

                    if self._watchFrame == ( y, x ):
                        print( "{0},{1}\t\tdelta_sigma_delta:{2}\t\tdiff:{3}".format( y, x, delta_sigma_delta, diff ) )

                    self._timeSpan2Mask[ y ][ x ] = diff < 0.4 * self._cumulativeAverage[ y ][ x ]

                    # http://en.wikipedia.org/wiki/Moving_average
                    if self._watchFrame == ( y, x ):
                        print( "{0},{1}\t\t{2}\t{3}\t\t{4}\t\t{5}".format( y, x, delta_sigma_delta, diff, self._cumulativeAverage[ y ][ x ], self._timeSpan2Mask[ y ][ x ] ) )
                        #print( "SigDeltSig: %d" % delta_sigma_delta )

                        '''
                        ############ Sample data to verify it's working right
                        ############ testing with a sin wave
                        gg = math.sin( math.radians( self._frameCount % 360 ) ) * 10000 + 10000 # random numbers -10000 and +10000
                        self._graph_ringbuf = np.roll( self._graph_ringbuf, 1 )

                        self._graph_ringbuf[ 0 ] = int( yjump * gg / self._scale )

                        self._movingAverageSlidingWindow = np.roll( self._movingAverageSlidingWindow, 1 )
                        self._movingAverageSlidingWindow[ 0 ] = gg
                        self._graph_ringbuf_MovingAverage = np.roll( self._graph_ringbuf_MovingAverage, 1 )
                        self._graph_ringbuf_MovingAverage[ 0 ] = self.movingAverage( ( yjump * self._movingAverageSlidingWindow / self._scale ), self._slidingWindow )
                        ########### testing
                        '''

                        self._graph_ringbuf = np.roll( self._graph_ringbuf, 1 )
                        self._graph_ringbuf[ 0 ] = int( yjump * delta_sigma_delta / self._scale )

                        #self._movingAverageSlidingWindow = np.roll( self._movingAverageSlidingWindow, 1 )
                        #self._movingAverageSlidingWindow[ 0 ] = gg

                        self._graph_ringbuf_MovingAverage = np.roll( self._graph_ringbuf_MovingAverage, 1 )
                        #self._graph_ringbuf_MovingAverage[ 0 ] = self.movingAverage( ( yjump * self._movingAverageSlidingWindow / scale ), self._slidingWindow )
                        self._graph_ringbuf_MovingAverage[ 0 ] = yjump * self._cumulativeAverage[ y ][ x ] / self._scale

                        #print( "MovAvg: %d" % self._graph_ringbuf_MovingAverage[ 0 ] )

                        print( "Count: %d   CumCount: %d" % ( self._Counter, self._countCumulativeAverage ) )
                        self._Counter += 1

                    self._SigmaDelta[ y ][ x ] = self._SigmaDeltaAccumulator[ y ][ x ]
                    self._SigmaDeltaAccumulator[ y ][ x ] = 0

                self._prevFrameSigma[ y ][ x ] = single_frame_sum
                last_X = x
            last_Y = y

        if self._frameCount % ( self._deltaT * 15 ) == 0:
            self._countCumulativeAverage += 1

        if self._enableDumpFile and len( outBuffer ) > 0:
            outBuffer += "\n"
            self._fileDataDump.write( outBuffer )

        # return the processed frame to be either passed to the next filter
        # or displayed
        return frame_in

