#!/usr/bin/env python

from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QEvent

# QListWidget isn't set up to easily capture drag-rearrange events
# This is a hack class to capture a dragged list rearrange event and spit out a signal
class FilterListOrderMapper( QObject ):
    listChanged = pyqtSignal()

    def eventFilter( self, sender, event ):

        if event.type() == QEvent.ChildRemoved:
        #if event.type() == QEvent.ChildRemoved:
        #if event.type() == QEvent.ChildAdded:
        #if event.type() == QEvent.Drop:
            self.listChanged.emit()
        return False

