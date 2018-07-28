#!/usr/bin/env python

import cv2
import numpy as np

from PyQt5 import QtGui

class OpenCVQImage( QtGui.QImage ):

    def __init__( self, opencvBgrImg ):
#        depth = cv2.IPL_DEPTH_8U

        if len( opencvBgrImg.shape ) == 3:
            h, w, nChannels = opencvBgrImg.shape
            opencvRgbImg = np.zeros( ( h, w, 3 ), np.uint8 )
            opencvRgbImg = cv2.cvtColor( opencvBgrImg, cv2.COLOR_BGR2RGB )
        else:
#            img_format = QtGui.QImage.Format_Mono
            h, w = opencvBgrImg.shape
#            opencvRgbImg = np.zeros( ( h, w, 3 ), np.uint8 )
            opencvRgbImg = cv2.cvtColor( opencvBgrImg, cv2.COLOR_GRAY2RGB )
#            cv2.mixChannels( [ opencvBgrImg ], [ opencvRgbImg ], [ 0, 2 ] )

#        if depth != cv.IPL_DEPTH_8U or nChannels != 3:
#            raise ValueError("the input image must be 8-bit, 3-channel")

        self._imgData = opencvRgbImg.tostring()
        super( OpenCVQImage, self ).__init__( self._imgData, w, h, QtGui.QImage.Format_RGB888 )
