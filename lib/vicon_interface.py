import logging
import socket
import datetime

from lib.template import GlobalInterface
from pyvicon import pyvicon
from pyvicon.pyvicon import *

# Start vicon logger - Global logger, since there are multiple instances of the SerialInterface class
logger = logging.getLogger('VICON.COMM')
logger.setLevel(logging.INFO)


################################################
# VICON COMMUNICATION                          #
#                                              #
# - Handles all the communication with the     #
#   Vicon system                               #
#                                              #
################################################


class ViconInterface(GlobalInterface.GlobalInterface):
    """ Main serial interface
    """

    def __init__(self):
        super(ViconInterface, self).__init__()

        self._comm = pyvicon.PyVicon()
        self._port = "192.168.10.1"

    def open_port(self, port):
        """ Opens a port

            :returns:
                true if the port was successfully opened
        """

        # self._port = port
        try:
            logger.debug("Opening %s", str(port))

            if self._comm is None:
                self._comm = pyvicon.PyVicon()

            # The Connect function from the Vicon library is not thread safe. In order to check if it is possible
            # to connect to the camera system (IP reachable), try it with socket instead
            try:
                s = socket.create_connection((port, 801), timeout=0.1)
                s.close()  # Don't forget to close it before trying it with the Vicon library!
            except socket.timeout:
                logger.debug("Socket error")
                return False

            # Connect
            self._comm.connect(port)

            # Failed connect
            if not self._comm.is_connected():
                return False

            logger.debug("Vicon connected!")

            self._comm.set_stream_mode(pyvicon.StreamMode.ServerPush)
            self._comm.enable_segment_data()
            self._comm.enable_marker_data()
            self._comm.enable_unlabeled_marker_data()
            self._comm.enable_device_data()

            logger.debug("Vicon configuration complete!")
        except :
            self._comm = None
            return False

        return True

    def is_connected(self):
        """ Check if there is a port connected

            :returns:
                Returns true if it is connected
        """
        return self._comm is not None and self._comm.is_connected()

    def stop_device(self):
        """ Stop reading

            :returns:
                True if reading successfully stopped
        """
        if not self.is_connected():
            return False

        pass

        return True

    def start_device(self):
        """ Connect and start device

            :returns:
                Returns true if it is connected
        """

        if not self.is_connected() or not self._comm.get_frame():
            return False
        return True

    def close_port(self):
        """ Closes a port

            :returns:
                Returns true port was successfully closed
        """

        if self.is_connected():
            try:
                self._comm.disconnect()
            except :
                self._comm = None
                return False

        return True

    def process_data(self):
        """ Process the data received from the MCU

            :returns:
                Returns true data was successfully processed
        """

        if not self.is_connected():
            return -1

        try:
            ret = self._comm.get_frame()
            logger.debug("Get frame: {}".format(ret))
            if ret != 2:
                count = self._comm.get_subject_count()
                logger.debug("Get count: {}".format(count))
                log_text = ''
                for i in range(0, count):
                    segment_name = self._comm.get_subject_name(i)
                    logger.debug("Get name: {}".format(segment_name))
                    elapsed_time_ms = str(int((datetime.datetime.now() - self._time_zero).total_seconds() * 1000))
                    pos = self._comm.get_segment_global_translation(segment_name, segment_name)
                    logger.debug("Get name: {}".format(pos))

                    if pos is not None:
                        log_text = log_text + "{},{},{:.2f},{:.2f},{:.2f}\t".format(elapsed_time_ms, segment_name, pos[0], pos[1], pos[2])
                    else:
                        log_text = log_text + "{},{},0,0,0\t".format(elapsed_time_ms, segment_name)
                    logger.debug("Done")
                return log_text
            else:
                logger.debug("Fehler")
        except:
            pass

        return -1

    def read_text(self):
        """ Receive text from serial port.

            :returns:
                Decoded and stripped text
        """

        pass

    def get_version(self):
        if self._comm is None:
            return ''

        return "linux_edition"
