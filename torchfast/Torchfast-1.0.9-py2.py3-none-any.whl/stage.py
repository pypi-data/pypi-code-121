from enum import Flag
from torch import distributed

class Stage(Flag):
    TRAIN = 1
    VALIDATION = 2
    INFERENCE = 3


def all_reduce_mean(tensor) -> None:
    # inplace operation!
    world_size = distributed.get_world_size()
    distributed.all_reduce(tensor, op=distributed.ReduceOp.SUM)
    tensor /= world_size
