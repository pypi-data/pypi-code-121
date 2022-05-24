from queue import Queue


class BaseQueue(Queue):

    def __init__(self, num):
        super().__init__(num)

    def set_size(self, num):
        super().__init__(num)

    def get_size(self):
        return self.qsize()

    def is_empty(self):
        return self.empty()

    # def put(self, item, block=True, timeout=None):
    #     self.put(item, block, timeout)
    #
    # def get(self, block=True, timeout=None):
    #     self.get(block, timeout)
