from lib.serial_interface import SerialInterface
from lib.template.GlobalThread import QtGlobalWorker


class QtSerialWorker(QtGlobalWorker):
    """ Main serial worker
    """

    def __init__(self, title, exp_name, mode=0):
        super().__init__(title, exp_name, 0)

        self._interface = SerialInterface(mode)
