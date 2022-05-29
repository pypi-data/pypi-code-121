from .track_base import BaseTrackObj


class NumberTrackObj(BaseTrackObj):
    def __init__(self, number, name=None) -> None:
        super().__init__()

        self.number = number
        self.set_name(name)

    def data(self):
        return self.number

    def show(self):
        print(self.data())
