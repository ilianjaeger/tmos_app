import socket
import logging
import datetime

from lib.template import GlobalInterface

# Start serial logger - Global logger, since there are multiple instances of the SerialInterface class
logger = logging.getLogger('PC.COMM')
logger.setLevel(logging.DEBUG)


################################################
# SERIAL COMMUNICATION                         #
#                                              #
# - Handles all the communication with the MCU #
#                                              #
################################################


class SocketInterface(GlobalInterface.GlobalInterface):
    """ Main serial interface
    """

    def __init__(self):
        super(SocketInterface, self).__init__()

        self._comm = None

    def open_port(self, port):
        """ Opens a port

            :returns:
                true if the port was successfully opened
        """

        self._port = port
        logger.debug("Opening %s", str(port))
        try:
            self._comm = socket.create_connection((port, 80), timeout=0.1)
        except socket.timeout:
            self._comm = None
            return False

        logger.debug("MCU connected!")

        return True

    def is_connected(self):
        """ Check if there is a port connected

            :returns:
                Returns true if it is connected
        """
        return self._comm is not None

    def close_port(self):
        """ Closes a port

            :returns:
                Returns true port was successfully closed
        """

        if self.is_connected():
            self._comm.close()

        return True

    def process_data(self):
        """ Process the data received from the MCU

            :returns:
                Returns true data was successfully processed
        """

        if not self.is_connected():
            return -1

        log_text = self.read_text()

        return log_text

    def read_text(self):
        """ Receive text from serial port.

            :returns:
                Decoded and stripped text
        """

        if not self.is_connected():
            return ''

        try:
            read_string = self._comm.recv(1024).decode('ascii').rstrip("\r\n")
        except socket.timeout:
            return ''
        except UnicodeDecodeError:
            logger.debug("Can't decode text")
            return ''

        logger.debug("Received {}".format(read_string))
        return read_string
