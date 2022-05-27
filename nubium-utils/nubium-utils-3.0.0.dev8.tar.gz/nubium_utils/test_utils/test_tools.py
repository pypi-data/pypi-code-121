class MockMessage:
    def __init__(self, key=None, value=None, headers=None, topic=None, timestamp=None, partition=None, offset=None, error=None):
        if not key:
            key = 'test_key'
        self.k = key
        if not value:
            value = 'test_value'
        self.v = value
        if not headers:
            headers = {'test_header_key': 'test_header_value'}
        self.h = headers
        if not topic:
            topic = 'test_topic'
        self.t = topic
        if not timestamp:
            timestamp = ('timestamp', 1642741200000) # Jan 21 2022 00:00:00.000 UTC
        self.time = timestamp
        if not partition:
            partition = 0
        self.p = partition
        if not offset:
            offset = 1
        self.of = offset
        self.e = error
    
    def key(self):
        return self.k

    def value(self):
        return self.v

    def headers(self):
        return self.h

    def topic(self):
        return self.t

    def timestamp(self):
        return self.time

    def partition(self):
        return self.p

    def offset(self):
        return self.of

    def error(self):
        return self.e
