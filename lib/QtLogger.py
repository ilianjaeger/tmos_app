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


class QLoggerBox(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the logger
        self.logger = logging.getLogger()  # 'APP_Logger'
        self.logger.setLevel(logging.DEBUG)

        # Create and add handler
        self.log_queue = queue.Queue()
        self.log_handler = QLoggingHandler(self.log_queue)
        self.logger.addHandler(self.log_handler)
        # logging.getLogger().addHandler(self) # Bind root logger

        # Polling timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.add_record)
        self.timer.start()

        # Set the widgets
        self.setTitle("Log output")
        self.setCheckable(False)

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.log_widget = QtWidgets.QPlainTextEdit()
        self.log_widget.setReadOnly(True)

        self.vbox.addWidget(self.log_widget)

    @pyqtSlot()
    def add_record(self):
        try:
            record = self.log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = self.log_handler.format(record)
            self.log_widget.appendHtml("<font color=" + COLORS[record.levelname] + ">" + msg + "</font>")
