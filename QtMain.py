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

        # Experiment name
        self.experiment_name = QtWidgets.QLineEdit(self)
        self.experiment_name.setText("Experiment_0")

        # Mode (8Hz or 32Hz)
        # self.mode = QtWidgets.QRadioButton()

        # Sensors
        self.sensor_box_1 = QtSensor.QtSensor("Sensor 1", self)
        self.sensor_box_2 = QtSensor.QtSensor("Sensor 2", self)
        self.sensor_box_3 = QtSensor.QtSensor("Sensor 3", self)
        self.sensor_box_4 = QtSensor.QtSensor("Sensor 4", self)

        # Sensor horizontal layout
        self.sensor_layout = QtWidgets.QHBoxLayout()
        self.sensor_layout.addWidget(self.sensor_box_1)
        self.sensor_layout.addWidget(self.sensor_box_2)
        self.sensor_layout.addWidget(self.sensor_box_3)
        self.sensor_layout.addWidget(self.sensor_box_4)

        # General Start/Stop button
        self.start_all_button = QtWidgets.QPushButton(self)
        self.start_all_button.setText('START ALL')
        self.start_all_button.setEnabled(True)
        self.start_all_button.clicked.connect(self.start_all_button_clicked)

        self.stop_all_button = QtWidgets.QPushButton(self)
        self.stop_all_button.setText('STOP ALL')
        self.stop_all_button.setEnabled(True)
        self.stop_all_button.clicked.connect(self.stop_all_button_clicked)

        start_stop_layout = QtWidgets.QHBoxLayout()
        start_stop_layout.addWidget(self.start_all_button)
        start_stop_layout.addWidget(self.stop_all_button)

        # Log Box
        log_text_box = QtLogger.QLoggerBox()

        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addWidget(self.experiment_name)
        root_layout.addLayout(self.sensor_layout)
        root_layout.addLayout(start_stop_layout)
        root_layout.addWidget(log_text_box)

        self.setLayout(root_layout)

    def start_all_button_clicked(self):
        logging.info("Starting all connected devices")

        self.sensor_box_1.start_button.click()
        self.sensor_box_2.start_button.click()
        self.sensor_box_3.start_button.click()
        self.sensor_box_4.start_button.click()

    def stop_all_button_clicked(self):
        logging.info("Stopping all connected devices")

        self.sensor_box_1.stop_button.click()
        self.sensor_box_2.stop_button.click()
        self.sensor_box_3.stop_button.click()
        self.sensor_box_4.stop_button.click()


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
