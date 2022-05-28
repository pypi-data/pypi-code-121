import time

class Timer:
    def __init__(self):
        self.begin_time = time.time()

    def reset(self):
        self.begin_time = time.time()

    def get_time(self):
        return time.time()-self.begin_time
        