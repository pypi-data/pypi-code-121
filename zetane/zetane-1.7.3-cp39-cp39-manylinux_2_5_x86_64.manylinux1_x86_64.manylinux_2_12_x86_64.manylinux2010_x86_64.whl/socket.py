

class NoSocket:
    def __init__(self):
        pass


    def add_to_q(self, item, debug):
        return self


    def connect(self):
        return self


    def disconnect(self):
        return self


    def remote(self):
        return self


class Socket:
    def __init__(self, context, retry_connection=True, timeout=10, max_retries=10, retry_timeout=5, analytics=None):
        pass


    def add_to_q(self, item, debug):
        """ Queue the Protobuf object to send to Zetane

        :param item: Protobuf object to be sent to Zetane
        :param debug: Flag to determine if we're running in Debug mode
        :return: The Zobj proto object received from Zetane as an Ack, if any, else None
        """
        return self


    def set_debugger(self, item):
        return self


    def retry(self):
        return self


    def dial(self):
        return self


    def connect(self):
        return self


    def disconnect(self):
        return self


    def remote(self):
        return self
