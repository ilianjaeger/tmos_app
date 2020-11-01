import logging
import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from lib.QtPlotter import data_plot_queue


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

        self._time_zero = datetime.datetime.now()

        # Set variables
        self._title = title
        self._exp_name = exp_name
        self._interval = interval

        # Log sensor data to console
        self._log_to_console = False

        # Log to data plotter
        self._log_to_plotter = True

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
        data = self._interface.process_data()

        if data == -1:
            self.emit_response('error', True, "Lost connection or empty frame! Stopping...")
            self.stop_read()
        elif type(data) == str and data != '':
            elapsed_time_ms = int((datetime.datetime.now() - self._time_zero).total_seconds() * 1000)

            for log_data in filter(None, data.split('\t')):
                log_text = "{},{}".format(elapsed_time_ms, log_data)
                self._data_logger.debug(log_text)

                if self._log_to_plotter:
                    data_plot_queue.put({"id": self._title, "time": elapsed_time_ms, "data": log_data})

                if self._log_to_console:
                    self.emit_response('log_data', True, log_text)

    def connect(self, port):
        self.emit_response('connected', self._interface.open_port(port), "")
        self._read_timer.stop()

    def disconnect(self):
        self.emit_response('disconnected', self._interface.close_port(), "")
        self._read_timer.stop()

    def start_read(self):
        self.emit_response('started', self._interface.start_device(), "")
        self._read_timer.start()

    def stop_read(self):
        self.emit_response('stopped', self._interface.stop_device(), "")
        self._read_timer.stop()

    def change_mode(self, mode):
        self.emit_response('mode_changed', self._interface.set_mode(int(mode)), "[{}]".format(mode))

    def change_log_handler(self, exp_name):
        if exp_name == self._exp_name:
            self.emit_response('handler_changed', False, "Name unchanged")
            return

        self._exp_name = exp_name

        self._data_logger.removeHandler(self._fh)  # Remove current handler
        self._fh.close()  # Close file
        self._fh = QtGlobalWorker._create_and_append_new_handler(self._exp_name, self._title)  # Create new handler
        self._data_logger.addHandler(self._fh)  # Attach this new handler

        self.emit_response('handler_changed', True, "[{}]".format(QtGlobalWorker.get_log_filename(self._exp_name, self._title)))

    def emit_error_signal(self):
        self.emit_response('error', False, "")

    def emit_response(self, resp_type, resp_succ, resp_arg):
        if resp_type not in self.WORKER_RESPONSE:
            return

        self._worker_response.emit(self.WORKER_RESPONSE[resp_type], resp_succ, resp_arg)

    def set_reference_time(self, t0):
        self._time_zero = t0

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
