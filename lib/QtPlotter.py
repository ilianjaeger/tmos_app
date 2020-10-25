from random import randint

from PyQt5 import QtCore, QtWidgets

import pyqtgraph as pg


class QtLivePlotter(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        self.graph = pg.PlotWidget()

        self.setWindowTitle("Cool Plotter")
        self.setCentralWidget(self.graph)

        self.x = list(range(0, 200, 1))
        self.y = list(range(0, 200, 1))

        self.graph.setBackground('w')
        self.new_pen = pg.mkPen(width=2, style=QtCore.Qt.DashLine)

        self.line = self.graph.plot(self.x, self.y, pen=self.new_pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]
        self.y.append(randint(0, 500))

        self.line.setData(self.x, self.y, pen=self.new_pen)
