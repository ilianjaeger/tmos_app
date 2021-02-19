import logging
import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

from lib.QtSocketThread import QtSocketWorker
from lib.template.GlobalThread import QtGlobalWorker


class QtSensor(QtWidgets.QGroupBox):
    def __init__(self, title, parent=None):
        super(QtSensor, self).__init__(parent)

        self.time_zero = datetime.datetime.now()

        # Start own module logger
        self.logger = logging.getLogger('TMOS')
        self.logger.setLevel(logging.INFO)

        ''' WIDGET '''
        # Create root layout
        self.root_layout = QtWidgets.QVBoxLayout()

        self.setTitle(title)
        self.setCheckable(False)
        self.setLayout(self.root_layout)

        ####
        self.config_hbox = QtWidgets.QHBoxLayout()
        ####

        ''' LABELS '''
        self.label_vbox = QtWidgets.QVBoxLayout()

        # IP address label
        self.IP_address_label = QtWidgets.QLabel()

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

        self.config_hbox.addWidget(self.IP_address_edit_label, 20)
        self.config_hbox.addWidget(self.IP_address_edit, 50)
        self.config_hbox.addWidget(self.IP_address_button, 30)

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

        ''' LOG OUTPUT TO CONSOLE '''
        self.console_log_check = QtWidgets.QCheckBox()
        self.console_log_check.setText("Log output to console")
        self.console_log_check.setChecked(False)
        self.console_log_check.stateChanged.connect(self.console_log_changed)

        ''' ADD LAYOUTS/WIDGETS '''
        self.root_layout.addLayout(self.config_hbox)
        self.root_layout.addLayout(self.hbox_connect_disconnect_buttons)
        self.root_layout.addWidget(self.console_log_check)

        ''' SOCKET WORKER (THREAD) '''
        # Worker
        self.socket_worker = QtSocketWorker(10)
        self.set_ip_button_clicked()

        # Thread
        self.socket_thread = QtCore.QThread(self)
        self.socket_thread.setObjectName(title.replace(" ", "_").upper())
        self.socket_worker.moveToThread(self.socket_thread)

        # Signals
        self.socket_worker.get_worker_response_signal().connect(self.socket_response_received)

        # Start thread
        self.socket_thread.start()

    @pyqtSlot()
    def set_ip_button_clicked(self):
        self.IP_address_label.setText("IP Address: " + self.IP_address_edit.text())
        self.socket_worker.get_instance().set_port(self.IP_address_edit.text())

    @pyqtSlot(int)
    def console_log_changed(self, checked):
        self.send_command('console', str(self.console_log_check.isChecked()))

    @pyqtSlot()
    def connect_button_clicked(self):
        self.logger.info('Connecting...')
        self.send_command('connect', self.socket_worker.get_instance().get_port())

    @pyqtSlot()
    def disconnect_button_clicked(self):
        self.logger.warning('Disconnecting...')
        self.send_command('disconnect')

    def send_command(self, comm_id, comm_arg=''):
        self.socket_worker.get_worker_command_signal().emit(QtGlobalWorker.WORKER_COMMAND[comm_id], comm_arg)

    @pyqtSlot(int, bool, str)
    def socket_response_received(self, resp, success, extra):
        if resp == QtGlobalWorker.WORKER_RESPONSE['connected']:
            self.socket_connected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['disconnected']:
            self.socket_disconnected(success)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['log_data']:
            self.log_data(extra)
        elif resp == QtGlobalWorker.WORKER_RESPONSE['error']:
            self.log_error(extra)

    def socket_connected(self, success):
        if success:
            self.logger.info("Successfully connected!")

            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.IP_address_edit.setEnabled(False)
            self.IP_address_button.setEnabled(False)
        else:
            self.logger.error("Could not connect!")

            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def socket_disconnected(self, success):
        if success:
            self.logger.info("Successfully disconnected!")
        else:
            self.logger.error("Could not connect!")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.IP_address_edit.setEnabled(True)
        self.IP_address_button.setEnabled(True)

    def log_data(self, data):
        self.logger.info(data)

    def log_error(self, msg):
        self.logger.error(msg)

    def is_connected(self):
        return self.disconnect_button.isEnabled()


    def serial_error_signal(self):
        self.logger.error("Serial error! Resetting...")

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
