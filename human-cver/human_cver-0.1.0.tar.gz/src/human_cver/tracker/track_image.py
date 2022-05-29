from .track_base import BaseTrackObj
from ..vis.plot_kps import imshow


class ImageTrackObj(BaseTrackObj):
    def __init__(self, img, name=None) -> None:
        super().__init__()

        self.img = img
        self.set_name(name)

    def data(self):
        return self.img

    def show(self):
        imshow("img", self.img, wait_ms=0)
