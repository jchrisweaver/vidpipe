# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_main.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from CameraWidget import CameraWidget


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1592, 473)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setMinimumSize(QtCore.QSize(640, 360))
        self.frame.setMaximumSize(QtCore.QSize(640, 360))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.videoLive = CameraWidget(self.frame)
        self.videoLive.setGeometry(QtCore.QRect(0, 0, 640, 360))
        self.videoLive.setMinimumSize(QtCore.QSize(640, 360))
        self.videoLive.setMaximumSize(QtCore.QSize(640, 360))
        self.videoLive.setObjectName("videoLive")
        self.horizontalLayout_6.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setMinimumSize(QtCore.QSize(640, 360))
        self.frame_2.setMaximumSize(QtCore.QSize(640, 360))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.videoFiltered = CameraWidget(self.frame_2)
        self.videoFiltered.setGeometry(QtCore.QRect(0, 0, 640, 360))
        self.videoFiltered.setMinimumSize(QtCore.QSize(640, 360))
        self.videoFiltered.setMaximumSize(QtCore.QSize(640, 360))
        self.videoFiltered.setObjectName("videoFiltered")
        self.horizontalLayout_6.addWidget(self.frame_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_Status = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_Status.sizePolicy().hasHeightForWidth())
        self.label_Status.setSizePolicy(sizePolicy)
        self.label_Status.setObjectName("label_Status")
        self.horizontalLayout_2.addWidget(self.label_Status)
        self.btnShowHist = QtWidgets.QPushButton(Dialog)
        self.btnShowHist.setObjectName("btnShowHist")
        self.horizontalLayout_2.addWidget(self.btnShowHist)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.filterList = QtWidgets.QListWidget(Dialog)
        self.filterList.setObjectName("filterList")
        self.horizontalLayout.addWidget(self.filterList)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_2.setText(_translate("Dialog", "Preview"))
        self.label.setText(_translate("Dialog", "Processed"))
        self.label_Status.setText(_translate("Dialog", "This is status text!!!"))
        self.btnShowHist.setText(_translate("Dialog", "Color Histogram"))
        self.pushButton_2.setText(_translate("Dialog", "Don\'t Push Me"))
