import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot

from vicon_dssdk import ViconDataStream


class QVicon(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(QVicon, self).__init__(parent)

        # Start own module logger
        self.logger = logging.getLogger('VICON')
        self.logger.setLevel(logging.INFO)

        ''' VICON SETUP '''
        # Create Vicon instance
        self.vicon = ViconDataStream.Client()

        # Retrieve version
        self._version = self.vicon.GetVersion()

        ''' WIDGET '''
        # Create root layout
        self.root_layout = QtWidgets.QVBoxLayout()

        self.setTitle("Vicon")
        self.setCheckable(False)
        self.setLayout(self.root_layout)

        # Version label
        self.version_label = QtWidgets.QLabel()
        self.version_label.setText("SDK Version: " + self.get_version())

        # IP address label
        self.IP_address_label = QtWidgets.QLabel()
        self.IP_address_label.setText("IP Address: " + self.get_IP_address())

        self.root_layout.addWidget(self.version_label)
        self.root_layout.addWidget(self.IP_address_label)

    def get_version(self):
        if type(self._version) is not tuple and len(self._version) < 3:
            return "Unknown"

        return str(self._version[0]) + "." + str(self._version[1]) + "." + str(self._version[2])

    def get_IP_address(self):
        return "192.168.0.1"
