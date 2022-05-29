import pickle
from typing import List

from .track_base import BaseTrackObj


def load_trackfile(trackfile) -> List[BaseTrackObj]:
    obj_list = []
    with open(trackfile, "rb") as fr:
        while True:
            try:
                obj = pickle.load(fr)
                obj_list.append(obj)
            except EOFError:
                break
    return obj_list


def analyzer(trackfile):
    obj_list = load_trackfile(trackfile)
    for obj in obj_list:
        obj.show()
