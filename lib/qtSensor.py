from PyQt5 import QtCore, QtGui, QtWidgets
import logging

from lib import comm_interface

class QtSensor(QtWidgets.QWidget):
    def __init__(self, title, parent = None):
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
        self.com_port_list.addItems(comm_interface.list_available_ports())
        self.com_port_list.currentIndexChanged.connect(self.port_selection_change)

        # Connect button
        self.connect_button = QtWidgets.QPushButton(self)
        self.connect_button.setText('Connect')
        self.connect_button.clicked.connect(self.connect_button_clicked)

        # Start button
        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText('Connect')
        self.start_button.clicked.connect(self.start_button_clicked)

        # Add everything to main layout (of the group box)
        self.vbox.addWidget(self.com_port_list)
        self.vbox.addWidget(self.connect_button)
        self.vbox.addWidget(self.start_button)

        ###################################################################
        self.comm = comm_interface.SerialInterface(0)

    def port_selection_change(self, i):
        self.logger.warning("Changed to port " + str(self.com_port_list.currentText()) + ". Disconnect and connect to apply changes")

    def connect_button_clicked(self):
        if self.com_port_list.currentText() == "":
            self.logger.warning("No available COM port found!")
            return

        self.logger.info('Connecting...')
        if not self.comm.open_port(self.com_port_list.currentText()):
            self.logger.error("An error occurred while opening the port. Closing...")

    def start_button_clicked(self):
        if not self.comm.is_connected():
            self.logger.error("Device not connected!")
            return

        self.logger.info('Starting...')
        self.comm.connect_device()