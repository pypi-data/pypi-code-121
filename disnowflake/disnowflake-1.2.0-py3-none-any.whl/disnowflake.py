from datetime import datetime


class DisnowFlake:
    def __init__(self, id: int):
        self.stamp_bin = bin(id >> 22)
        self.stamp_dec = int(self.stamp_bin, 0)
        self.stamp_to_unix = (self.stamp_dec + 1420070400000) / 1000
        self.timestamp = datetime.fromtimestamp(self.stamp_to_unix)

    @property
    def year(self) -> int:
        return self.timestamp.year

    @property
    def month(self) -> int:
        return self.timestamp.month

    @property
    def day(self) -> int:
        return self.timestamp.day

    @property
    def hour(self) -> int:
        return self.timestamp.hour

    @property
    def minute(self) -> int:
        return self.timestamp.minute

    @property
    def second(self) -> int:
        return self.timestamp.second

    @property
    def microsecond(self) -> int:
        return self.timestamp.microsecond
