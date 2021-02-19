import logging
import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot


################################################
# BASE THREAD WORKER FOR SENSORS               #
#                                              #
# - Handles all the work with respect to a     #
#   sensor -> Vicon and TMOS                   #
#                                              #
################################################


class QtGlobalWorker(QtCore.QObject):
    """ Main global worker
    """

    # The commands sent by the GUI thread
    WORKER_COMMAND = {
        'connect': 1,
        'disconnect': 2,
        'console': 3
    }

    # The responses sent to the GUI thread
    WORKER_RESPONSE = {
        'error': -1,
        'connected': 1,
        'disconnected': 2,
        'log_data': 3
    }

    _worker_response = QtCore.pyqtSignal(int, bool, str)
    _worker_command = QtCore.pyqtSignal(int, str)

    def __init__(self, interval):
        super().__init__()

        # Set variables
        self._interval = interval

        # Log sensor data to console
        self._log_to_console = False

        # Global interface
        self._interface = None

        # Read timer (we HAVE to set the parent, otherwise we need to explicitly move the timer to the thread)
        self._read_timer = QtCore.QTimer(self)
        self._read_timer.setInterval(self._interval)

        # Signals
        self._worker_command.connect(self.received_command)  # Worker commands
        self._read_timer.timeout.connect(self.read_data)  # Read timer

    @pyqtSlot(int, str)
    def received_command(self, command, arg):
        if command == self.WORKER_COMMAND['connect']:
            self.connect(arg)
        elif command == self.WORKER_COMMAND['disconnect']:
            self.disconnect()
        elif command == self.WORKER_COMMAND['console']:
            self.change_log_to_console(arg)

    @pyqtSlot()
    def read_data(self):
        data = self._interface.process_data()

        if data == -1:
            self.emit_response('error', True, "Lost connection or empty frame! Stopping...")
            self.disconnect()
        elif type(data) == str and data != '':
            if self._log_to_console:
                self.emit_response('log_data', True, data)

    def connect(self, port):
        ret = self._interface.open_port(port)
        self.emit_response('connected', ret, "")

        if ret:
            self._read_timer.start()

    def disconnect(self):
        self.emit_response('disconnected', self._interface.close_port(), "")
        self._read_timer.stop()

    def emit_error_signal(self):
        self.emit_response('error', False, "")

    def emit_response(self, resp_type, resp_succ, resp_arg):
        if resp_type not in self.WORKER_RESPONSE:
            return

        self._worker_response.emit(self.WORKER_RESPONSE[resp_type], resp_succ, resp_arg)

    def change_log_to_console(self, activate):
        self._log_to_console = activate == 'True'

    def get_interval(self):
        return self._interval

    def get_worker_command_signal(self):
        return self._worker_command

    def get_worker_response_signal(self):
        return self._worker_response

    def get_instance(self):
        return self._interface
