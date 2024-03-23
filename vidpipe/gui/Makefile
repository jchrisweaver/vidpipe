dlg_main : dialog_main.ui
	mv ../dialog_main_auto.py ../dialog_main_auto.old || true
	pyuic5 dialog_main.ui -o dialog_main_auto.py
	sed -i '' 's/QtWidgets.QWidget/CameraWidget/g' dialog_main_auto.py
	echo "from CameraWidget import CameraWidget" | sed -i '' '/from PyQt5 import QtCore, QtGui, QtWidgets/r /dev/stdin' dialog_main_auto.py
	cp dialog_main_auto.py ../

# NOTE: the rediculous sed command to insert the line is due to the Mac OS/BSD version of sed
