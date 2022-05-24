import threading


class FlushMessagesEvent(object):
    def __init__(self):
        self.event = threading.Event()
