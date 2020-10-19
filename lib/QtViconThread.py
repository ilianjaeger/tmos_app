from PyQt5.QtCore import pyqtSlot

from lib.vicon_interface import ViconInterface
from lib.GlobalThread import QtGlobalWorker


class QtViconWorker(QtGlobalWorker):
    """ Main serial worker
    """

    def __init__(self, title, exp_name, interval):
        super().__init__(title, exp_name, interval)

        self._interface = ViconInterface()

    @pyqtSlot()
    def read_data(self):
        data = self._interface.process_data()

        if data != '':
            self._data_logger.debug(data)

            if self._log_to_console:
                self._worker_response.emit(self.WORKER_RESPONSE['log_data'], True, data)
