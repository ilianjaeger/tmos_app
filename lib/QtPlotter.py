import queue
from random import randint

from PyQt5 import QtCore, QtWidgets

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock


data_plot_queue = queue.Queue()


class QtLivePlotter(Dock):
    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        # Graph
        self.graph = pg.PlotWidget()

        self.addWidget(self.graph)

        # Use 200 points
        self.x = 200 * [0]
        self.y = 200 * [0]

        self.new_pen = pg.mkPen(width=4, style=QtCore.Qt.DashLine)

        self.line = self.graph.plot(self.x, self.y, pen=self.new_pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        global data_plot_queue

        try:
            # Get all queued points
            while not data_plot_queue.empty():
                record = data_plot_queue.get(block=False)

                self.x = self.x[1:]
                self.x.append(record["x"])

                self.y = self.y[1:]
                self.y.append(record["y"])

                self.line.setData(self.x, self.y, pen=self.new_pen)
        except queue.Empty:
            pass
