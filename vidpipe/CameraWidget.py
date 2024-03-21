#!/usr/bin/env python

import numpy as np
from OpenCVQImage import OpenCVQImage
from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QSizePolicy, QWidget


class CameraWidget( QWidget ):

    newFrame = pyqtSignal( np.ndarray )

    def __init__( self, parent = None ):
        super( CameraWidget, self ).__init__( parent )

        self._frame = None

    def setCamera( self, cameraDevice ):
        self._cameraDevice = cameraDevice
        self._cameraDevice.newFrame.connect( self._onNewFrame )

        #w, h = self._cameraDevice.frameSize
        #self.setMinimumSize(w, h)
        #self.setMaximumSize( 960, 1280)
        #self.setMinimumSize( 640, 480)
        #self.setMaximumSize(  w, h )
        #self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        #self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )

    @pyqtSlot( np.ndarray )
    def _onNewFrame(self, frame):
        self._frame = frame.copy()
        self.newFrame.emit( self._frame )
        self.update()

    def setNewFrame( self, frame ):
        self._frame = frame

    def changeEvent( self, e ):
        if e.type() == QEvent.EnabledChange:
            if self.isEnabled():
                self._cameraDevice.newFrame.connect( self._onNewFrame )
            else:
                self._cameraDevice.newFrame.disconnect( self._onNewFrame )


    def paintEvent(self, e):
        if self._frame is None:
            return

        # Assuming OpenCVQImage(self._frame) correctly converts the NumPy array to QImage
        qimage = OpenCVQImage(self._frame)

        # Get the current size of the QWidget
        widgetSize = self.size()

        # Scale the QImage to fit the QWidget, maintaining the aspect ratio
        scaledImage = qimage.scaled(widgetSize, aspectRatioMode=Qt.KeepAspectRatio)

        # Create a QPainter to draw the QImage
        painter = QPainter(self)

        # Calculate the top-left point to center the image (if aspect ratio is kept)
        x = (widgetSize.width() - scaledImage.width()) // 2
        y = (widgetSize.height() - scaledImage.height()) // 2

        # Draw the scaled image
        painter.drawImage(QPoint(x, y), scaledImage)

    '''
    def paintEvent( self, e ):
        if self._frame is None:
            return
        painter = QPainter( self )
        painter.drawImage( QPoint( 0, 0 ), OpenCVQImage( self._frame ) )
    '''
    def sizeHint( self ):
        w, h = self._cameraDevice.frameSize
        return QSize( w, h )

    def minimumnSizePolicy( self ):
        return self.sizeHint()

