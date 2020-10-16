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

        self.experiment_name = "Experiment 0"
        self.set_title()

        ''' CONFIGURATION '''
        # Main Layout
        self.config_box = QtWidgets.QGroupBox(self)
        self.config_box.setTitle("Configuration")
        self.config_root_layout = QtWidgets.QVBoxLayout()
        self.config_box.setLayout(self.config_root_layout)

        self.config_layout = QtWidgets.QHBoxLayout()

        # Experiment name
        self.experiment_name_line = QtWidgets.QLineEdit(self)
        self.experiment_name_line.setText(self.experiment_name)
        self.experiment_name_label = QtWidgets.QLabel(self.config_box)
        self.experiment_name_label.setText("Log name")

        # Mode (8Hz or 32Hz)
        self.mode_select_8 = QtWidgets.QRadioButton("8 Hz")
        self.mode_select_8.setChecked(True)
        self.mode_select_32 = QtWidgets.QRadioButton("32 Hz")
        self.mode_select_label = QtWidgets.QLabel()
        self.mode_select_label.setText("Mode")

        # Save button
        self.save_button = QtWidgets.QPushButton(self.config_box)
        self.save_button.setText('Save configuration')
        self.save_button.setEnabled(True)
        self.save_button.clicked.connect(self.save_config)

        # Add to layout
        self.config_root_layout.addLayout(self.config_layout)
        self.config_root_layout.addWidget(self.save_button)

        self.config_layout.addWidget(self.experiment_name_label)
        self.config_layout.addWidget(self.experiment_name_line)
        self.config_layout.addWidget(self.mode_select_label)
        self.config_layout.addWidget(self.mode_select_8)
        self.config_layout.addWidget(self.mode_select_32)

        ''' SENSORS '''
        # Sensors
        self.sensor_box_1 = QtSensor.QtSensor("Sensor 1", self.experiment_name, self)
        self.sensor_box_2 = QtSensor.QtSensor("Sensor 2", self.experiment_name, self)
        self.sensor_box_3 = QtSensor.QtSensor("Sensor 3", self.experiment_name, self)
        self.sensor_box_4 = QtSensor.QtSensor("Sensor 4", self.experiment_name, self)

        # Sensor horizontal layout
        self.sensor_layout = QtWidgets.QHBoxLayout()
        self.sensor_layout.addWidget(self.sensor_box_1)
        self.sensor_layout.addWidget(self.sensor_box_2)
        self.sensor_layout.addWidget(self.sensor_box_3)
        self.sensor_layout.addWidget(self.sensor_box_4)

        ''' START/STOP BUTTONS '''
        # Start button
        self.start_all_button = QtWidgets.QPushButton(self)
        self.start_all_button.setText('START ALL')
        self.start_all_button.setEnabled(True)
        self.start_all_button.clicked.connect(self.start_all_button_clicked)

        # Stop button
        self.stop_all_button = QtWidgets.QPushButton(self)
        self.stop_all_button.setText('STOP ALL')
        self.stop_all_button.setEnabled(True)
        self.stop_all_button.clicked.connect(self.stop_all_button_clicked)

        # Add to layout
        start_stop_layout = QtWidgets.QHBoxLayout()
        start_stop_layout.addWidget(self.start_all_button)
        start_stop_layout.addWidget(self.stop_all_button)

        # Log Box
        log_text_box = QtLogger.QLoggerBox()

        ''' MAIN LAYOUT '''
        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addWidget(self.config_box)
        root_layout.addLayout(self.sensor_layout)
        root_layout.addLayout(start_stop_layout)
        root_layout.addWidget(log_text_box)

        self.setLayout(root_layout)

    def set_title(self):
        self.setWindowTitle("TMOS App - " + self.experiment_name)

    def set_icons(self):
        # Set icon
        app_icon = QtGui.QIcon()
        app_icon.addFile('img/motion_sensor_16.png', QtCore.QSize(16, 16))
        app_icon.addFile('img/motion_sensor_24.png', QtCore.QSize(24, 24))
        app_icon.addFile('img/motion_sensor_32.png', QtCore.QSize(32, 32))
        app_icon.addFile('img/motion_sensor_64.png', QtCore.QSize(64, 64))
        self.setWindowIcon(app_icon)

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

    def save_config(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)

        msg.setText("In order to make these configurations take effect all devices have to be disconnected. Continue?")
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Save configuration")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        # msg.buttonClicked.connect(self.)

        decision = msg.exec_()
        if decision == QtWidgets.QMessageBox.Cancel:
            logging.info("Not saving configuration!")
        else:
            # Change file handlers
            self.experiment_name = self.experiment_name_line.text()
            self.set_title()
            self.sensor_box_1.serial_worker.change_log_handler(self.experiment_name)
            self.sensor_box_2.serial_worker.change_log_handler(self.experiment_name)
            self.sensor_box_3.serial_worker.change_log_handler(self.experiment_name)
            self.sensor_box_4.serial_worker.change_log_handler(self.experiment_name)

            # Change operation mode
            op_mode = int(self.mode_select_32.isChecked())
            self.sensor_box_1.serial_worker.change_mode(op_mode)
            self.sensor_box_2.serial_worker.change_mode(op_mode)
            self.sensor_box_3.serial_worker.change_mode(op_mode)
            self.sensor_box_4.serial_worker.change_mode(op_mode)

            logging.info("Configuration successfully saved!")


if __name__ == '__main__':
    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = MainWindow()

    # Start
    main_window.show()
    app.exec_()
