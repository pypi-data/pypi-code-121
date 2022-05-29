from datetime import datetime

class EventTimeGen(object):
    def __init__(self, mes_per_sec=100, num_of_mes=1000, last_dt=datetime.utcnow()):
        self.mes_per_sec = mes_per_sec
        self.index = num_of_mes
        self.num_of_mes = num_of_mes
        self.last_dt = last_dt
        self.last_ts = last_dt.timestamp()
        self.first_ts = self.last_ts - num_of_mes/mes_per_sec
        self.cur_ts = self.first_ts
    
    def __iter__(self):
        return self

    def __next__(self):
        self.index -= 1
        if self.index < 0:
            raise StopIteration
        self.cur_ts = self.cur_ts + 1/self.mes_per_sec
        return self.cur_ts