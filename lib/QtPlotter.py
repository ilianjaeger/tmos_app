import queue
import numpy as np
import logging

from PyQt5 import QtCore

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock

data_plot_queue = queue.Queue()


class QtLivePlotter(Dock):

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

        self.lr = []
        self.startTime = 0
        self.mov_thresh = 2000
        self.mov_detected = False
        self.door_movement_array = []
        self.door_movement_detect_time = []
        self.door_movement_detect_pos = []
        self.door_movement_detect_type = []

    def update_plot(self):
        global data_plot_queue

        try:
            # Get all queued points
            while not data_plot_queue.empty():
                record = data_plot_queue.get(block=False)

                for graph_id, obj in self.graphs.items():
                    # If plot does not exist, create it
                    if record["id"] not in self.graphs[graph_id]["plots"]:
                        self.create_graph(graph_id, record["id"])

                    self.update_graph(graph_id, self.graphs[graph_id]["plots"][record["id"]], record)

                    if graph_id == "dist_raw":
                        self.update_people_counter(record)
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

    def update_people_counter(self, new_data):
        new_dist_raw = float(new_data['data'].split(',')[self.TMOS_DATA_BIT_POS["dist_raw"]["pos"]])
        if new_dist_raw > self.mov_thresh:
            if not self.mov_detected:
                self.startTime = new_data['time']
                self.lr.append(pg.LinearRegionItem([self.startTime, self.startTime], movable=False))
                self.graphs["dist_raw"]["widget"].addItem(self.lr[-1])

            self.mov_detected = True
            self.door_movement_array.append(new_dist_raw)
            self.lr[-1].setRegion([self.startTime, new_data['time']])

        else:
            if self.mov_detected and len(self.door_movement_array) != 0:
                # Detect type
                index_of_max = self.door_movement_array.index(max(self.door_movement_array))

                if index_of_max > len(self.door_movement_array) / 2:
                    self.door_movement_detect_type.append("in")
                else:
                    self.door_movement_detect_type.append("out")

                logging.info("Found new person")
                self.door_movement_array = []
                self.door_movement_detect_time.append(new_data['time'])
                self.door_movement_detect_pos.append(new_dist_raw)
                self.mov_detected = False

        for item in list(self.lr):
            if item.getRegion()[0] < self.graphs["dist_raw"]["plots"][new_data["id"]]["x"][0]:
                self.graphs["dist_raw"]["widget"].removeItem(item)
                self.lr.remove(item)
            else:
                break
