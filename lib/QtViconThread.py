import datetime

from PyQt5.QtCore import pyqtSlot

from lib.vicon_interface import ViconInterface
from lib.template.GlobalThread import QtGlobalWorker


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
            elapsed_time_ms = int((datetime.datetime.now() - self._time_zero).total_seconds() * 1000)
            log_text = "{} {}".format(elapsed_time_ms, data)
            self._data_logger.debug(log_text)

            if self._log_to_console:
                self._worker_response.emit(self.WORKER_RESPONSE['log_data'], True, log_text)
        else:
            self._worker_response.emit(self.WORKER_RESPONSE['error'], True, "Empty frame! Stopping...")
            self.stop_read()
