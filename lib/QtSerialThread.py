import logging
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from lib.serial_interface import SerialInterface

# The serial commands sent by the GUI thread
SERIAL_COMMAND = {
    'connect': 1,
    'disconnect': 2,
    'start': 3,
    'stop': 4,
    'mode': 5,
    'handler': 6,
    'console': 7
}

# The serial responses sent to the GUI thread
SERIAL_RESPONSE = {
    'error': -1,
    'connected': 1,
    'disconnected': 2,
    'started': 3,
    'stopped': 4,
    'mode_changed': 5,
    'handler_changed': 6
}


def get_log_filename(name, title):
    return "output/" + name.replace(" ", "_").upper() + "_" + title.replace(" ", "_").upper() + ".log"


def _create_and_append_new_handler(name, title):
    fh = logging.FileHandler(get_log_filename(name, title))
    fh.setLevel(logging.DEBUG)

    return fh


class QtSerialWorker(QtCore.QObject):
    """ Main serial worker
    """

    serial_response = QtCore.pyqtSignal(int, bool, str)
    serial_command = QtCore.pyqtSignal(int, str)

    def __init__(self, title, exp_name):
        super().__init__()

        # Set variables
        self.title = title
        self.exp_name = exp_name
        self.running_read = False

        # Log sensor data to console
        self.log_to_console = False

        # Serial interface
        self.serial = SerialInterface()

        # Data logger
        self.data_logger = logging.getLogger('DATA.' + self.title)
        self.data_logger.setLevel(logging.DEBUG)
        self.data_logger.propagate = False  # Very ugly solution, but it works...

        # File Handler
        self.fh = _create_and_append_new_handler(self.exp_name, self.title)
        self.data_logger.addHandler(self.fh)  # Print content to file

        # Serial read timer (we HAVE to set the parent, otherwise we need to explicitly move the timer to the thread)
        self.read_timer = QtCore.QTimer(self)
        self.read_timer.setInterval(10)

        # Signals
        self.serial_command.connect(self.received_command)  # Serial commands
        self.read_timer.timeout.connect(self.read_data)  # Read timer

    @pyqtSlot(int, str)
    def received_command(self, command, arg):
        # print("[%s] Received command" % QtCore.QThread.currentThread().objectName())

        if command == SERIAL_COMMAND['connect']:
            self.connect(arg)
        elif command == SERIAL_COMMAND['disconnect']:
            self.disconnect()
        elif command == SERIAL_COMMAND['start']:
            self.start_read()
        elif command == SERIAL_COMMAND['stop']:
            self.stop_read()
        elif command == SERIAL_COMMAND['mode']:
            self.change_mode(arg)
        elif command == SERIAL_COMMAND['handler']:
            self.change_log_handler(arg)
        elif command == SERIAL_COMMAND['console']:
            self.change_log_to_console(arg)

    @pyqtSlot()
    def read_data(self):
        # print("[%s] Timeout reached" % QtCore.QThread.currentThread().objectName())

        data = self.serial.process_data()

        if data != '':
            self.data_logger.debug(data)

            if self.log_to_console:
                logging.debug(str(self.serial.get_port()) + data)  # print(data)

    def connect(self, port):
        if self.serial.open_port(port):
            self.serial_response.emit(SERIAL_RESPONSE['connected'], True, "")
        else:
            self.serial_response.emit(SERIAL_RESPONSE['connected'], False, "")

        self.running_read = False
        self.read_timer.stop()

    def disconnect(self):
        if self.serial.close_port():
            self.serial_response.emit(SERIAL_RESPONSE['disconnected'], True, "")
        else:
            self.serial_response.emit(SERIAL_RESPONSE['disconnected'], False, "")

        self.running_read = False
        self.read_timer.stop()

    def start_read(self):
        if self.serial.connect_device():
            self.serial_response.emit(SERIAL_RESPONSE['started'], True, "")
        else:
            self.serial_response.emit(SERIAL_RESPONSE['started'], False, "")

        self.running_read = True
        self.read_timer.start()

    def stop_read(self):
        if self.serial.stop_device():
            self.serial_response.emit(SERIAL_RESPONSE['stopped'], True, "")
        else:
            self.serial_response.emit(SERIAL_RESPONSE['stopped'], False, "")

        self.running_read = False
        self.read_timer.stop()

    def emit_error_signal(self):
        self.serial_response.emit(SERIAL_RESPONSE['error'], False, "")
        self.running_read = False

    def change_mode(self, mode):
        self.serial_response.emit(SERIAL_RESPONSE['mode_changed'], self.serial.set_mode(int(mode)), "[{}]".format(mode))

    def change_log_handler(self, exp_name):
        if exp_name == self.exp_name:
            self.serial_response.emit(SERIAL_RESPONSE['handler_changed'], False, "Name unchanged")
            return

        self.exp_name = exp_name

        self.data_logger.removeHandler(self.fh)  # Remove current handler
        self.fh.close()  # Close file
        self.fh = _create_and_append_new_handler(self.exp_name, self.title)  # Create new handler
        self.data_logger.addHandler(self.fh)  # Attach this new handler

        self.serial_response.emit(SERIAL_RESPONSE['handler_changed'], True,
                                  "[{}]".format(get_log_filename(self.exp_name, self.title)))

    def change_log_to_console(self, activate):
        self.log_to_console = activate == 'True'
