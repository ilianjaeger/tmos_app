import datetime


class GlobalInterface:
    """ Global Interface
    """

    def __init__(self):
        self._comm = None
        self._port = None
        self._timeout = 0.005

        self._time_zero = datetime.datetime.now()

    def get_port(self):
        return self._port

    def get_timeout(self):
        return self._timeout

    def get_instance(self):
        return self._comm

    def set_port(self, port):
        self._port = port

    def set_reference_time(self, t0):
        self._time_zero = t0

    def is_connected(self):
        pass

    def open_port(self, port):
        pass

    def close_port(self):
        pass

    def stop_device(self):
        pass

    def start_device(self):
        pass

    def process_data(self):
        pass

    def emit_error_signal(self):
        pass
