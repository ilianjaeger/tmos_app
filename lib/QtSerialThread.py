from lib.serial_interface import SerialInterface
from lib.template.GlobalThread import QtGlobalWorker


class QtSerialWorker(QtGlobalWorker):
    """ Main serial worker
    """

    def __init__(self, title, exp_name, mode=0):
        # Initialize with an interval of 0 => Read sensor as soon/fast as possible
        super().__init__(title, exp_name, 0, QtGlobalWorker.DATA_TYPES['tmos'])

        self._interface = SerialInterface(mode)
