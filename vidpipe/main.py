#!/usr/bin/env python

from __future__ import division
import sys
import numpy as np
import cv2
import random

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDialog, QGroupBox, QFrame, QLayout, QCheckBox, QListWidgetItem, QAbstractItemView, QSpinBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLineEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QPoint, QEvent
from PyQt5.QtCore import Qt, QSignalMapper, QVariant, QRegExp
from PyQt5.QtGui import QRegExpValidator, QValidator, QPalette, QColor
from dialog_main_auto import Ui_Dialog

from helpers import draw_rect, draw_str, clock, combine, intersection_rect

from FilterListOrderMapper import FilterListOrderMapper

from CameraDevice import CameraDevice
from CameraWidget import CameraWidget

from FrameProcessor import FrameProcessor
from EdgeDetector import EdgeDetector
from FleshDetector import FleshDetector
from BlurFilter import BlurFilter
from BlockNumber import BlockNumber
from Histogram import HistogramFilter
from SimpleMotionDetection import SimpleMotionDetection
from ActivityFilter import ActivityFilter

class KnobTurner( QObject, Ui_Dialog ):

    _frameCount = 0                 # running total frames shown
    _frameRate_RunningAvg = -1.0    # decaying average frame rate (displayed on video)
    _alpha = 0.01                   # how fast to update the screen refresh frame rate display variable
    _showHist = False
    _histogramWindowName = "Color Histogram"

    class Mapper( QObject ):

        def __init__(self, caller, called, action = None ):
            QObject.__init__( self )
            self._caller = caller
            self._called = called
            self._action = action

        @property
        def caller( self ):
            return self._caller

        @property
        def called( self ):
            return self._called

        @property
        def action( self ):
            return self._action

    def __init__( self ):
        print( ">>>>>>>>>>>>>>>TODO: Restore the latest set of options??" )
        Ui_Dialog.__init__( self )
        QObject.__init__( self )

        self._filters = [
            BlurFilter(),
            FleshDetector(),
            SimpleMotionDetection(),
            ActivityFilter(),
            HistogramFilter(),
            BlockNumber(),
            EdgeDetector()
            ]

    @pyqtSlot( )
    def resetFilterListModel( self ):
        # if we get here then the filter list has been drag-rearranged

        # reset the filter list based off the filterList order
        self._filters = []
        prev = None
        for indx in range( 0, self.filterList.count() ):
            fltr = self.filterList.item( indx ).data( Qt.UserRole )
            self._filters.append( fltr )

        for indx in range( 0, self.filterList.count() ):
            print("Index: %d Name: %s" % ( indx, self.filterList.item( indx ).data( Qt.UserRole ).name ) )

    def getFilterProperties( self, fltr ):
        attribs = [ funct.replace( FrameProcessor.propStartsWith, "" ) for funct in dir( fltr ) if callable( getattr( fltr, funct ) ) and funct.startswith( FrameProcessor.propStartsWith ) ]

        setters = [ ftn.replace( FrameProcessor.propEndsWithSetter, "" ) for ftn in attribs if ftn.endswith( FrameProcessor.propEndsWithSetter ) ]
        getters = [ ftn.replace( FrameProcessor.propEndsWithGetter, "" ) for ftn in attribs if ftn.endswith( FrameProcessor.propEndsWithGetter ) ]

        return getters, setters

    def check_state( self, caller ):
        validator = caller.validator()
        state = validator.validate( caller.text(), 0 )[ 0 ]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        caller.setStyleSheet( 'QLineEdit { background-color: %s }' % color )
        return ( state == QValidator.Acceptable )

    @pyqtSlot( QObject )
    def saveFilterValue( self, obj ):
        assert( isinstance( obj.caller, QSpinBox ) or isinstance( obj.caller, QCheckBox ) or isinstance( obj.caller, QLineEdit ) )

        if isinstance( obj.caller, QSpinBox ):
            newVal = obj.caller.value()
        elif isinstance( obj.caller, QCheckBox ):
            newVal = obj.caller.isChecked()
        elif isinstance( obj.caller, QLineEdit ):
            if self.check_state( obj.caller ) != True:
                return
            newVal = [ int( t ) for t in obj.caller.text().split( "," ) ]

        try:
            func = getattr( obj.called, obj.action )
        except AttributeError:
            print( "Whoops, for some reason the callback isn't valid." )
        else:
            result = func( newVal )

        # reset the frame rate
        self._frameRate_RunningAvg = -1

    def setupUi( self, dlg ):
        Ui_Dialog.setupUi( self, dlg )

        self.btnShowHist.clicked.connect( self.showHistogram )

        self._filterListOrderMapper = FilterListOrderMapper()
        self._filterListOrderMapper.listChanged.connect( self.resetFilterListModel )

        self.filterList.installEventFilter( self._filterListOrderMapper )
        self.filterList.setDragDropMode( QAbstractItemView.InternalMove )

        self._optionMapper = QSignalMapper( dlg )
        self._optionMapper.mapped[ QObject ].connect( self.saveFilterValue )
        self._optionSave = []   # this is only for making sure the Mapper object doesn't get garbage collected

        #regx = QRegExp( "([0-9]{1,3}[\,][ ]*){2}[0-9]{1,3}" )
        regx = QRegExp( "([0-9]{1,3}[\,][ ]*){1,2}[0-9]{1,3}" )

        for fltr in self._filters:
            print( "Filter added: %s" % fltr.name )

            fltr.loadConfig( None )

            self.label_Status.setText( "Loading filters" )
            getters, setters = self.getFilterProperties( fltr )
            print( "\tAvailable GETable options: ", getters )
            print( "\tAvailable SETable options: ", setters )

            group = QGroupBox()
            vbl = QVBoxLayout( group )

            # Row ------
            fm = QFrame()
            vb = QVBoxLayout( fm )

            vb.setSizeConstraint( QLayout.SetFixedSize )

            # add the enabled checkbox first always
            cb2 = QCheckBox( fltr.name )
            cb2.setCheckState( getattr( fltr, FrameProcessor.propStartsWith + "Enabled" + FrameProcessor.propEndsWithGetter )() )
            cb2.setStyleSheet( 'background-color:#%02x%02x%02x' % ( fltr.color()[ :: -1 ] ) )
            vb.addWidget( cb2 )
            # watch for values changing
            cb2.stateChanged.connect( self._optionMapper.map )
            self._optionSave.append(
                KnobTurner.Mapper( cb2, fltr,
                                  FrameProcessor.propStartsWith + "Enabled" + FrameProcessor.propEndsWithSetter ) )
            self._optionMapper.setMapping( cb2, self._optionSave[ -1 ] )

            for item in setters:
                prop_type = getattr( fltr, FrameProcessor.propTypeStartsWith + item )()
                if prop_type is int:
                    hz = QHBoxLayout()
                    lb1 = QLabel( "%s:" % item )
                    sp1 = QSpinBox()
                    sp1.setRange( 0, 10000000 ) # TODO: add this as a query to the filter
                    sp1.setValue( getattr( fltr, FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithGetter )() )
                    vb.addWidget( lb1 )
                    vb.addWidget( sp1 )

                    # watch for values changing
                    sp1.valueChanged.connect( self._optionMapper.map )
                    self._optionSave.append(
                        KnobTurner.Mapper( sp1, fltr,
                                          FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithSetter ) )
                    self._optionMapper.setMapping( sp1, self._optionSave[ -1 ] )

                elif prop_type is bool:
                    if item == "Enabled":
                        continue
                    else:
                        cb2 = QCheckBox( item )
                    cb2.setCheckState( getattr( fltr, FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithGetter )() )
                    vb.addWidget( cb2 )

                    # watch for values changing
                    cb2.stateChanged.connect( self._optionMapper.map )
                    self._optionSave.append(
                        KnobTurner.Mapper( cb2, fltr,
                                          FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithSetter ) )
                    self._optionMapper.setMapping( cb2, self._optionSave[ -1 ] )
                elif prop_type is tuple:
                    hz = QHBoxLayout()
                    lb1 = QLabel( "%s:" % item )

                    val = getattr( fltr, FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithGetter )()
                    le = QLineEdit( "{0}".format( val ).replace( "(","" ).replace( ")", "" ).replace( "[", "" ).replace( "]", "" ) )

                    le.setValidator( QRegExpValidator( regx ) )
                    le.textChanged.connect( self._optionMapper.map )
                    le.textChanged.emit( le.text() )

                    self._optionSave.append(
                        KnobTurner.Mapper( le, fltr,
                                          FrameProcessor.propStartsWith + item + FrameProcessor.propEndsWithSetter ) )
                    self._optionMapper.setMapping( le, self._optionSave[ -1 ] )

                    vb.addWidget( lb1 )
                    vb.addWidget( le )
            # end Row 2 -----

            vbl.addWidget( fm )
            vbl.setSizeConstraint( QLayout.SetFixedSize )

            lwi = QListWidgetItem()
            lwi.setSizeHint( vbl.sizeHint() )
            lwi.setData( Qt.UserRole, QVariant( fltr ) )    # attach the filter to this item in the list
            self.filterList.addItem( lwi )
            self.filterList.setItemWidget( lwi, group )

        self.label_Status.setText( "Loading filters... Done" )

        self.label_Status.setText( "Starting cameras..." )
        self.startCamera()
        self.label_Status.setText( "Starting cameras... Done" )

        self.showWindows()

        self.label_Status.setText( "Ready" )

    def startCamera( self ):
        print( "Starting camera" )
        #vid = "drop.avi"    # use video instead of camera
        vid = None
        self._cameraDevice = CameraDevice( vid )

        self.videoLive.setCamera( self._cameraDevice )
        self.videoLive.newFrame.connect( self.processPreviewFrame )

        self.videoFiltered.setCamera( self._cameraDevice )
        self.videoFiltered.newFrame.connect( self.processFilteredFrame )

    def showHistogram( self ):
        self._showHist = not self._showHist

        if not self._showHist:
            cv2.destroyWindow( self._histogramWindowName )

    def updateHistogram( self ):
        bin_count = self.hist.shape[ 0 ]
        bin_w = 40
        img = np.zeros( ( 256, bin_count * bin_w, 3 ), np.uint8 )
        #for i in xrange( bin_count ):
        for i in range( 0, bin_count ):
            h = int( self.hist[ i ] )
            cv2.rectangle( img, ( i * bin_w + 2, 255 ), ( ( i + 1 ) * bin_w - 2, 255 - h ),
                          ( int( 180.0 * i / bin_count ), 255, 255 ), -1 )
        img = cv2.cvtColor( img, cv2.COLOR_HSV2BGR )
        cv2.imshow( self._histogramWindowName, img )

    def showWindows( self ):
        self.videoLive.show()
        self.videoFiltered.show()
        print( self.videoLive.sizeHint() )

    @pyqtSlot( np.ndarray )
    def processPreviewFrame(self, frame ):

        # update histogram every 15th frame (picked arbitrarily)
        if self._showHist == True and self._frameCount % 15 == 0:
            hsv = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )
            hist = cv2.calcHist( [ hsv ], [ 0 ], None, [ 16 ], [ 0, 180 ] )
            cv2.normalize( hist, hist, 0, 255, cv2.NORM_MINMAX );
            self.hist = hist.reshape( -1 )

            self.updateHistogram()

        intersect_box = None
        colors = []
        boxes = []
        for fltr in self._filters:
            if fltr.prop_Enabled_get():
                box = fltr.getBoundingBox() # CAREFUL!!: returns (x1, y1, x2, y2) NOT x, y, w, h ****
                if len( box ) != 0:
                    colors.append( fltr.color() )
                    boxes.append( box )
                    if intersect_box == None:
                        intersect_box = box
                    else:
                        intersect_box = intersection_rect( intersect_box, box )

        # fade the color for all but the intersection of active areas
        if intersect_box != None:
            rectW = intersect_box[ 2 ] - intersect_box[ 0 ]
            rectH = intersect_box[ 3 ] - intersect_box[ 1 ]
            saverect = frame[ intersect_box[ 1 ] : intersect_box[ 1 ] + rectH, intersect_box[ 0 ] : intersect_box[ 0 ] + rectW ]

        frame = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
        ## TODO: this crashes now with 'TypeError: No loop matching the specified signature and casting was found for ufunc true_divide' - new numpy
        # frame /= 2  # cut the overal luminocity of the preview video by half to highlight the in-frame portion
        frame = cv2.cvtColor( frame, cv2.COLOR_GRAY2BGR )

        # restore the color to only the intersection
        if intersect_box != None:
            frame[ intersect_box[ 1 ] : intersect_box[ 1 ] + rectH, intersect_box[ 0 ] : intersect_box[ 0 ] + rectW ] = saverect

        # paint the boxes back on top of the gray image
        for index, box in enumerate( boxes ):
            cv2.rectangle( frame, ( box[ 0 ], box[ 1 ] ), ( box[ 2 ], box[ 3 ] ), colors[ index ], 2 )

        self.videoLive.setNewFrame( frame )

    @pyqtSlot( np.ndarray )
    def processFilteredFrame(self, frame ):
        t = clock()

        for fltr in self._filters:
            if fltr.prop_Enabled_get() == True:   # I'm cheating here because I know this property exists for all filters
                frame = fltr.processFrame( frame )

        # show time
        delta_t = clock() - t
        if self._frameRate_RunningAvg == -1:
            self._frameRate_RunningAvg = delta_t
        self._frameRate_RunningAvg = ( self._alpha * delta_t ) + ( 1.0 - self._alpha ) * self._frameRate_RunningAvg
        draw_str( frame, 20, 20, 'time: %.1f ms' % ( self._frameRate_RunningAvg * 1000 ) )

        # last guy puts the frame up
        self.videoFiltered.setNewFrame( frame )

    @pyqtSlot()
    def shutDown( self ):
        print( ">>>>>>>>>>>>>>>TODO: Print and/or save the latest set of options!!" )

        for fltr in self._filters:
            fltr.saveConfig( None )

        print( "Shutting down" )

def main():
    app = QApplication( sys.argv )

    window = QDialog()
    ui = KnobTurner()
    ui.setupUi( window )

    app.lastWindowClosed.connect( ui.shutDown )

    window.show()
    window.raise_()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main()
