import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import logging

from lib import QtLogger
from lib import QtSensor

# Initialize logger
logging.getLogger().setLevel(logging.DEBUG)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        # Sensors
        sensor_box_1 = QtSensor.QtSensor("Sensor 1", self)
        sensor_box_2 = QtSensor.QtSensor("Sensor 2", self)
        sensor_box_3 = QtSensor.QtSensor("Sensor 3", self)
        sensor_box_4 = QtSensor.QtSensor("Sensor 4", self)

        # Log Box
        log_text_box = QtLogger.QLoggerBox(self)

        # Sensor horizontal layout
        sensor_layout = QtWidgets.QHBoxLayout()
        sensor_layout.addWidget(sensor_box_1)
        sensor_layout.addWidget(sensor_box_2)
        sensor_layout.addWidget(sensor_box_3)
        sensor_layout.addWidget(sensor_box_4)

        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addLayout(sensor_layout)
        root_layout.addWidget(log_text_box.widget)

        self.setLayout(root_layout)


if __name__ == '__main__':
    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = MainWindow()

    # Set title
    main_window.setWindowTitle("TMOS App")

    # Set icon
    app_icon = QtGui.QIcon()
    app_icon.addFile('img/motion_sensor_16.png', QtCore.QSize(16, 16))
    app_icon.addFile('img/motion_sensor_24.png', QtCore.QSize(24, 24))
    app_icon.addFile('img/motion_sensor_32.png', QtCore.QSize(32, 32))
    app_icon.addFile('img/motion_sensor_64.png', QtCore.QSize(64, 64))
    main_window.setWindowIcon(app_icon)

    # Start
    main_window.show()
    app.exec_()
