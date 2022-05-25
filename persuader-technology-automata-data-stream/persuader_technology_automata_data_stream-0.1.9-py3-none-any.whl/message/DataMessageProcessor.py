class DataMessageProcessor:

    def __init__(self):
        self.listen_stream = None
        self.listen_data = None

    def set_listen_stream(self, stream):
        self.listen_stream = stream

    def get_listen_stream(self):
        return self.listen_stream

    def set_listen_data(self, data):
        self.listen_data = data

    def get_listen_data(self):
        return self.listen_data

    def process_message(self, message):
        pass
