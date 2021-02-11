import sys
import queue
import numpy as np

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot

import pyqtgraph as pg


class QThread1(QtCore.QThread):
    def __init__(self, data_queue, parent=None):
        QtCore.QThread.__init__(self, parent)

        self.data_queue = data_queue

    def run(self):
        while True:
            line = sys.stdin.readline()

            data = line.split('\t')
            if len(data) > 2:
                self.data_queue.put(dict({"id": data[0], "type": data[1], "data": data[2]}))


class QtLivePlotter(QtWidgets.QMainWindow):
    DATA_TYPES = {
        'nan': 0,
        'tmos': 1,
        'vicon': 2
    }

    TMOS_DATA_BIT_POS = {
        'time': {"pos": 0, "title": "PC time"},
        'temp_1': {"pos": 1, "title": "temp TMOS 1"},
        'temp_2': {"pos": 2, "title": "temp TMOS 2"},
        'data_1': {"pos": 3, "title": "TMOS 1"},
        'data_2': {"pos": 4, "title": "TMOS 2"}
    }

    NUM_DATA_POINTS = 100

    data_plot_queue = queue.Queue()

    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        self.setWindowTitle("TMOS Logger")

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()

        # Graph for TMOS data
        self.tmos_graph = dict({"widget": None, "plots": dict()})
        self.tmos_graph["widget"] = pg.PlotWidget(title="TMOS Log")
        self.tmos_graph["widget"].getPlotItem().addLegend()
        self.tmos_graph["widget"].getPlotItem().setLabel(axis="left", text="T_obj")
        self.tmos_graph["widget"].getPlotItem().setLabel(axis="bottom", text="time")

        # Create lines for both TMOS sensors
        self.create_graph(self.tmos_graph, 'data_1')
        self.create_graph(self.tmos_graph, 'data_2')

        # Add graph to main layout
        self.main_layout.addWidget(self.tmos_graph['widget'])

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.read_thread = QThread1(self.data_plot_queue)
        self.read_thread.start()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    @pyqtSlot()
    def update_plot(self):
        try:
            # Get all queued points
            while not self.data_plot_queue.empty():
                record = self.data_plot_queue.get(block=False)

                if int(record['type']) == self.DATA_TYPES['tmos']:
                    self.update_tmos_graph('data_1', record['data'])
                    self.update_tmos_graph('data_2', record['data'])
        except queue.Empty:
            pass

    def create_graph(self, graph, plot_name):
        graph["plots"][plot_name] = dict()

        graph["plots"][plot_name]["x"] = np.array(self.NUM_DATA_POINTS * [0])
        graph["plots"][plot_name]["y"] = np.array(self.NUM_DATA_POINTS * [0])
        graph["plots"][plot_name]["line"] = graph["widget"].plot(graph["plots"][plot_name]["x"],
                                                                 graph["plots"][plot_name]["y"],
                                                                 pen=pg.intColor(len(graph["plots"])),
                                                                 name=self.TMOS_DATA_BIT_POS[plot_name]['title'])

    def update_tmos_graph(self, data_name, new_data):
        self.tmos_graph['plots'][data_name]["x"][:-1] = self.tmos_graph['plots'][data_name]["x"][1:]
        self.tmos_graph['plots'][data_name]["x"][-1] = float(new_data.split(',')[self.TMOS_DATA_BIT_POS["time"]["pos"]])
        self.tmos_graph['plots'][data_name]["y"][:-1] = self.tmos_graph['plots'][data_name]["y"][1:]
        self.tmos_graph['plots'][data_name]["y"][-1] = float(new_data.split(',')[self.TMOS_DATA_BIT_POS[data_name]["pos"]])
        self.tmos_graph['plots'][data_name]["line"].setData(self.tmos_graph['plots'][data_name]["x"], self.tmos_graph['plots'][data_name]["y"])


if __name__ == '__main__':
    # sys.stdin = open("output/ALL_TEMP_SENSOR_1.log")

    # Main application
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QThread.currentThread().setObjectName('main')

    # Main window
    main_window = QtLivePlotter()

    # Show windows
    main_window.show()

    app.exec_()
