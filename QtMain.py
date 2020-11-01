import sys
import logging
import datetime

from PyQt5 import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import *

from lib import QtLogger
from lib import QtSensor
from lib import QtPlotter

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

        self.style_dark = load_style("style/dark.css")

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
        self.experiment_name_label.setText("Logging name")

        # Default output folder
        self.default_output_folder = QtWidgets.QLabel()
        self.default_output_folder.setText("output/")
        font = self.default_output_folder.font()
        font.setBold(True)
        self.default_output_folder.setFont(font)

        # Mode (8Hz or 32Hz)
        self.mode_select_8 = QtWidgets.QRadioButton("8 Hz")
        self.mode_select_32 = QtWidgets.QRadioButton("32 Hz")
        self.mode_select_32.setChecked(True)
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

        # Sensors
        self.sensor_box = QtSensor.QtSensor("Sensor", self.experiment_name, int(self.mode_select_32.isChecked()), self)

        # Log Box
        self.log_text_box = QtLogger.QLoggerBox()

        ''' MAIN LAYOUT '''
        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addWidget(self.config_box)
        root_layout.addWidget(self.sensor_box)
        root_layout.addWidget(self.log_text_box)

        # scroll bar
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)

        # Main central widget (main content)
        self.main_central_widget = QtWidgets.QWidget()
        self.main_central_widget.setLayout(root_layout)
        self.scroll.setWidget(self.main_central_widget)

        # Docking area
        self.dock_area = DockArea()

        # Dock for the main window
        self.main_dock = Dock("Main configuration")
        self.main_dock.addWidget(self.scroll)

        # Dock for the plotter
        self.plotter_dock = QtPlotter.QtLivePlotter("Data plots")

        # Add docks to dock area
        self.dock_area.addDock(self.plotter_dock)
        self.dock_area.addDock(self.main_dock)

        self.dock_area.moveDock(self.main_dock, 'above', self.plotter_dock)

        # Set dock area as main window central widget
        self.setCentralWidget(self.dock_area)

        # Set dark theme as default
        self.change_style('dark')

    def adjust_widget_size(self):
        self.main_central_widget.adjustSize()
        self.resize(self.main_central_widget.sizeHint())

    def set_title(self):
        self.setWindowTitle("TMOS People Counter")

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

        self.log_text_box.adapt_colors_to_mode(style)

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
    main_window.adjust_widget_size()

    app.exec_()
