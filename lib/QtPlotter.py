import queue
import numpy as np
import logging

from PyQt5 import QtCore

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock

data_plot_queue = queue.Queue()

TMOS_DATA_BIT_POS = {
    'in_time': {"pos": 1, "title": "Local Time"},
    'dist_raw': {"pos": 2, "title": "Raw Value"},
    'temp': {"pos": 3, "title": "Temperature"},
    'dist_filt': {"pos": 4, "title": "Filtered value"},
    'vel': {"pos": 5, "title": "Velocity"},
    'bin_1': {"pos": 6, "title": "Presence bit"},
    'bin_2': {"pos": 7, "title": "Movement bit"}
}


class PeopleCounterPlotItem:
    def __init__(self, graph_widget, start_x, data_value):
        self.graph_widget = graph_widget

        self.start_x = start_x
        self.end_x = start_x

        self.max_data_x = start_x
        self.max_data_value = data_value

        # Create linear region
        self.linear_region = pg.LinearRegionItem([start_x, start_x], movable=False)
        self.arrow_item = None
        self.text_item = None

        # Add linear region to plot
        self.graph_widget.addItem(self.linear_region)

    def remove_item(self):
        # Remove all items
        self.graph_widget.removeItem(self.linear_region)
        self.graph_widget.removeItem(self.arrow_item)
        self.graph_widget.removeItem(self.text_item)

    def update_linear_region(self, pos_x, data_value):
        self.end_x = pos_x
        self.linear_region.setRegion([self.start_x, pos_x])

        if data_value > self.max_data_value:
            self.max_data_value = data_value
            self.max_data_x = pos_x

    def finalize_reading(self, x_pos, data_value):
        self.update_linear_region(x_pos, data_value)

        self.arrow_item = pg.ArrowItem(tipAngle=30, baseAngle=-30, headLen=40, tailLen=None, angle=-90, pen=None, brush="y")
        self.arrow_item.setPos(self.max_data_x, self.max_data_value)

        went_out = self.max_data_x < (self.end_x + self.start_x) / 2
        print(went_out, self.start_x, self.end_x, self.max_data_x)

        self.text_item = pg.TextItem(
            html='<span style="color:{};font-size:30px;">{}</span>'.format(("green", "red")[went_out], ("IN", "OUT")[went_out]),
            anchor=(0.5, 2.0), fill=(0, 0, 255, 0))
        self.text_item.setPos(self.max_data_x, self.max_data_value)

        self.graph_widget.addItem(self.text_item)
        self.graph_widget.addItem(self.arrow_item)

    def get_initial_pos(self):
        return self.start_x


class PeopleCounter:
    def __init__(self, data_graph):
        self.data_graph = data_graph

        # Array with dicts containing all plot items
        self.plot_data_items = []
        self.mov_thresh = 2000
        self.mov_detected = False

    def update(self, new_data):
        new_dist_raw = float(new_data['data'].split(',')[TMOS_DATA_BIT_POS["dist_raw"]["pos"]])
        if new_dist_raw > self.mov_thresh:
            if not self.mov_detected:
                self._create_plot_item(new_data["time"], new_dist_raw)

            self.mov_detected = True
            self._update_current_plot_item(new_data["time"], new_dist_raw)

        else:
            if self.mov_detected:
                self._finalize_current_plot_item(new_data["time"], new_dist_raw)

                logging.info("Found new person")
                self.mov_detected = False

        self._update_plot_items(new_data["id"])

    def _create_plot_item(self, x_pos, data_value):
        new_plot_item = PeopleCounterPlotItem(self.data_graph["widget"], x_pos, data_value)
        self.plot_data_items.append(new_plot_item)

    def _update_current_plot_item(self, x_pos, data_value):
        self.plot_data_items[-1].update_linear_region(x_pos, data_value)

    def _finalize_current_plot_item(self, x_pos, data_value):
        self.plot_data_items[-1].finalize_reading(x_pos, data_value)

    def _update_plot_items(self, sensor_id):
        for item in list(self.plot_data_items):
            if item.get_initial_pos() < self.data_graph["plots"][sensor_id]["x"][0]:
                item.remove_item()
                self.plot_data_items.remove(item)
            else:
                break


class QtLivePlotter(Dock):

    NUM_DATA_POINTS = 200

    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        # Graphs
        # self.graphs = {"dist_raw": dict(), "dist_filt": dict(), "vel": dict(), "temp": dict()}
        self.graphs = {"dist_raw": dict()}
        for gr in self.graphs:
            self.graphs[gr] = dict({"widget": pg.PlotWidget(title=TMOS_DATA_BIT_POS[gr]["title"]), "plots": dict()})
            self.graphs[gr]["widget"].getPlotItem().addLegend()
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="left", text=TMOS_DATA_BIT_POS[gr]["title"])
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="bottom", text="time")

            self.addWidget(self.graphs[gr]["widget"])

        self.people_counter = PeopleCounter(self.graphs["dist_raw"])

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

                for graph_id, obj in self.graphs.items():
                    # If plot does not exist, create it
                    if record["id"] not in self.graphs[graph_id]["plots"]:
                        self.create_graph(graph_id, record["id"])

                    self.update_graph(graph_id, self.graphs[graph_id]["plots"][record["id"]], record)

                    if graph_id == "dist_raw":
                        self.people_counter.update(record)
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

    @staticmethod
    def update_graph(graph_id, cur_plot, new_data):
        cur_plot["x"][:-1] = cur_plot["x"][1:]
        cur_plot["x"][-1] = new_data['time']
        cur_plot["y"][:-1] = cur_plot["y"][1:]
        cur_plot["y"][-1] = float(new_data['data'].split(',')[TMOS_DATA_BIT_POS[graph_id]["pos"]])
        cur_plot["line"].setData(cur_plot["x"], cur_plot["y"])
