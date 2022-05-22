from ..iter import *
from ..symbols import name


def quickcardio(nam="cardio"):
    for d,x,tx,ty in pipeline(name==nam, shuffle, split, normalize("zscore")):
        return x,tx,ty



