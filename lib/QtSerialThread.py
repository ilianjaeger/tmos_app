import logging
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from lib.serial_interface import SerialInterface

# The serial commands sent by the GUI thread
SERIAL_COMMAND = {
    'connect': 1,
    'disconnect': 2,
    'start': 3,
    'stop': 4
}

# The serial responses sent to the GUI thread
SERIAL_RESPONSE = {
    'error': -1,
    'connected': 1,
    'disconnected': 2,
    'started': 3,
    'stopped': 4
}


class QtSerialWorker(QtCore.QObject):
    """ Main serial worker
    """

    serial_response = QtCore.pyqtSignal(int, bool)
    serial_command = QtCore.pyqtSignal(int, str)

    def __init__(self, title):
        super().__init__()

        # Set variables
        self.title = title
        self.running_read = False

        # Serial interface
        self.serial = SerialInterface(0)

        # Data logger
        self.data_logger = logging.getLogger(self.title)
        self.data_logger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(title.replace(" ", "_").upper() + ".log")
        self.fh.setLevel(logging.DEBUG)
        self.data_logger.addHandler(self.fh)  # Print content to file
        self.data_logger.propagate = False  # Very ugly solution, but it works...

        # Signals
        self.serial_command.connect(self.received_command)

    @pyqtSlot(int, str)
    def received_command(self, command, arg):
        print("[%s] Processing" % QtCore.QThread.currentThread().objectName())

        if command == SERIAL_COMMAND['connect']:
            self.connect(arg)
        elif command == SERIAL_COMMAND['disconnect']:
            self.disconnect()
        elif command == SERIAL_COMMAND['start']:
            self.start_read()
        elif command == SERIAL_COMMAND['stop']:
            self.stop_read()

    def connect(self, port):
        if self.serial.open_port(port):
            self.serial_response.emit(SERIAL_RESPONSE['connected'], True)
        else:
            self.serial_response.emit(SERIAL_RESPONSE['connected'], False)

        self.running_read = False

    def disconnect(self):
        if self.serial.close_port():
            self.serial_response.emit(SERIAL_RESPONSE['disconnected'], True)
        else:
            self.serial_response.emit(SERIAL_RESPONSE['disconnected'], False)

        self.running_read = False

    def start_read(self):
        if self.serial.connect_device():
            self.serial_response.emit(SERIAL_RESPONSE['started'], True)
        else:
            self.serial_response.emit(SERIAL_RESPONSE['started'], False)

        self.running_read = True

    def stop_read(self):
        if self.serial.stop_device():
            self.serial_response.emit(SERIAL_RESPONSE['stopped'], True)
        else:
            self.serial_response.emit(SERIAL_RESPONSE['stopped'], False)

        self.running_read = False

    def emit_error_signal(self):
        self.serial_response.emit(SERIAL_RESPONSE['error'], False)
        self.running_read = False


class QtSerialThread(QtCore.QThread):
    """ Main serial thread object
    """

    def __init__(self, title, worker):
        QtCore.QThread.__init__(self)

        # Set thread name
        self.title = title.replace(" ", "_").upper()
        self.setObjectName(self.title)

        self.worker = worker

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            print("running " + self.title)

            '''if self.worker.running_read:
                self.worker.received_command(SERIAL_COMMAND['start'], '')
                # data = self.process_data()
                # if data != '':
                #    self.data_logger.debug(data)'''
            self.sleep(2)
            self.
