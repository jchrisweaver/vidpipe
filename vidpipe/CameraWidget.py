#!/usr/bin/env python

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QPoint, QEvent, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QSizePolicy

from OpenCVQImage import OpenCVQImage
import numpy as np

class CameraWidget( QWidget ):

    newFrame = pyqtSignal( np.ndarray )

    def __init__( self, parent = None ):
        super( CameraWidget, self ).__init__( parent )

        self._frame = None

    def setCamera( self, cameraDevice ):
        self._cameraDevice = cameraDevice
        self._cameraDevice.newFrame.connect( self._onNewFrame )

        w, h = self._cameraDevice.frameSize
        self.setMinimumSize(w, h)
        self.setMaximumSize( 960, 1280)
        #self.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )

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

    def paintEvent( self, e ):
        if self._frame is None:
            return
        painter = QPainter( self )
        painter.drawImage( QPoint( 0, 0 ), OpenCVQImage( self._frame ) )

    def sizeHint( self ):
        w, h = self._cameraDevice.frameSize
        return QSize( w, h )

    def minimumnSizePolicy( ):
        return sizeHint()

