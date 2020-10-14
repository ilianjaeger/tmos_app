import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

from lib import serial_interface
from lib import QtSerialThread


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

        ''' SERIAL WORKER (THREAD) '''
        # Worker
        self.serial_worker = QtSerialThread.QtSerialWorker(title)

        # Thread
        self.serial_thread = QtCore.QThread(self)
        self.serial_thread.setObjectName(title.replace(" ", "_").upper())
        self.serial_worker.moveToThread(self.serial_thread)

        # Signals
        self.serial_worker.serial_response.connect(self.serial_response_received)

        # Start serial thread
        self.serial_thread.start()

    @pyqtSlot(int)
    def port_selection_change(self, i):
        if self.comm.is_connected():
            self.logger.warning(
                "Changed to port " + str(self.com_port_list.currentText()) + ". Disconnect and connect to apply changes")

    @pyqtSlot()
    def connect_button_clicked(self):
        if self.com_port_list.currentText() == "":
            self.logger.warning("No available COM port found!")
            return

        self.logger.info('Connecting...')
        self.serial_worker.serial_command.emit(QtSerialThread.SERIAL_COMMAND['connect'], self.com_port_list.currentText())

    @pyqtSlot()
    def disconnect_button_clicked(self):
        self.logger.warning('Disconnecting...')
        self.serial_worker.serial_command.emit(QtSerialThread.SERIAL_COMMAND['disconnect'], '')

    @pyqtSlot()
    def start_button_clicked(self):
        self.logger.info('Starting...')
        self.serial_worker.serial_command.emit(QtSerialThread.SERIAL_COMMAND['start'], '')

    @pyqtSlot()
    def stop_button_clicked(self):
        self.logger.info('Stopping...')
        self.serial_worker.serial_command.emit(QtSerialThread.SERIAL_COMMAND['stop'], '')

    @pyqtSlot(int, bool)
    def serial_response_received(self, resp, success):
        # print("[%s] Received response" % QtCore.QThread.currentThread().objectName())

        if resp == QtSerialThread.SERIAL_RESPONSE['connected']:
            self.serial_connected(success)
        elif resp == QtSerialThread.SERIAL_RESPONSE['disconnected']:
            self.serial_disconnected(success)
        elif resp == QtSerialThread.SERIAL_RESPONSE['started']:
            self.serial_started(success)
        elif resp == QtSerialThread.SERIAL_RESPONSE['stopped']:
            self.serial_stopped(success)
        else:
            self.serial_error_signal()

    def serial_connected(self, success):
        if success:
            self.logger.info("Successfully connected!")

            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.com_port_list.setEnabled(False)
        else:
            self.logger.error("Could not connect!")

            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def serial_disconnected(self, success):
        if success:
            self.logger.info("Successfully disconnected!")
        else:
            self.logger.error("Could not connect!")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.com_port_list.setEnabled(True)

    def serial_started(self, success):
        if success:
            self.logger.info('Successfully started!')

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.logger.error("Could not start!")

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def serial_stopped(self, success):
        if success:
            self.logger.info('Successfully stopped!')
        else:
            self.logger.error("Could not stop!")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def serial_error_signal(self):
        self.logger.error("Serial error! Resetting...")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.com_port_list.setEnabled(True)
