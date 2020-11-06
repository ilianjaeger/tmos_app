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
        'dev_id': {"pos": 1, "title": "Device ID"},
        'in_time': {"pos": 2, "title": "Local Time"},
        'dist_raw': {"pos": 3, "title": "Raw Value"},
        'temp': {"pos": 4, "title": "Temperature"},
        'dist_filt': {"pos": 5, "title": "Filtered value"},
        'vel': {"pos": 6, "title": "Velocity"},
        'bin_1': {"pos": 7, "title": "Presence bit"},
        'bin_2': {"pos": 8, "title": "Movement bit"}
    }

    NUM_DATA_POINTS = 100

    data_plot_queue = queue.Queue()

    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        self.setWindowTitle("TMOS Logger")

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel()
        self.label.setText(sys.stdin.encoding)
        self.main_layout.addWidget(self.label)

        # Graphs
        # self.graphs = {"dist_raw": dict(), "dist_filt": dict(), "vel": dict(), "temp": dict()}
        self.graphs = {"dist_raw": dict()}
        for gr in self.graphs:
            self.graphs[gr] = dict({"widget": pg.PlotWidget(title=self.TMOS_DATA_BIT_POS[gr]["title"]), "plots": dict()})
            self.graphs[gr]["widget"].getPlotItem().addLegend()
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="left", text=self.TMOS_DATA_BIT_POS[gr]["title"])
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="bottom", text="time")

            self.main_layout.addWidget(self.graphs[gr]["widget"])

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
                # self.label.setText(record)
                # continue
                # if record["type"] != self.DATA_TYPES['tmos']:
                #     continue

                for graph_id, obj in self.graphs.items():
                    # If plot does not exist, create it
                    if record["id"] not in self.graphs[graph_id]["plots"]:
                        self.create_graph(graph_id, record["id"])

                    self.update_graph(graph_id, self.graphs[graph_id]["plots"][record["id"]], record)
        except queue.Empty:
            pass

    def create_graph(self, graph_id, plot_name):
        self.graphs[graph_id]["plots"][plot_name] = dict()
        cur_plot = self.graphs[graph_id]["plots"][plot_name]
        cur_plot["x"] = np.array(self.NUM_DATA_POINTS * [0])
        cur_plot["y"] = np.array(self.NUM_DATA_POINTS * [0])
        cur_plot["line"] = self.graphs[graph_id]["widget"].plot(cur_plot["x"], cur_plot["y"],
                                                                pen=pg.intColor(len(self.graphs[graph_id]["plots"])),
                                                                name=plot_name)

    def update_graph(self, graph_id, cur_plot, new_data):
        cur_plot["x"][:-1] = cur_plot["x"][1:]
        cur_plot["x"][-1] = float(new_data['data'].split(',')[self.TMOS_DATA_BIT_POS["time"]["pos"]])
        cur_plot["y"][:-1] = cur_plot["y"][1:]
        cur_plot["y"][-1] = float(new_data['data'].split(',')[self.TMOS_DATA_BIT_POS[graph_id]["pos"]])
        cur_plot["line"].setData(cur_plot["x"], cur_plot["y"])

    def reset_graphs(self):
        for _, obj in self.graphs.items():
            # If plot does not exist, create it
            for _, sensor_plot in obj["plots"].items():
                sensor_plot["x"] = np.array(self.NUM_DATA_POINTS * [0])
                sensor_plot["y"] = np.array(self.NUM_DATA_POINTS * [0])
                sensor_plot["line"].setData(sensor_plot["x"], sensor_plot["y"])


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
