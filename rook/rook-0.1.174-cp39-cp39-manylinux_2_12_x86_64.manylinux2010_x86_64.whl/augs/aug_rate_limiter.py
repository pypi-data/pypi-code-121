from threading import Lock


class AugRateLimiter(object):
    # enable this flag in unittests only to expose some methods that are needed for tests
    ENABLE_SPECIAL_METHODS_FOR_TESTS = False

    def __init__(self, quota, window_size):
        self._quota = quota
        self._window_size = window_size
        self._lock = Lock()

        self._windows = {}

    def allow(self, now_ns):
        if self._quota is None:
            return '0'

        with self._lock:
            self._cleanup(now_ns)

            current_window_key = now_ns // self._window_size * self._window_size
            prev_window_key = current_window_key - self._window_size

            current_window_usage = self._windows.setdefault(current_window_key, 0)
            prev_window_usage = self._windows.get(prev_window_key)

            if prev_window_usage is None:
                if current_window_usage > self._quota:
                    return None
            else:
                prev_weight = 1 - (now_ns - current_window_key) / float(self._window_size)
                weighted_usage = (prev_window_usage * prev_weight) + current_window_usage

                if weighted_usage > self._quota:
                    return None

            return current_window_key

    def record(self, key, duration_ns):
        if self._quota is None:
            return

        with self._lock:
            total_duration = self._windows.get(key)  # windows might be cleared while aug is running (unlikely)

            if total_duration is not None:
                self._windows[key] += duration_ns

    def _cleanup(self, now):
        if len(self._windows) > 10:
            self._windows = {k: v for k, v in self._windows.items() if k > now - self._window_size * 5}

    def get_windows_for_tests_only(self):
        if not AugRateLimiter.ENABLE_SPECIAL_METHODS_FOR_TESTS:
            raise NotImplementedError('This method should be used only in unit tests!!!!')
        return self._windows
