from datetime import datetime
class Dummy:

    def __init__(self):
        self.__bias = 0
        self.__baseline = 1/3

    @property
    def bias(self):
        return self.__bias

    @property
    def baseline(self):
        return self.__baseline
    
    @baseline.setter
    def baseline(self, new_baseline):
        self.__baseline = new_baseline

    def scale(self, multiplier):
        return round(self.__baseline * multiplier + self.__bias, 3)

    def get_current_date_time(self):
        current_dt = datetime.now()
        return current_dt.strftime("%H:%M:%S %d/%m/%Y")