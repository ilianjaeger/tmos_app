import sys
from PyQt5 import QtWidgets
import logging

from lib import QtLogger
from lib import QtSensor

logging.getLogger().setLevel(logging.DEBUG)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        # Sensors
        sensor_box_1 = QtSensor.QtSensor("Sensor 1", self)
        sensor_box_2 = QtSensor.QtSensor("Sensor 2", self)

        # Log Box
        log_text_box = QtLogger.QLoggerBox(self)

        # Sensor horizontal layout
        sensor_layout = QtWidgets.QHBoxLayout()
        sensor_layout.addWidget(sensor_box_1)
        sensor_layout.addWidget(sensor_box_2)

        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addLayout(sensor_layout)
        root_layout.addWidget(log_text_box.widget)

        self.setLayout(root_layout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

    parent = psutil.Process(os.getpid())
    parent.kill()
