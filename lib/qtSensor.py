import logging
import threading

from PyQt5 import QtWidgets

from lib import serial_interface


class QtSensor(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super(QtSensor, self).__init__(parent)

        # Start own module logger
        self.logger = logging.getLogger('PC.' + title.replace(" ", "_").upper())
        self.logger.setLevel(logging.INFO)

        # The entire sensor block is encapsulated by a GroupBox
        self.setWindowTitle("group_box" + title)

        # Set a QGrid layout [root layout]
        self.root_layout = QtWidgets.QGridLayout()
        self.setLayout(self.root_layout)

        # Create the group and add it to the root layout
        self.groupbox = QtWidgets.QGroupBox(title)
        self.groupbox.setCheckable(False)
        self.root_layout.addWidget(self.groupbox)

        self.vbox = QtWidgets.QVBoxLayout()
        self.groupbox.setLayout(self.vbox)

        # The available serial ports
        self.com_port_list = QtWidgets.QComboBox()
        self.com_port_list.addItems(serial_interface.list_available_ports())
        self.com_port_list.currentIndexChanged.connect(self.port_selection_change)

        ''' CONNECT AND DISCONNECT BUTTONS '''
        self.hbox_connect_disconnect_buttons = QtWidgets.QHBoxLayout()

        # Connect button
        self.connect_button = QtWidgets.QPushButton(self)
        self.connect_button.setText('Connect')
        self.connect_button.setEnabled(True)
        self.connect_button.clicked.connect(self.connect_button_clicked)

        # Disconnect button
        self.disconnect_button = QtWidgets.QPushButton(self)
        self.disconnect_button.setText('Disconnect')
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)

        self.hbox_connect_disconnect_buttons.addWidget(self.connect_button)
        self.hbox_connect_disconnect_buttons.addWidget(self.disconnect_button)

        ''' START AND STOP BUTTONS '''
        self.hbox_start_stop_buttons = QtWidgets.QHBoxLayout()

        # Start button
        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText('Start')
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_button_clicked)

        # Stop button
        self.stop_button = QtWidgets.QPushButton(self)
        self.stop_button.setText('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_button_clicked)

        self.hbox_start_stop_buttons.addWidget(self.start_button)
        self.hbox_start_stop_buttons.addWidget(self.stop_button)

        ''' ADD LAYOUTS/WIDGETS '''
        self.vbox.addWidget(self.com_port_list)
        self.vbox.addLayout(self.hbox_connect_disconnect_buttons)
        self.vbox.addLayout(self.hbox_start_stop_buttons)

        ###################################################################
        self.comm = serial_interface.SerialInterface(0)

        ''' BIND SIGNALS '''
        self.comm.error_signal.connect(self.serial_error_signal)

    def port_selection_change(self, i):
        if self.comm.is_connected():
            self.logger.warning(
                "Changed to port " + str(self.com_port_list.currentText()) + ". Disconnect and connect to apply changes")

    def connect_button_clicked(self):
        if self.com_port_list.currentText() == "":
            self.logger.warning("No available COM port found!")
            return

        self.logger.info('Connecting...')
        if not self.comm.open_port(self.com_port_list.currentText()):
            self.logger.error("An error occurred while opening the port!")
            return

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def disconnect_button_clicked(self):
        self.logger.warning('Disconnecting...')
        self.comm.close_port()

        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.logger.warning('Device successfully disconnected...')

    def start_button_clicked(self):
        self.logger.info('Starting...')

        if not self.comm.connect_device():
            self.logger.error("An error occurred while trying to start the reading")
            return

        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)

    def stop_button_clicked(self):
        self.logger.info('Stopping...')

        if not self.comm.stop_device():
            self.logger.error("An error occurred while trying to stop the reading")
            return

        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def serial_error_signal(self):
        self.logger.error("Serial error! Closing port")

        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
