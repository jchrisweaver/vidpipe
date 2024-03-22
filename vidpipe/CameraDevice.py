#!/usr/bin/env python

import cv2
import numpy as np
from PyQt5 import QtCore


class CameraDevice( QtCore.QObject ):

    _DEFAULT_FPS = 30

    newFrame = QtCore.pyqtSignal( np.ndarray )

    def __init__(self, filename = None, cameraId=0, mirrored=True, parent=None):
        super(CameraDevice, self).__init__(parent)

        self.mirrored = mirrored

        self._cameraDevice  = cv2.VideoCapture( filename if filename else cameraId )

        self._timer = QtCore.QTimer( self )
        self._timer.timeout.connect( self._queryFrame )
        self._timer.setInterval( int( 1000 / self.fps ) )

        if filename:
            self._maxFrameCount = self._cameraDevice.get( cv2.CAP_PROP_FRAME_COUNT );
        self._frameCount = 0

        self.paused = False
        self._maxFrameCount = -1

    # from: https://stackoverflow.com/questions/9710520/opencv-createimage-function-isnt-working
    def _createBlankImage( self, w, h, rgb_colors = ( 0, 0, 0 ) ):
        """Create new image(numpy array) filled with certain color in RGB"""
        # Create black blank image
        image = np.zeros((h, w, 3), np.uint8)

        # Since OpenCV uses BGR, convert the color first
        color = tuple(reversed(rgb_colors))

        # Fill image with color
        image[:] = color

        return image

    @QtCore.pyqtSlot()
    def _queryFrame(self):
        success, frame = self._cameraDevice.read()

        if not success:
            print( "Error getting frame" )
        else:
            if self.mirrored:
                h, w, channels = frame.shape
                mirroredFrame = self._createBlankImage( w, h )
                mirroredFrame = cv2.flip(frame, 1)
                frame = mirroredFrame
            self.newFrame.emit( frame )
            self._frameCount += 1

        if self._maxFrameCount > -1 and self._frameCount % self._maxFrameCount == 0:
            print( "Repeat at: %d" % self._frameCount )

    @property
    def paused(self):
        return not self._timer.isActive()

    @paused.setter
    def paused(self, p):
        if p:
            self._timer.stop()
        else:
            self._timer.start()

    @property
    def frameSize(self):
        w = self._cameraDevice.get( cv2.CAP_PROP_FRAME_WIDTH )
        h = self._cameraDevice.get( cv2.CAP_PROP_FRAME_HEIGHT )
        return int(w), int(h)

    @property
    def fps( self ):
        fps =  int( self._cameraDevice.get( cv2.CAP_PROP_FPS ) )
        if not fps > 0:
            fps = self._DEFAULT_FPS
        return fps
