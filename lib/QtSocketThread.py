from lib.socket_interface import SocketInterface
from lib.template.GlobalThread import QtGlobalWorker


class QtSocketWorker(QtGlobalWorker):
    """ Main socket worker
    """

    def __init__(self, interval):
        super().__init__(interval)

        self._interface = SocketInterface()
