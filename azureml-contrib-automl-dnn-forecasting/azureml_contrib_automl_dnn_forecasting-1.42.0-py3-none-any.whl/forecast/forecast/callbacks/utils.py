import enum


class CallbackDistributedExecMode(enum.Enum):
    """In which process(es) should a callback run when training is distributed."""

    INCOMPATIBLE = enum.auto()  # callback is incompatible with distributed-training (the default)
    ALL = enum.auto()           # callback should run in all processes
    RANK_0 = enum.auto()        # callback should run in one process
    LOCAL_RANK_0 = enum.auto()  # callback should run in one process per node
