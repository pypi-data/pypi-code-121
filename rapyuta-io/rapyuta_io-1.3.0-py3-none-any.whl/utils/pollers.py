from abc import abstractmethod
import time

from rapyuta_io.utils import RetriesExhausted


class RefreshPollerMixin(object):
    """
    Mixin to be used for API resource objects that have `refresh()` method (see utils.partials.PartialMixin.refresh()).
    This refresh method is used to update object after polling the API resource.
    """

    @abstractmethod
    def refresh(self):
        # See utils.partials.PartialMixin.refresh() for documentation
        raise NotImplementedError

    @abstractmethod
    def is_ready(self):
        """
        Is called after the `refresh()` call. Implementation should return False if final state (Success/Failure) has
        not been achieved yet. Else, either return True to indicate Success, or raise an Exception to indicate Failure.
        """
        raise NotImplementedError

    def poll_till_ready(self, retry_count, sleep_interval):
        """
        :param retry_count: Number of retries.
        :type retry_count: int
        :param sleep_interval: Sleep seconds between retries.
        :type sleep_interval: int

        :raises: :py:class:`RetriesExhausted`: If the number of polling retries exhausted before the object was ready.
        """
        for _ in range(retry_count):
            self.refresh()
            if self.is_ready():
                return
            time.sleep(sleep_interval)
        msg = 'Retries exhausted: Tried {} times with {}s interval.'.format(retry_count, sleep_interval)
        raise RetriesExhausted(msg)
