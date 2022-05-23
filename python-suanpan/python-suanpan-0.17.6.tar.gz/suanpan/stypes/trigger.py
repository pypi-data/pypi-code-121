import abc
import typing as t

if t.TYPE_CHECKING:
    from suanpan.stypes.app import AppT


class IntervalT(object):
    @abc.abstractmethod
    def __init__(self, seconds, pre=False):
        """init interval instance

        Arguments:
            seconds: the seconds this interval wait
            pre: if True, wait before doing the trigger function
                else wait after doing the trigger function

        Example:
            interval = Interval(3600)
        """
        ...


class TriggerT(AppT):
    @abc.abstractmethod
    def loop(self, interval: IntervalT):
        """run the trigger every intervals"""
        ...
