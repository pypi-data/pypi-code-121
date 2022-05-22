from collections import deque

DEFAULT_STICKINESS = 20


class SignalSmoother:
    def __init__(self, initial_state: int, stickiness=DEFAULT_STICKINESS):
        self._prev_inputs = deque(maxlen=stickiness + 1)
        self._prev_output = initial_state
        self._initial_state = initial_state

    def __call__(self, level: int):
        self._prev_inputs.append(level)
        ret_value = max(self._prev_inputs)
        if ret_value != self._prev_output:
            self._prev_output = ret_value
            return ret_value
        return None

    def reset(self):
        self._prev_inputs = deque(maxlen=self._prev_inputs.maxlen)
        self._prev_output = self._initial_state
