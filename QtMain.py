import sys
import struct
import logging
import datetime
import subprocess

from PyQt5 import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import *

from lib import QtLogger
from lib import QtSensor
from lib import QtVicon
from lib.serial_interface import list_available_ports

# Initialize logger
logging.getLogger().setLevel(logging.INFO)


def load_style(filename):
    # Add the stylesheet to the application
    try:
        fh = open(filename, "r")
        return fh.read()
    except FileNotFoundError:
        pass

    return ""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_instance, *args):
        super().__init__(*args)

        self.app_instance = app_instance

        ''' WINDOW CONFIGURATION '''
        self.experiment_name = "Experiment 0"
        self.set_title()

        ''' WIDGET CONFIGURATION '''
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
        self.experiment_name_label.setText("Experiment name")

        # Default output folder
        self.default_output_folder = QtWidgets.QLabel()
        self.default_output_folder.setText("output/")
        font = self.default_output_folder.font()
        font.setBold(True)
        self.default_output_folder.setFont(font)

        # Save button
        self.save_button = QtWidgets.QPushButton(self.config_box)
        self.save_button.setText('Save configuration')
        self.save_button.setEnabled(True)
        self.save_button.clicked.connect(self.save_config)

        # Add to layout
        self.config_root_layout.addLayout(self.config_layout)
        self.config_root_layout.addWidget(self.save_button)

        self.config_layout.addWidget(self.experiment_name_label)
        self.config_layout.addWidget(self.default_output_folder)
        self.config_layout.addWidget(self.experiment_name_line)

        # Vicon instance
        self.vicon_box = QtVicon.QtVicon("Vicon", self.experiment_name)

        # Sensors
        self.sensor_box = QtSensor.QtSensor("Drone", self.experiment_name, self)

        # Sensor horizontal layout
        self.sensor_layout = QtWidgets.QHBoxLayout()
        self.sensor_layout.addWidget(self.sensor_box)
        self.sensor_layout.addWidget(self.vicon_box)

        # Start button
        self.start_all_button = QtWidgets.QPushButton(self)
        self.start_all_button.setText('START ALL')
        self.start_all_button.setEnabled(True)
        self.start_all_button.clicked.connect(self.start_all_button_clicked)

        # Refresh COM ports button
        self.refresh_com_button = QtWidgets.QPushButton(self)
        self.refresh_com_button.setText('Refresh COM Ports')
        self.refresh_com_button.setEnabled(True)
        self.refresh_com_button.clicked.connect(self.update_com_ports)

        # Stop button
        self.stop_all_button = QtWidgets.QPushButton(self)
        self.stop_all_button.setText('STOP ALL')
        self.stop_all_button.setEnabled(True)
        self.stop_all_button.clicked.connect(self.stop_all_button_clicked)

        # Add to layout
        start_stop_layout = QtWidgets.QHBoxLayout()
        start_stop_layout.addWidget(self.start_all_button)
        start_stop_layout.addWidget(self.refresh_com_button)
        start_stop_layout.addWidget(self.stop_all_button)

        # Log Box
        self.log_text_box = QtLogger.QLoggerBox()

        ''' MAIN LAYOUT '''
        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addWidget(self.config_box)
        root_layout.addLayout(self.sensor_layout)
        root_layout.addLayout(start_stop_layout)
        root_layout.addWidget(self.log_text_box)

        # scroll bar
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)

        # Main central widget (main content)
        self.main_central_widget = QtWidgets.QWidget(self.scroll)
        self.main_central_widget.setLayout(root_layout)
        self.scroll.setWidget(self.main_central_widget)

        # Set dock area as main window central widget
        self.setCentralWidget(self.scroll)

        # Set dark theme as default
        self.style_dark = load_style("style/dark.css")
        # self.change_style('dark')

        # Update COM ports after initialization
        self.update_com_ports()

    def update_com_ports(self):
        available_ports = list_available_ports()
        self.sensor_box.update_com_port_list(available_ports)

    def adjust_widget_size(self):
        self.main_central_widget.adjustSize()
        self.resize(self.main_central_widget.sizeHint())

    def set_title(self):
        self.setWindowTitle("Ilian's App - " + self.experiment_name)

    def change_style(self, style):
        if style == 'dark':
            self.app_instance.setStyleSheet(self.style_dark)
        else:
            self.app_instance.setStyleSheet("")

        self.log_text_box.adapt_colors_to_mode(style)

    def start_all_button_clicked(self):
        logging.info("Starting all connected devices")

        t0 = datetime.datetime.now()

        self.sensor_box.start_button.click()
        self.sensor_box.set_reference_time(t0)

        self.vicon_box.start_button.click()
        self.vicon_box.set_reference_time(t0)

    def stop_all_button_clicked(self):
        logging.info("Stopping all connected devices")

        self.sensor_box.stop_button.click()
        self.vicon_box.stop_button.click()

    def save_config(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)

        msg.setText("In order to make these configurations take effect all devices have to be stopped. Continue?")
        msg.setWindowTitle("Save configuration")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        decision = msg.exec_()
        if decision == QtWidgets.QMessageBox.Cancel:
            logging.warning("Not saving configuration!")
        else:
            # Stop all device before making any changes
            self.stop_all_button_clicked()

            # Change file handlers
            self.experiment_name = self.experiment_name_line.text()
            self.set_title()
            self.sensor_box.change_file_handler(self.experiment_name)
            self.vicon_box.change_file_handler(self.experiment_name)

            logging.info("Configuration successfully saved!")


if __name__ == '__main__':
    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = MainWindow(app)

    # Start
    main_window.show()
    main_window.adjust_widget_size()

    app.exec_()
