import threading


class ExceptionCapturingLocationService(object):
    NAME = "exception_capturing"

    def __init__(self):
        self._lock = threading.RLock()
        self._aug_ids = []

    def get_ids(self):
        return self._aug_ids

    def add_exception_capturing_aug(self, aug):
        with self._lock:
            self._aug_ids.append(aug.aug_id)
            aug.set_active()

    def remove_aug(self, aug_id):
        with self._lock:
            try:
                self._aug_ids.remove(aug_id)
            except ValueError: # if value is not the array then there's nothing to do here
                pass

    def clear_augs(self):
        with self._lock:
            del self._aug_ids[:]

    def close(self):
        self.clear_augs()

    def pre_fork(self):
        if self._lock:
            self._lock.acquire()

    def post_fork(self):
        if self._lock:
            self._lock.release()

    def activation_status(self):
        return len(self._aug_ids) > 0
