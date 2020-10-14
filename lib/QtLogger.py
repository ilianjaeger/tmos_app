from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
import logging
import queue

# Logging colors
COLORS = {
    'WARNING': "orange",
    'INFO': "black",
    'DEBUG': "blue",
    'CRITICAL': "orange",
    'ERROR': "red"
}


class QLoggingHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()

        self.setFormatter(logging.Formatter('[%(name)s] [%(levelname)s] %(message)s'))
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class QLoggerBox(QtWidgets.QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)

        # Set the logger
        self.logger = logging.getLogger()  # 'APP_Logger'
        self.logger.setLevel(logging.DEBUG)

        # Create and add handler
        self.log_queue = queue.Queue()
        self.log_handler = QLoggingHandler(self.log_queue)
        self.logger.addHandler(self.log_handler)
        # logging.getLogger().addHandler(self) # Bind root logger

        # Set the widget
        # self.widget = QtWidgets.QPlainTextEdit(parent)
        self.setReadOnly(True)

        # Polling timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.add_record)
        self.timer.start()

    @pyqtSlot()
    def add_record(self):
        try:
            record = self.log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = self.log_handler.format(record)
            self.appendHtml("<font color=" + COLORS[record.levelname] + ">" + msg + "</font>")
