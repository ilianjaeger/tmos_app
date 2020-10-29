import queue
import numpy as np

from PyQt5 import QtCore

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock

data_plot_queue = queue.Queue()


class QtLivePlotter(Dock):
    DATA_TYPES = {
        'nan': 0,
        'tmos': 1,
        'vicon': 2
    }

    TMOS_DATA_BIT_POS = {
        'in_time': {"pos": 1, "title": "Local Time"},
        'dist_raw': {"pos": 2, "title": "Raw Value"},
        'temp': {"pos": 3, "title": "Temperature"},
        'dist_filt': {"pos": 4, "title": "Filtered value"},
        'vel': {"pos": 5, "title": "Velocity"},
        'bin_1': {"pos": 6, "title": "Presence bit"},
        'bin_2': {"pos": 7, "title": "Movement bit"}
    }

    NUM_DATA_POINTS = 200

    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        # Graphs
        self.graphs = {"dist_raw": dict(), "dist_filt": dict(), "vel": dict(), "temp": dict()}
        for gr in self.graphs:
            self.graphs[gr] = dict({"widget": pg.PlotWidget(title=self.TMOS_DATA_BIT_POS[gr]["title"]), "plots": dict()})
            self.graphs[gr]["widget"].getPlotItem().addLegend()
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="left", text=self.TMOS_DATA_BIT_POS[gr]["title"])
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="bottom", text="time")

            self.addWidget(self.graphs[gr]["widget"])

        # Current plot number (used for color index)
        self.current_index = 0

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

                if record["type"] != self.DATA_TYPES['tmos']:
                    continue

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
        cur_plot["x"][-1] = new_data['time']
        cur_plot["y"][:-1] = cur_plot["y"][1:]
        cur_plot["y"][-1] = float(new_data['data'].split(',')[self.TMOS_DATA_BIT_POS[graph_id]["pos"]])
        cur_plot["line"].setData(cur_plot["x"], cur_plot["y"])
