import sys
import logging

from PyQt5 import QtWidgets, QtGui, QtCore

from lib import QtLogger
from lib import QtSensor

# Initialize logger
logging.getLogger().setLevel(logging.INFO)


def load_style(filename):
    # Add the stylesheet to the application
    try:
        fh = open(filename, "r")
        return fh.read()
    except FileNotFoundError:
        pass

    return ""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_instance, *args):
        super().__init__(*args)

        self.app_instance = app_instance

        self.style_dark = load_style("style/dark.css")

        self.style_menu_dark = QtWidgets.QAction("Dark", self)
        self.style_menu_dark.setStatusTip('Set to dark mode')
        self.style_menu_dark.triggered.connect(lambda: self.change_style('dark'))

        self.style_menu_classic = QtWidgets.QAction("Classic", self)
        self.style_menu_classic.setStatusTip('Set to light mode')
        self.style_menu_classic.triggered.connect(lambda: self.change_style('classic'))

        main_menu = self.menuBar()
        main_menu = main_menu.addMenu('Window')
        main_menu.addAction(self.style_menu_dark)
        main_menu.addAction(self.style_menu_classic)

        ''' WIDGET CONFIGURATION '''
        # Sensors
        self.sensor_box = QtSensor.QtSensor("TMOS STM32", self)

        # Log Box
        self.log_text_box = QtLogger.QLoggerBox()

        ''' MAIN LAYOUT '''
        # Main vertical Layout
        root_layout = QtWidgets.QVBoxLayout()
        root_layout.addWidget(self.sensor_box)
        root_layout.addWidget(self.log_text_box)

        # scroll bar
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)

        # Main central widget (main content)
        self.main_central_widget = QtWidgets.QWidget(self.scroll)
        self.main_central_widget.setLayout(root_layout)
        self.scroll.setWidget(self.main_central_widget)

        # Set scroll area as main window central widget
        self.setCentralWidget(self.scroll)

        # Set dark theme as default
        self.change_style('dark')

    def adjust_widget_size(self):
        self.main_central_widget.adjustSize()
        self.resize(self.main_central_widget.sizeHint())

    def set_title(self):
        self.setWindowTitle("TMOS STM32 App")

    def set_icons(self):
        # Set icon
        app_icon = QtGui.QIcon()
        app_icon.addFile('img/motion_sensor_16.png', QtCore.QSize(16, 16))
        app_icon.addFile('img/motion_sensor_24.png', QtCore.QSize(24, 24))
        app_icon.addFile('img/motion_sensor_32.png', QtCore.QSize(32, 32))
        app_icon.addFile('img/motion_sensor_64.png', QtCore.QSize(64, 64))
        self.setWindowIcon(app_icon)

    def change_style(self, style):
        if style == 'dark':
            self.app_instance.setStyleSheet(self.style_dark)
        else:
            self.app_instance.setStyleSheet("")

        self.log_text_box.adapt_colors_to_mode(style)


if __name__ == '__main__':
    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = MainWindow(app)

    # Start
    main_window.show()
    main_window.adjust_widget_size()

    app.exec_()
