from .track_base import BaseTrackObj


class NumpyTrackObj(BaseTrackObj):
    def __init__(self, number, name=None) -> None:
        super().__init__()

        self.number = number
        self.set_name(name)

    def data(self):
        return self.number

    def show(self):
        print(self.data())
