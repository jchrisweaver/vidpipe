#!/usr/bin/env python

import cv2
from FrameProcessor import FrameProcessor


class SampleFilter( FrameProcessor ):

    def __init__( self ):
        super( SampleFilter, self ).__init__()
        self._name = "Sample Filter"

    def processFrame( self, frame_in ):
        # frame_in is BGR
        # frame_in.shape = ( 480, 640, 3 )

        # return the processed frame to be either passed to the next filter
        # or displayed
        return frame_in

