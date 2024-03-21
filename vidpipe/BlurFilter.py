#!/usr/bin/env python

import cv2
from FrameProcessor import FrameProcessor


class BlurFilter( FrameProcessor ):

    '''
    blur_kernel (kernel size) determines how many pixels to sample during the convolution
    sigma defines how much to modulate them by
    For more info:  http://http.developer.nvidia.com/GPUGems3/gpugems3_ch40.html
    '''

    _blur_kernel = 5  # good starting point is 5 - very light blur
    _sigma = 0

    def __init__( self ):
        super( BlurFilter, self ).__init__()
        self._name = "Blur Filter"
        self._sigma = 0.3 * ( ( self._blur_kernel - 1 ) * 0.5 - 1 ) + 0.8

    def prop_BlurSize_set( self, val ):
        # val must be odd
        if val % 2 == 0:
            val += 1    # hackish but 1 point won't matter enough to worry about
        self._blur_kernel = val
        self._sigma = 0.3 * ( ( self._blur_kernel - 1 ) * 0.5 - 1 ) + 0.8

    def prop_BlurSize_get( self):
        return self._blur_kernel

    def type_BlurSize( self ):
        return int

    def processFrame( self, frame_in ):
        # http://docs.opencv.org/modules/imgproc/doc/filtering.html#gaussianblur
        blurred = cv2.GaussianBlur( frame_in, ( self._blur_kernel, self._blur_kernel ), self._sigma )
        return blurred
