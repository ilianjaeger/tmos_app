import sys
import glob
import time
import serial
import logging
import datetime

from lib.template import GlobalInterface

# Start serial logger - Global logger, since there are multiple instances of the SerialInterface class
logger = logging.getLogger('PC.COMM')
logger.setLevel(logging.INFO)


################################################
# SERIAL COMMUNICATION                         #
#                                              #
# - Handles all the communication with the MCU #
#                                              #
################################################


class SerialInterface(GlobalInterface.GlobalInterface):
    """ Main serial interface
    """

    def __init__(self, mode=0):
        super(SerialInterface, self).__init__(mode)

        self._baudraute = 115200
        self._parity = 'N'
        self._stop_bits = 1


    def open_port(self, port):
        """ Opens a port

            :returns:
                true if the port was successfully opened
        """

        self._port = port
        try:
            logger.debug("Opening %s", str(port))
            self._comm = serial.Serial(baudrate=self._baudraute, port=self._port, timeout=self._timeout,
                                       parity=self._parity, stopbits=self._stop_bits)
            if not self._comm.isOpen():
                return False

            logger.debug("MCU connected!")

            self.stop_device()

        except serial.SerialException:
            self._comm = None
            # self.emit_error_signal()
            return False

        return True

    def is_connected(self):
        """ Check if there is a port connected

            :returns:
                Returns true if it is connected
        """
        return self._comm is not None and self._comm.isOpen()

    def stop_device(self):
        """ Stop reading

            :returns:
                True if reading successfully stopped
        """
        if not self.is_connected():
            return False

        try:
            self._comm.write(b'STOP\r\n')  # Stop any ongoing reading
            self._comm.reset_input_buffer()  # flush buffer

        except serial.SerialException:
            self._comm = None
            # self.emit_error_signal()
            return False

        return True

    def start_device(self):
        """ Connect and start device

            :returns:
                Returns true if it is connected
        """

        if not self.is_connected():
            return False

        try:
            logger.debug("Stopping and resetting device")
            if not self.stop_device():
                return False

            logger.debug("Connecting")
            # Send CONNECTED command and wait for ACK
            self._comm.write(b'CONNECT\r\n')

            # Sometimes it takes up to 3 seconds... :(
            if not (self.wait_for_text_timeout("CONNECTED ", 3000) and self.wait_for_text_timeout(">", 3000)):
                logger.error("Could not connect to board")
                return False

            # Send START command
            logger.debug("Start sensor reading [MODE " + str(self._mode) + " - " + ("SLOW", "FAST")[self._mode] + "]")
            self._comm.write(bytes("START {}\r\n".format(self._mode), 'utf8'))

            if not self.wait_for_text_timeout("Start Measurements", 600):
                logger.error("Could not start reading")
                return False

            logger.debug("Initialization complete!")

            time.sleep(1)

        except serial.SerialException:
            self._comm = None
            # self.emit_error_signal()
            return False

        return True

    def close_port(self):
        """ Closes a port

            :returns:
                Returns true port was successfully closed
        """

        if self.is_connected():
            try:
                self._comm.close()
            except serial.SerialException:
                self._comm = None
                # self.emit_error_signal()
                return False

        return True

    def process_data(self):
        """ Process the data received from the MCU

            :returns:
                Returns true data was successfully processed
        """

        if not self.is_connected():
            return -1

        log_text = ''
        try:
            recv = self.read_text()
            while recv != '':

                list_data = recv.split('\t')  # Data separated by tabs
                n = len(list_data)  # Number of elements

                # We always receive 10 data elements
                if n != 10:
                    logger.debug("Wrong data received! Skipping [{}]".format(recv))
                    return ''

                # list_data = list_data[1:n - 1]  # First and last elements are garbage
                list_data = list_data[0:n - 1]
                list_data[0] = str(int((datetime.datetime.now() - self._time_zero).total_seconds() * 1000))

                log_text = log_text + ','.join(map(str, list_data)) + '\t'

                recv = self.read_text()

        except serial.SerialException:
            self._comm = None
            self.emit_error_signal()
            return -1

        return log_text

    def read_text(self):
        """ Receive text from serial port.

            :returns:
                Decoded and stripped text
        """

        if not self.is_connected() or not self._comm.in_waiting:
            return ''

        try:
            read_string = self._comm.readline().decode('ascii').rstrip("\r\n")
        except serial.SerialException:
            self._comm = None
            self.emit_error_signal()
            return ''
        except UnicodeDecodeError:
            logger.debug("Can't decode text")
            return ''

        return read_string

    def wait_for_text_timeout(self, txt, timeout_ms):
        """ Wait for a specific text/pattern. Timeout given in seconds

            :returns:
                true if there was a match, false for a timeout
        """

        t0 = datetime.datetime.now()

        while int((datetime.datetime.now() - t0).total_seconds() * 1000) < timeout_ms:
            if self.read_text() == txt:
                return True

        logger.error("Did not receive '{}'".format(txt))
        return False


def list_available_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
