import time
import logging
import datetime

from lib import GlobalInterface
from vicon_dssdk import ViconDataStream

# Start vicon logger - Global logger, since there are multiple instances of the SerialInterface class
logger = logging.getLogger('VICON.COMM')
logger.setLevel(logging.DEBUG)

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

        self._comm = ViconDataStream.Client()
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
                self._comm = ViconDataStream.Client()

            self._comm.Connect(port)

            if not self._comm.IsConnected():
                return False

            logger.debug("Vicon connected!")

            self._comm.SetStreamMode(ViconDataStream.Client.StreamMode.EServerPush)
            self._comm.EnableSegmentData()
            self._comm.EnableMarkerData()
            self._comm.EnableUnlabeledMarkerData()
            self._comm.EnableDeviceData()
            # self._comm.SetAxisMapping(ViconDataStream.CoreClient.Forward, ViconDataStream.CoreClient.Left,
            #                           ViconDataStream.CoreClient.Up)

            logger.debug("Vicon configuration complete!")
        except ViconDataStream.DataStreamException:
            self._comm = None
            return False

        return True

    def is_connected(self):
        """ Check if there is a port connected

            :returns:
                Returns true if it is connected
        """
        return self._comm is not None and self._comm.IsConnected()

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

        if not self.is_connected() or not self._comm.GetFrame():
            return False
        return True

    def close_port(self):
        """ Closes a port

            :returns:
                Returns true port was successfully closed
        """

        if self.is_connected():
            try:
                self._comm.Disconnect()
            except ViconDataStream.DataStreamException:
                self._comm = None
                return False

        return True

    def process_data(self):
        """ Process the data received from the MCU

            :returns:
                Returns true data was successfully processed
        """

        if not self.is_connected():
            return ''

        # print("Trying")
        # return ''
        try:
            if self._comm.GetFrame():
                names = self._comm.GetSubjectNames()
                for i in names:
                    # print('obj', i)
                    segment_names = self._comm.GetSegmentNames(i)
                    for s in segment_names:
                        # print('segment', s)
                        pos = self._comm.GetSegmentGlobalTranslation(i, s)
                        return "{}, {}, {}, {}".format(s, pos[0][0], pos[0][1], pos[0][2])
        except ViconDataStream.DataStreamException as e:
            pass
            # self._comm.GetFrame()

        return ''

    def read_text(self):
        """ Receive text from serial port.

            :returns:
                Decoded and stripped text
        """

        pass

    def get_version(self):
        if self._comm is None:
            return ''

        ver = self._comm.GetVersion()
        if type(ver) is not tuple and len(ver) < 3:
            return "Unknown"

        return str(ver[0]) + "." + str(ver[1]) + "." + str(ver[2])
