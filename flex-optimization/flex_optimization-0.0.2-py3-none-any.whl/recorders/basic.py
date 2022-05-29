from flex_optimization.core.recorder import Recorder


class RecorderBasic(Recorder):
    def __init__(self, problem=None, method=None):
        super().__init__(problem, method)

    def record(self, type_: int, *args, **kwargs):
        if type_ == 4:
            pass
