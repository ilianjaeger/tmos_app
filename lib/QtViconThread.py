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

        if data == -1:
            self._worker_response.emit(self.WORKER_RESPONSE['error'], True,
                                       "Lost connection or empty frame! Stopping...")
            self.stop_read()
        elif type(data) == str:
            elapsed_time_ms = int((datetime.datetime.now() - self._time_zero).total_seconds() * 1000)

            for log_data in filter(None, data.split('\t')):
                log_text = "{},{}".format(elapsed_time_ms, log_data)
                self._data_logger.debug(log_text)

                if self._log_to_console:
                    self._worker_response.emit(self.WORKER_RESPONSE['log_data'], True, log_text)
