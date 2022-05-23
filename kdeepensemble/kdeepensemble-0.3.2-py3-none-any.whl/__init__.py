import tensorflow as tf
from .version import __version__
from .kdens import DeepEnsemble, resample, map_tile, neg_ll, map_batch_reshape

custom_things = [DeepEnsemble, neg_ll]
custom_objects = {o.__name__: o for o in custom_things}
del custom_things
