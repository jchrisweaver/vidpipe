#!/usr/bin/env python

import cv2
from FrameProcessor import FrameProcessor


class SampleFilter( FrameProcessor ):

    # the color shown in the filter list box (left hand list box of filters)
    # this is the color that should be used in the processFrame function for showing details in the frame_in
    _color = ( 0, 255, 0 )

    # the name of the filter that shows up in the filter list
    _name = "Sample Filter"

    def __init__( self ):
        super( SampleFilter, self ).__init__()

    # Called for every frame of video
    # Don't do any long running processing in this function
    # Delays in this function will increase the value shown in the video as "time: X ms"

    # frame_in is a numpy array
    # The frame_in is BGR and contains the video frame details
    # Any alteration of the frame_in data is passed to the next filter and is shown in the videoFiltered frame

    # To show an area of interest or activity, update the self._activeRects

    # To show the entire area that's affected by the filter, update the self._boundingBox
    # The bounding box will affect the preview video (left video window)
    def processFrame( self, frame_in ):
        # frame_in is BGR

        # get the size of the frame
        h, w, colors = frame_in.shape

        # set a bounding box to show in the live video where activity or areas of interest are located
        # For instance, if the filter is tracking a ball, set the bounding box around the ball
        # If the filter affects the entire frame, like a black and white filter, do not set the bounding box
        # self._boundingBox = ( 100, 100, w / 2 , h / 2 )

        # Once processing is complete, the processed frame is returned and passed to the next filter
        # in the chain.  The changes from this filter will be input to the next filter

        # if you want to take actions that will affect the video frame but do not want to pass it to the next filter
        # copy the frame_in and take the actions on the copy
        return frame_in

