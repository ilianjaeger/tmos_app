import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

from lib import QtLogger
from lib import qtSensor

logging.getLogger().setLevel(logging.DEBUG)

class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        log_text_box = QtLogger.QLoggerBox(self)
        sensor_box = qtSensor.QtSensor("Sensor 1", self)

        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Test Me')    

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(sensor_box)
        layout.addWidget(log_text_box.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)    

        # Connect signal to slot
        self._button.clicked.connect(self.test)    

    def test(self):
        logging.debug('damn, a bug')
        logging.info('something to remember')
        logging.warning('that\'s not right')
        logging.error('foobar')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())