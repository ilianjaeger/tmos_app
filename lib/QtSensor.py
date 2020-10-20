import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

from lib import serial_interface
from lib.QtSerialThread import QtSerialWorker
from lib.GlobalThread import QtGlobalWorker


class QtSensor(QtWidgets.QGroupBox):
    def __init__(self, title, exp_name, parent=None):
        super(QtSensor, self).__init__(parent)

        # Start own module logger
        self.logger = logging.getLogger('PC.' + title.replace(" ", "_").upper())
        self.logger.setLevel(logging.INFO)

        # The entire sensor block is encapsulated by a GroupBox
        self.setWindowTitle("group_box" + title)

        # Set a QGrid layout [root layout]
        self.root_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.root_layout)

        # Create the group and add it to the root layout
        self.setTitle(title)
        self.setCheckable(False)

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

        ''' LOG OUTPUT TO CONSOLE '''
        self.console_log_check = QtWidgets.QCheckBox()
        self.console_log_check.setText("Log output to console")
        self.console_log_check.setChecked(False)
        self.console_log_check.stateChanged.connect(self.console_log_changed)

        ''' ADD LAYOUTS/WIDGETS '''
        self.root_layout.addWidget(self.com_port_list)
        self.root_layout.addLayout(self.hbox_connect_disconnect_buttons)
        self.root_layout.addLayout(self.hbox_start_stop_buttons)
        self.root_layout.addWidget(self.console_log_check)

        ''' SERIAL WORKER (THREAD) '''
        # Worker
        self.serial_worker = QtSerialWorker(title, exp_name, 10)

        # Thread
        self.serial_thread = QtCore.QThread(self)
        self.serial_thread.setObjectName(title.replace(" ", "_").upper())
        self.serial_worker.moveToThread(self.serial_thread)

        # Signals
        self.serial_worker.get_worker_response_signal().connect(self.serial_response_received)

        # Start serial thread
        self.serial_thread.start()

    @pyqtSlot(int)
    def console_log_changed(self, checked):
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['console'], str(self.console_log_check.isChecked()))

    @pyqtSlot(int)
    def port_selection_change(self, i):
        pass
        '''if self.comm.is_connected(): self.logger.warning( "Changed to port " + str(self.com_port_list.currentText(
        )) + ". Disconnect and connect to apply changes") '''

    @pyqtSlot()
    def connect_button_clicked(self):
        if self.com_port_list.currentText() == "":
            self.logger.warning("No available COM port found!")
            return

        self.logger.info('Connecting...')
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['connect'], self.com_port_list.currentText())

    @pyqtSlot()
    def disconnect_button_clicked(self):
        self.logger.warning('Disconnecting...')
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['disconnect'], '')

    @pyqtSlot()
    def start_button_clicked(self):
        self.logger.info('Starting...')
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['start'], '')

    @pyqtSlot()
    def stop_button_clicked(self):
        self.logger.info('Stopping...')
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['stop'], '')

    def change_mode(self, mode):
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['mode'], str(mode))

    def change_file_handler(self, name):
        self.serial_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['handler'], str(name))

    @pyqtSlot(int, bool, str)
    def serial_response_received(self, resp, success, extra):
        # print("[%s] Received response" % QtCore.QThread.currentThread().objectName())

        if resp == QtGlobalWorker.WORKER_RESPONSE['connected']:
            self.serial_connected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['disconnected']:
            self.serial_disconnected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['started']:
            self.serial_started(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['stopped']:
            self.serial_stopped(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['mode_changed']:
            self.mode_changed(success, extra)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['handler_changed']:
            self.handler_changed(success, extra)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['log_data']:
            self.log_data(extra)
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

    def mode_changed(self, success, extra):
        if success:
            self.logger.debug("Operation mode successfully updated! Mode set to " + extra)
        else:
            self.logger.error("Invalid mode selected! Invalid mode " + extra)

    def handler_changed(self, success, extra):
        if success:
            self.logger.debug("Successfully changed log file! New file " + extra)
        else:
            self.logger.debug("Log file not updated! " + extra)

    def log_data(self, data):
        self.logger.info(data)

    def is_connected(self):
        return self.disconnect_button.isEnabled()

    def is_started(self):
        return self.stop_button.isEnabled()

    def serial_error_signal(self):
        self.logger.error("Serial error! Resetting...")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.com_port_list.setEnabled(True)