from abc import ABC, abstractmethod


class Cache(ABC):
    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def set(self, key, value, ttl=None):
        raise NotImplementedError

    @abstractmethod
    def incr(self, key, amount=1):
        raise NotImplementedError
