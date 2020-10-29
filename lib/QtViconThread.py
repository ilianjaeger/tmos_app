import datetime

from PyQt5.QtCore import pyqtSlot

from lib.vicon_interface import ViconInterface
from lib.template.GlobalThread import QtGlobalWorker


class QtViconWorker(QtGlobalWorker):
    """ Main serial worker
    """

    def __init__(self, title, exp_name, interval):
        super().__init__(title, exp_name, interval, QtGlobalWorker.DATA_TYPES['vicon'])

        self._interface = ViconInterface()
