import queue
import numpy as np
import logging

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock

data_plot_queue = queue.Queue()

WIDGET_COMMAND_TYPES = {
    "add": 1,
    "remove": 2,
    "region": 3,
    "create": 4,
    "update": 5
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


class PeopleCounterPlotItem:
    def __init__(self, graph_widget, command_signal, start_x, data_value):
        self.graph_widget = graph_widget
        self.command_signal = command_signal

        self.start_x = start_x
        self.end_x = start_x

        self.max_data_x = start_x
        self.max_data_value = data_value

        # Create linear region
        self.linear_region = pg.LinearRegionItem([start_x, start_x], movable=False)
        self.arrow_item = None
        self.text_item = None

        # Add linear region to plot
        self._send_command("add", self.linear_region)
        # self.graph_widget.addItem(self.linear_region)

    def remove_item(self):
        # Remove all items
        self._send_command('remove', self.linear_region)
        self._send_command('remove', self.arrow_item)
        self._send_command('remove', self.text_item)

        # self.graph_widget.removeItem(self.linear_region)
        # self.graph_widget.removeItem(self.arrow_item)
        # self.graph_widget.removeItem(self.text_item)

    def update_linear_region(self, pos_x, data_value):
        self.end_x = pos_x

        self._send_command("region", self.linear_region, self.start_x, pos_x)
        # self.linear_region.setRegion([self.start_x, pos_x])

        if data_value > self.max_data_value:
            self.max_data_value = data_value
            self.max_data_x = pos_x

    def finalize_reading(self, x_pos, data_value):
        self.update_linear_region(x_pos, data_value)

        self.arrow_item = pg.ArrowItem(tipAngle=30, baseAngle=-30, headLen=40, tailLen=None, angle=-90, pen=None,
                                       brush="y")
        self.arrow_item.setPos(self.max_data_x, self.max_data_value)

        went_out = self.max_data_x < (self.end_x + self.start_x) / 2

        self.text_item = pg.TextItem(
            html='<span style="color:{};font-size:30px;">{}</span>'.format(("green", "red")[went_out],
                                                                           ("IN", "OUT")[went_out]),
            anchor=(0.5, 2.0), fill=(0, 0, 255, 0))
        self.text_item.setPos(self.max_data_x, self.max_data_value)

        self._send_command("add", self.text_item)
        self._send_command("add", self.arrow_item)
        # self.graph_widget.addItem(self.text_item)
        # self.graph_widget.addItem(self.arrow_item)

    def get_initial_pos(self):
        return self.start_x

    def _send_command(self, vtype, vobject, vmin=0, vmax=0):
        self.command_signal.emit(WIDGET_COMMAND_TYPES[vtype], vobject, vmin, vmax)


class PeopleCounter:
    def __init__(self, data_graph, command_signal):
        self.data_graph = data_graph
        self.command_signal = command_signal

        # Array with dicts containing all plot items
        self.plot_data_items = []
        self.mov_thresh = 1000
        self.mov_detected = False

    def update(self):
        if self.data_graph["plot"]["y"][-1] > self.mov_thresh:
            if not self.mov_detected:
                self._create_plot_item()

            self.mov_detected = True
            self._update_current_plot_item()

        else:
            if self.mov_detected:
                self._finalize_current_plot_item()

                logging.info("Found new person")
                self.mov_detected = False

        self._update_plot_items()

    def _create_plot_item(self):
        new_plot_item = PeopleCounterPlotItem(self.data_graph["widget"], self.command_signal, self.data_graph["plot"]["x"][-1],
                                              self.data_graph["plot"]["y"][-1])
        self.plot_data_items.append(new_plot_item)

    def _update_current_plot_item(self):
        if len(self.plot_data_items) == 0:
            return

        self.plot_data_items[-1].update_linear_region(self.data_graph["plot"]["x"][-1], self.data_graph["plot"]["y"][-1])

    def _finalize_current_plot_item(self):
        self.plot_data_items[-1].finalize_reading(self.data_graph["plot"]["x"][-1], self.data_graph["plot"]["y"][-1])

    def _update_plot_items(self):
        for item in list(self.plot_data_items):
            if item.get_initial_pos() < self.data_graph["plot"]["x"][0]:
                item.remove_item()
                self.plot_data_items.remove(item)
            else:
                break


class QtLivePlotterWorker(QtCore.QObject):
    NUM_DATA_POINTS = 200

    def __init__(self, graphs, command_signal):
        super().__init__()

        self.graphs = graphs
        self.command_signal = command_signal
        self.people_counter = PeopleCounter(self.graphs["dist_raw"], command_signal)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot)

        self.timer.start()

    @pyqtSlot()
    def update_plot(self):
        global data_plot_queue

        try:
            # Get all queued points
            while not data_plot_queue.empty():
                record = data_plot_queue.get(block=False)

                for graph_id, obj in self.graphs.items():
                    # If plot does not exist, create it
                    if self.graphs[graph_id]["plot"] is None:
                        self.create_graph(graph_id)

                    self.update_graph(graph_id, record)

                    if graph_id == "dist_raw":
                        self.people_counter.update()
        except queue.Empty:
            pass

    def create_graph(self, graph_id):
        self.graphs[graph_id]["plot"] = dict()
        cur_plot = self.graphs[graph_id]["plot"]
        cur_plot["x"] = np.array(self.NUM_DATA_POINTS * [0])
        cur_plot["y"] = np.array(self.NUM_DATA_POINTS * [0])
        cur_plot["origin"] = 0.0

        # self.command_signal.emit(WIDGET_COMMAND_TYPES['create'], None, 0, 0)
        cur_plot["line"] = self.graphs[graph_id]["widget"].plot(cur_plot["x"], cur_plot["y"], name="TMOS Sensor")

    def update_graph(self, graph_id, new_data):
        cur_plot = self.graphs[graph_id]["plot"]
        cur_plot["x"][:-1] = cur_plot["x"][1:]
        cur_plot["x"][-1] = new_data['time']
        cur_plot["y"][:-1] = cur_plot["y"][1:]
        cur_plot["y"][-1] = float(new_data['data'].split(',')[TMOS_DATA_BIT_POS[graph_id]["pos"]]) - cur_plot["origin"]

        # self.command_signal.emit(WIDGET_COMMAND_TYPES['update'], None, 0, 0)
        cur_plot["line"].setData(cur_plot["x"], cur_plot["y"])


class QtLivePlotter(Dock):
    widget_command_signal = QtCore.pyqtSignal(int, object, int, int)

    def __init__(self, *args, **kwargs):
        super(QtLivePlotter, self).__init__(*args, **kwargs)

        # Buttons
        self.button_origin = QtWidgets.QPushButton("Set Origin")
        self.button_origin.pressed.connect(self.set_origin)
        self.addWidget(self.button_origin)

        # Graphs
        # self.graphs = {"dist_raw": dict(), "dist_filt": dict(), "vel": dict(), "temp": dict()}
        self.graphs = {"dist_raw": dict()}
        for gr in self.graphs:
            self.graphs[gr] = dict({"widget": pg.PlotWidget(title=TMOS_DATA_BIT_POS[gr]["title"]), "plot": None})
            self.graphs[gr]["widget"].getPlotItem().addLegend()
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="left", text=TMOS_DATA_BIT_POS[gr]["title"])
            self.graphs[gr]["widget"].getPlotItem().setLabel(axis="bottom", text="time")

            self.addWidget(self.graphs[gr]["widget"])

        self.worker = QtLivePlotterWorker(self.graphs, self.widget_command_signal)

        # The thread for the timer
        self.plotter_thread = QtCore.QThread(self)
        self.plotter_thread.setObjectName("Plotter")

        self.worker.moveToThread(self.plotter_thread)
        self.worker.timer.moveToThread(self.plotter_thread)

        self.widget_command_signal.connect(self.received_command)

        # Start the thread
        self.plotter_thread.start()

    @pyqtSlot(int, object, int, int)
    def received_command(self, command, vobj, vmin, vmax):
        widget = self.graphs["dist_raw"]
        if command == WIDGET_COMMAND_TYPES['add']:
            widget["widget"].addItem(vobj)
        elif command == WIDGET_COMMAND_TYPES['remove']:
            widget["widget"].removeItem(vobj)
        elif command == WIDGET_COMMAND_TYPES['region']:
            vobj.setRegion([vmin, vmax])
        # elif command == WIDGET_COMMAND_TYPES['create']:
        #     widget["plot"]["line"] = widget["widget"].plot(widget["plot"]["x"], widget["plot"]["y"],
        #                                                    pen="red",
        #                                                    name="TMOS Sensor")
        # elif command == WIDGET_COMMAND_TYPES['update']:
        #     widget["plot"]["line"].setData(widget["plot"]["x"], widget["plot"]["y"])

    @pyqtSlot()
    def set_origin(self):
        # print(self.graphs)

        if self.graphs["dist_raw"]["plot"] is None:
            return

        self.graphs["dist_raw"]["plot"]["origin"] = self.graphs["dist_raw"]["plot"]["y"][-1] + self.graphs["dist_raw"]["plot"]["origin"]
        self.graphs["dist_raw"]["plot"]["y"] = self.graphs["dist_raw"]["plot"]["y"] - self.graphs["dist_raw"]["plot"]["y"][-1]
