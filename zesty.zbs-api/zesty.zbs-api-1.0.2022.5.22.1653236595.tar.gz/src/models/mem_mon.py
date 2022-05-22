

class MemoryMonitor:
    total = None
    available = None
    used = None
    free = None
    percent = None

    def __init__(self, mem_mon_data):
        self.total = mem_mon_data.get('total')
        self.available = mem_mon_data.get('available')
        self.used = mem_mon_data.get('used')
        self.free = mem_mon_data.get('free')
        self.percent = mem_mon_data.get('percent')

    def to_dict(self):
        return self.__dict__
