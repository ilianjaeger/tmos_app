from lib.serial_interface import SerialInterface
from lib.template.GlobalThread import QtGlobalWorker


class QtSerialWorker(QtGlobalWorker):
    """ Main serial worker
    """

    def __init__(self, title, exp_name, interval):
        super().__init__(title, exp_name, interval, QtGlobalWorker.DATA_TYPES['tmos'])

        self._interface = SerialInterface()
