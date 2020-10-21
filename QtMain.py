import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import logging

from lib import QtLogger
from lib import QtSensor
from lib import QVicon

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
        # Frameless
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.experiment_name = "Experiment 0"
        self.set_title()

        self.style_dark = load_style("style/dark.css")
        self.change_style('dark')

        self.style_menu_dark = QtWidgets.QAction("Dark", self)
        self.style_menu_dark.setStatusTip('Set to dark mode')
        self.style_menu_dark.triggered.connect(lambda: self.change_style('dark'))

        self.style_menu_classic = QtWidgets.QAction("Classic", self)
        self.style_menu_classic.setStatusTip('Set to light mode')
        self.style_menu_classic.triggered.connect(lambda: self.change_style('classic'))

        main_menu = self.menuBar()
        main_menu = main_menu.addMenu('Window')
        main_menu.addAction(self.style_menu_dark)
        main_menu.addAction(self.style_menu_classic)

        ''' CONFIGURATION '''
        self.central_widget = QtWidgets.QWidget()

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
        self.config_layout.addWidget(self.default_output_folder)
        self.config_layout.addWidget(self.experiment_name_line)
        self.config_layout.addWidget(self.mode_select_label)
        self.config_layout.addWidget(self.mode_select_8)
        self.config_layout.addWidget(self.mode_select_32)

        ''' VICON '''
        # Vicon instance
        self.vicon_box = QVicon.QVicon("Vicon", self.experiment_name)

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
        root_layout.addWidget(self.vicon_box)
        root_layout.addLayout(self.sensor_layout)
        root_layout.addLayout(start_stop_layout)
        root_layout.addWidget(log_text_box)

        self.central_widget.setLayout(root_layout)
        self.setCentralWidget(self.central_widget)
        # self.setLayout(root_layout)

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

    def change_style(self, style):
        if style == 'dark':
            self.app_instance.setStyleSheet(self.style_dark)
        else:
            self.app_instance.setStyleSheet("")

    def start_all_button_clicked(self):
        logging.info("Starting all connected devices")

        self.sensor_box_1.start_button.click()
        self.sensor_box_2.start_button.click()
        self.sensor_box_3.start_button.click()
        self.sensor_box_4.start_button.click()
        self.vicon_box.start_button.click()

    def stop_all_button_clicked(self):
        logging.info("Stopping all connected devices")

        self.sensor_box_1.stop_button.click()
        self.sensor_box_2.stop_button.click()
        self.sensor_box_3.stop_button.click()
        self.sensor_box_4.stop_button.click()
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
            self.sensor_box_1.change_file_handler(self.experiment_name)
            self.sensor_box_2.change_file_handler(self.experiment_name)
            self.sensor_box_3.change_file_handler(self.experiment_name)
            self.sensor_box_4.change_file_handler(self.experiment_name)
            self.vicon_box.change_file_handler(self.experiment_name)

            # Change operation mode
            op_mode = int(self.mode_select_32.isChecked())
            self.sensor_box_1.change_mode(op_mode)
            self.sensor_box_2.change_mode(op_mode)
            self.sensor_box_3.change_mode(op_mode)
            self.sensor_box_4.change_mode(op_mode)
            self.vicon_box.change_mode(op_mode)

            logging.info("Configuration successfully saved!")


if __name__ == '__main__':
    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = MainWindow(app)

    # Start
    main_window.show()
    app.exec_()
