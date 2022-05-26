from abc import ABCMeta, abstractmethod


class Backend(metaclass=ABCMeta):
    @abstractmethod
    def bind(self, plan_id, user_id):
        raise NotImplementedError

    @abstractmethod
    def feature(self, feature_id, user_id):
        raise NotImplementedError

    @abstractmethod
    def increment(self, feature_id, user_id):
        raise NotImplementedError

    @abstractmethod
    def decrement(self, feature_id, user_id):
        raise NotImplementedError

    @abstractmethod
    def set(self, feature_id, user_id, value):
        raise NotImplementedError

    @abstractmethod
    def feature_matrix(self):
        raise NotImplementedError

    @abstractmethod
    def usage(self, user_id):
        raise NotImplementedError
