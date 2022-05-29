# embedded inmemory storage for kafka emulation

from collections import deque
from time import time


class KafkaMessage:
    def __init__(self, value, topic, partition=0, offset=0, timestamp=time(), key=b''):
        self._value = value
        self._key = key
        self._topic = topic
        self._error = None
        self._partition, self._offset, self._timestamp = partition, offset, timestamp

    def value(self):
        return self._value

    def key(self):
        return self._key

    def topic(self):
        return self._topic

    def timestamp(self):
        return self._timestamp

    def error(self):
        return self._error


class Store(object):
    def __init__(self):
        self.topics = {}

    def get_topic_lens(self):
        topic2len = {}
        full_len = 0

        for topic, deq in self.topics.items():
            topic_len = len(deq)
            if topic_len:
                topic2len[topic] = topic_len
                full_len += topic_len

        return full_len, topic2len

    def __read_queue(self, topic, limit=1000):
        msgs = []

        if topic not in self.topics:
            return msgs

        for k in range(limit):
            try:
                mes = self.topics[topic].pop()
                msgs.append(mes)
            except IndexError:
                break

        return msgs

    def reader_generator(self, topic, max_values=1000):
        while True:
            batch = self.__read_queue(topic, limit=max_values)
            if not batch:
                return
            yield batch

    def _produce_kaf_format(self, topic, mes):
        self.last_write_time = time()

        if topic not in self.topics:
            self.topics[topic] = deque()
        self.topics[topic].appendleft(mes)

    def produce(self, topic, value, key=b''):
        mes = KafkaMessage(value=value,
                           topic=topic,
                           partition=0, offset=0, timestamp=time(),
                           key=key)

        self._produce_kaf_format(topic, mes)
