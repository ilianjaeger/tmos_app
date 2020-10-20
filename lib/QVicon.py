import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

from lib.QtViconThread import QtViconWorker
from lib.GlobalThread import QtGlobalWorker


class QVicon(QtWidgets.QGroupBox):
    def __init__(self, title, exp_name, parent=None):
        super(QVicon, self).__init__(parent)

        # Start own module logger
        self.logger = logging.getLogger('VICON')
        self.logger.setLevel(logging.INFO)

        ''' WIDGET '''
        # Create root layout
        self.root_layout = QtWidgets.QVBoxLayout()

        self.setTitle("Vicon")
        self.setCheckable(False)
        self.setLayout(self.root_layout)

        ####
        self.config_hbox = QtWidgets.QHBoxLayout()
        ####

        ''' LABELS '''
        self.label_vbox = QtWidgets.QVBoxLayout()

        # Version label
        self.version_label = QtWidgets.QLabel()
        self.version_label.setText("SDK Version: -")

        # IP address label
        self.IP_address_label = QtWidgets.QLabel()

        self.label_vbox.addWidget(self.version_label)
        self.label_vbox.addWidget(self.IP_address_label)
        self.config_hbox.addLayout(self.label_vbox)

        ''' IP ADDRESS '''
        self.IP_address_edit = QtWidgets.QLineEdit(self)
        self.IP_address_edit.setText("192.168.10.1")
        self.IP_address_edit_label = QtWidgets.QLabel()

        self.IP_address_button = QtWidgets.QPushButton(self)
        self.IP_address_button.setText('Set IP')
        self.IP_address_button.setEnabled(True)
        self.IP_address_button.clicked.connect(self.set_ip_button_clicked)

        self.config_hbox.addWidget(self.IP_address_edit_label, 50)
        self.config_hbox.addWidget(self.IP_address_edit, 30)
        self.config_hbox.addWidget(self.IP_address_button, 20)

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
        self.root_layout.addLayout(self.config_hbox)
        self.root_layout.addLayout(self.hbox_connect_disconnect_buttons)
        self.root_layout.addLayout(self.hbox_start_stop_buttons)
        self.root_layout.addWidget(self.console_log_check)

        ''' VICON WORKER (THREAD) '''
        # Worker
        self.vicon_worker = QtViconWorker(title, exp_name, 10)
        self.version_label.setText("SDK Version: " + self.vicon_worker.get_instance().get_version())
        self.set_ip_button_clicked()

        # Thread
        self.vicon_thread = QtCore.QThread(self)
        self.vicon_thread.setObjectName(title.replace(" ", "_").upper())
        self.vicon_worker.moveToThread(self.vicon_thread)

        # Signals
        self.vicon_worker.get_worker_response_signal().connect(self.vicon_response_received)

        # Start vicon thread
        self.vicon_thread.start()

    @pyqtSlot()
    def set_ip_button_clicked(self):
        self.IP_address_label.setText("IP Address: " + self.IP_address_edit.text())
        self.vicon_worker.get_instance().set_port(self.IP_address_edit.text())

    @pyqtSlot(int)
    def console_log_changed(self, checked):
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['console'],
                                                           str(self.console_log_check.isChecked()))

    @pyqtSlot()
    def connect_button_clicked(self):
        self.logger.info('Connecting Vicon...')
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['connect'], self.vicon_worker.get_instance().get_port())

    @pyqtSlot()
    def disconnect_button_clicked(self):
        self.logger.warning('Disconnecting Vicon...')
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['disconnect'], "")

    @pyqtSlot()
    def start_button_clicked(self):
        self.logger.info('Starting...')
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['start'], '')

    @pyqtSlot()
    def stop_button_clicked(self):
        self.logger.info('Stopping...')
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['stop'], '')

    def change_mode(self, mode):
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['mode'], str(mode))

    def change_file_handler(self, name):
        self.vicon_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND['handler'], str(name))

    @pyqtSlot(int, bool, str)
    def vicon_response_received(self, resp, success, extra):
        if resp == QtGlobalWorker.WORKER_RESPONSE['connected']:
            self.vicon_connected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['disconnected']:
            self.vicon_disconnected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['started']:
            self.vicon_started(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['stopped']:
            self.vicon_stopped(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['mode_changed']:
            self.mode_changed(success, extra)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['handler_changed']:
            self.handler_changed(success, extra)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['log_data']:
            self.log_data(extra)

    def vicon_connected(self, success):
        if success:
            self.logger.info("Successfully connected!")

            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.IP_address_edit.setEnabled(False)
            self.IP_address_button.setEnabled(False)
        else:
            self.logger.error("Could not connect!")

            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def vicon_disconnected(self, success):
        if success:
            self.logger.info("Successfully disconnected!")
        else:
            self.logger.error("Could not connect!")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.IP_address_edit.setEnabled(True)
        self.IP_address_button.setEnabled(True)

    def vicon_started(self, success):
        if success:
            self.logger.info('Successfully started!')

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.IP_address_edit.setEnabled(False)
            self.IP_address_button.setEnabled(False)
        else:
            self.logger.error("Could not start!")

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.IP_address_edit.setEnabled(False)
            self.IP_address_button.setEnabled(False)

    def vicon_stopped(self, success):
        if success:
            self.logger.info('Successfully stopped!')
        else:
            self.logger.error("Could not stop!")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.IP_address_edit.setEnabled(False)
        self.IP_address_button.setEnabled(False)

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


'''
    

    def get_IP_address(self):
        return "192.168.0.1"
        '''
