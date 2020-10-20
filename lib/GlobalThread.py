import logging
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
        'start': 3,
        'stop': 4,
        'mode': 5,
        'handler': 6,
        'console': 7
    }

    # The responses sent to the GUI thread
    WORKER_RESPONSE = {
        'error': -1,
        'connected': 1,
        'disconnected': 2,
        'started': 3,
        'stopped': 4,
        'mode_changed': 5,
        'handler_changed': 6,
        'log_data': 7
    }

    _worker_response = QtCore.pyqtSignal(int, bool, str)
    _worker_command = QtCore.pyqtSignal(int, str)

    def __init__(self, title, exp_name, interval):
        super().__init__()

        # Set variables
        self._title = title
        self._exp_name = exp_name
        self._interval = interval

        # Log sensor data to console
        self._log_to_console = False

        # Global interface
        self._interface = None

        # Data logger
        self._data_logger = logging.getLogger('DATA.' + self._title)
        self._data_logger.setLevel(logging.DEBUG)
        self._data_logger.propagate = False  # Very ugly solution, but it works...

        # File Handler
        self._fh = QtGlobalWorker._create_and_append_new_handler(self._exp_name, self._title)
        self._data_logger.addHandler(self._fh)  # Print content to file

        # Read timer (we HAVE to set the parent, otherwise we need to explicitly move the timer to the thread)
        self._read_timer = QtCore.QTimer(self)
        self._read_timer.setInterval(self._interval)

        # Signals
        self._worker_command.connect(self.received_command)  # Worker commands
        self._read_timer.timeout.connect(self.read_data)  # Read timer

    @pyqtSlot(int, str)
    def received_command(self, command, arg):
        # print("[%s] Received command" % QtCore.QThread.currentThread().objectName())

        if command == self.WORKER_COMMAND['connect']:
            self.connect(arg)
        elif command == self.WORKER_COMMAND['disconnect']:
            self.disconnect()
        elif command == self.WORKER_COMMAND['start']:
            self.start_read()
        elif command == self.WORKER_COMMAND['stop']:
            self.stop_read()
        elif command == self.WORKER_COMMAND['mode']:
            self.change_mode(arg)
        elif command == self.WORKER_COMMAND['handler']:
            self.change_log_handler(arg)
        elif command == self.WORKER_COMMAND['console']:
            self.change_log_to_console(arg)

    @pyqtSlot()
    def read_data(self):
        # print("[%s] Timeout reached" % QtCore.QThread.currentThread().objectName())

        data = self._interface.process_data()

        if data != '':
            self._data_logger.debug(data)

            if self._log_to_console:
                self._worker_response.emit(self.WORKER_RESPONSE['log_data'], True, data)

    def connect(self, port):
        if self._interface.open_port(port):
            self._worker_response.emit(self.WORKER_RESPONSE['connected'], True, "")
        else:
            self._worker_response.emit(self.WORKER_RESPONSE['connected'], False, "")

        self._read_timer.stop()

    def disconnect(self):
        if self._interface.close_port():
            self._worker_response.emit(self.WORKER_RESPONSE['disconnected'], True, "")
        else:
            self._worker_response.emit(self.WORKER_RESPONSE['disconnected'], False, "")

        self._read_timer.stop()

    def start_read(self):
        if self._interface.start_device():
            self._worker_response.emit(self.WORKER_RESPONSE['started'], True, "")
        else:
            self._worker_response.emit(self.WORKER_RESPONSE['started'], False, "")

        self._read_timer.start()

    def stop_read(self):
        if self._interface.stop_device():
            self._worker_response.emit(self.WORKER_RESPONSE['stopped'], True, "")
        else:
            self._worker_response.emit(self.WORKER_RESPONSE['stopped'], False, "")

        self._read_timer.stop()

    def emit_error_signal(self):
        self._worker_response.emit(self.WORKER_RESPONSE['error'], False, "")

    def change_mode(self, mode):
        self._worker_response.emit(self.WORKER_RESPONSE['mode_changed'], self._interface.set_mode(int(mode)), "[{}]".format(mode))

    def change_log_handler(self, exp_name):
        if exp_name == self._exp_name:
            self._worker_response.emit(self.WORKER_RESPONSE['handler_changed'], False, "Name unchanged")
            return

        self._exp_name = exp_name

        self._data_logger.removeHandler(self._fh)  # Remove current handler
        self._fh.close()  # Close file
        self._fh = QtGlobalWorker._create_and_append_new_handler(self._exp_name, self._title)  # Create new handler
        self._data_logger.addHandler(self._fh)  # Attach this new handler

        self._worker_response.emit(self.WORKER_RESPONSE['handler_changed'], True,
                                  "[{}]".format(QtGlobalWorker.get_log_filename(self._exp_name, self._title)))

    def change_log_to_console(self, activate):
        self._log_to_console = activate == 'True'

    def get_interval(self):
        return self._interval

    def get_title(self):
        return self._title

    def get_exp_name(self):
        return self._exp_name

    def get_worker_command_signal(self):
        return self._worker_command

    def get_worker_response_signal(self):
        return self._worker_response

    def get_instance(self):
        return self._interface

    @staticmethod
    def get_log_filename(name, title):
        return "output/" + name.replace(" ", "_").upper() + "_" + title.replace(" ", "_").upper() + ".log"

    @staticmethod
    def _create_and_append_new_handler(name, title):
        fh = logging.FileHandler(QtGlobalWorker.get_log_filename(name, title))
        fh.setLevel(logging.DEBUG)

        return fh
