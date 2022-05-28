from datetime import datetime, timedelta

class Datetime:
    def __init__(self, *, timestamp=-1):
        if timestamp<0:
            self._dt = datetime.now()
        else:
            self._dt = datetime.fromtimestamp(timestamp)

    def __str__(self):
        return self._dt.strftime('%Y-%m-%d %H:%M:%S')

    def change(self, **kwargs):
        self._dt = self._dt + timedelta(**kwargs)
        return self

    def timestamp(self, timestamp=-1):
        if timestamp>0:
            self._dt = datetime.fromtimestamp(timestamp)
            return self
        else:
            return int(self._dt.timestamp())