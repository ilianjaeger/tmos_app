from PyQt5 import QtWidgets
import logging

# Logging colors
COLORS = {
    'WARNING': "orange",
    'INFO': "black",
    'DEBUG': "blue",
    'CRITICAL': "orange",
    'ERROR': "red"
}


class QLoggerBox(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        
        # Set the logger
        self.setFormatter(logging.Formatter('[%(name)s] [%(levelname)s] %(message)s'))
        logging.getLogger().addHandler(self)

        # Set the widget
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)    

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendHtml("<font color=" + COLORS[record.levelname] + ">" + msg + "</font>")