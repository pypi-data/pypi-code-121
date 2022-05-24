class MSGBase:
    def __init__(self, *args, **kwargs):
        self.get_pypers_queue()

    def get_pypers_queue(self):
        raise NotImplementedError()
