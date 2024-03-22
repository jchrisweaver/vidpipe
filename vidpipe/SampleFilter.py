#!/usr/bin/env python

import cv2
from FrameProcessor import FrameProcessor


class SampleFilter( FrameProcessor ):

    # the color shown in the filter settings box
    # the color that should be used in the processFrame function for showing details
    _color = ( 0, 255, 0 )

    # the name of the filter that shows up in the filter list
    _name = "Sample Filter"

    def __init__( self ):
        super( SampleFilter, self ).__init__()

    def processFrame( self, frame_in ):
        # frame_in is BGR

        # get the size of the frame
        h, w, colors = frame_in.shape

        # return the processed frame to be either passed to the next filter
        # or displayed
        return frame_in

