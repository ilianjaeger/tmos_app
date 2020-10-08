import sys
import glob
import time
import serial
import struct
import numpy as np
import logging
import datetime

# Start logger
logger = logging.getLogger('PC.COMM')
logger.setLevel(logging.INFO)


################################################
# SERIAL COMMUNICATION                         #
#                                              #
# - Handles all the communication with the MCU #
#                                              #
################################################


class SerialInterface(object):
    """ Main serial interface
    """

    def __init__(self, mode):
        self._port = None
        self._timeout = 0.5
        self._baudraute = 115200
        self._parity = 'N'
        self._stop_bits = 1
        self._mode = int(mode)
        self._online = False


    def open_port(self, port):
        """ Opens a port
        """

        self._port = port
        try:
            logger.debug("Opening " + str(port))
            self._comm  = serial.Serial(baudrate = self._baudraute, port = self._port, timeout=self._timeout, parity = self._parity, stopbits = self._stop_bits)
            if not self._comm.isOpen():
                return False

            logger.info("MCU connected!")
        except(serial.SerialException):
            self._comm = None
            return False

        return True


    def connect_device(self):
        """ Connect and start device
        """
        
        logger.info("Stopping and resetting device")
        self._comm.write(b'STOP\r\n') # Stop any ongoing reading
        self._comm.reset_input_buffer() # flush buffer

        logger.info("Connecting")
        # Send CONNECTED command and wait for ACK
        self._comm.write(b'CONNECT\r\n')

        # Sometimes it takes up to 3 seconds... :(
        if not (self.wait_for_text_timeout("CONNECTED ", 3.0) and self.wait_for_text_timeout(">", 3.0)):
            logger.error("Could not connect to board")
            self._online = False
            return False

        # Send START command
        logger.info("Start sensor reading [MODE " + str(self._mode) + " - " + ("SLOW", "FAST")[self._mode] + "]")
        self._comm.write(bytes("START {}\r\n".format(self._mode), 'utf8'))
        
        if not self.wait_for_text_timeout("Start Measurements", 0.6):
            logger.error("Could not start reading")
            self._online = False
            return False

        logger.info("Initialization complete!")
        self._online = True
        return True


    def close_port(self):
        """ Closes a port
        """

        if self._comm != None:
            self._comm.close()


    def receive_serial_data(self, size):
        """ Receive data from serial port.

            :returns:
                Numpy array with the received data (1 dimensional)
        """

        if self._comm == None:
            return np.array([])

        logger.debug(" --- Receiving data ---")
        logger.debug("\t[Expecting " + str(size) + " bytes]")

        # start with a dict, as it is easier to append values
        recv_data = []
        bytes_received = 0
        # for i in tqdm(range(size)):
        for i in range(size):
            data = self._comm.read(1)
            if len(data) == 0 and len(recv_data) != 0:
                break
            elif len(data) != 0:
                # Unpack data
                recv_data.append(struct.unpack('>B', data))
                bytes_received = bytes_received + 1

        logger.debug("\t[" + str(bytes_received) + "/" + str(size) + " bytes received]")

        if bytes_received != size:
            logger.debug("\tFilling missing data with zeros")
            for i in range(size - bytes_received):
                # Append a tuple, since struct.unpack also returns a tuple
                recv_data.append((0,))

        logger.debug(" -- END Receiving data --")

        # Transform dict to numpy array
        return np.array(recv_data).astype('uint8')


    def read_text(self):
        """ Receive text from serial port.

            :returns:
                Decoded and stripped text
        """

        if not self._comm.in_waiting:
            return ''

        read_string = ''
        try:
            read_string = self._comm.readline().decode('ascii').rstrip("\r\n")
        except:
            pass
        
        return read_string

    def wait_for_text_timeout(self, txt, timeout_s):
        """ Wait for a specific text/pattern. Timeout given in seconds

            :returns:
                true if there was a match, false for a timeout
        """
        
        t0 = datetime.datetime.now()
        timeout_us = timeout_s * 1000000
       
        while ((datetime.datetime.now() - t0).microseconds < timeout_us):             
            if(self.read_text() == txt):
                return True

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
    