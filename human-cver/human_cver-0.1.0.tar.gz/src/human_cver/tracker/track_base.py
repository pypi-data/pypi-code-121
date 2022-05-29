class BaseTrackObj(object):
    def __init__(self) -> None:
        self._name = None
        self._time = None
        self._abs_time = None
        self._step = None

    def set_name(self, name):
        self._name = name

    def data(self):
        raise NotImplementedError("not implemented!")

    def show(self):
        raise NotImplementedError("not implemented!")
