import sys
import glob
import time
import serial
import struct
import numpy as np
import logging

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

    def __init__(self):
        self._port = None
        self._timeout = 0.5
        self._baudraute = 115200
        self._parity = 'N'
        self._stop_bits = 1


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
        """ Connect to device
        """
        
        logger.info("Connecting...")
        self._comm.write(b'CONNECT\r\n')
        '''time.sleep(0.5)
        print(self._port, ": ", self._comm.readline())
        time.sleep(2)

        logger.info("Start sensor reading...")
        self._comm.write(b'START 0\r\n')
        time.sleep(2)
        print(self._port, ": ", self._comm.readline())
        print(self._port, ": ", self._comm.readline())
        time.sleep(0.5)'''

        logger.info("Initialization complete!")


    def close_port(self):
        """ Closes a port
        """

        if self._comm != None:
            self._comm.close()


    def send_serial_data(self, d):
        """ Send data to serial port.
        """

        # Aquire lock
        self._lock.acquire()
        logger.debug(" --- Sending data ---")

        start_t = time.time()

        # First send the number of data points to be sent
        # Pack the length into 4 bytes
        self._comm.write(struct.pack('<I', len(d)))

        # for i in tqdm(range(len(d))):
        for i in range(len(d)):
            self._comm.write(struct.pack('<B', d[i]))
        
        logger.debug("\t[" + str(len(d)) + " bytes sent in " + str(time.time() - start_t) + " ms]")
        logger.debug(" -- END Sending data --")
        self._lock.release()


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
            #read_string = self._comm.read_until().decode('utf-8').rstrip("\n")
            read_string = self._comm.readline().decode('ascii')
        except:
            pass
        
        return read_string


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
    