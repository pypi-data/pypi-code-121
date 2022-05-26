import numpy as np
from . import Algorithm
from collections import deque


class MovingAverage(Algorithm):
    """An example implementation of class :py:class:`Algorithm`. This algorithm implements the Dual Moving Average Crossover strategy. See https://faculty.fuqua.duke.edu/~charvey/Teaching/BA453_2002/CCAM/CCAM.htm for more information.
    """
    def __init__(self, price_feature_pos, short_window=30, long_window=180,
                 initial_cap=100):
        # simplified version of moving average. buy all cap / sell all cap at once.
        self._wallet_usd = np.float32(initial_cap)
        self._wallet_crypto = np.float32(0)
        self._price_feature_pos = price_feature_pos

        # moving average things
        self._short_window = deque([np.float32(0)], maxlen=short_window)
        self._long_window = deque([np.float32(0)], maxlen=long_window)
        self._short_avg_history = [0]
        self._long_avg_history = [0]

    def _update_windows(self, price):
        self._short_window.append(np.float32(price))
        self._long_window.append(np.float32(price))
        self._short_avg_history.append(self._get_short_avg())
        self._long_avg_history.append(self._get_long_avg())

    def _get_long_avg(self):
        return np.array(self._long_window, dtype=np.float32).mean()

    def _get_short_avg(self):
        return np.array(self._short_window, dtype=np.float32).mean()

    def _generate_signal(self):
        cur_short = self._short_avg_history[-1]
        prev_short = self._short_avg_history[-2]
        cur_long = self._long_avg_history[-1]
        prev_long = self._long_avg_history[-2]
        is_cross = (cur_short - cur_long) * (prev_short - prev_long) < 0
        if is_cross and cur_short > cur_long:
            return 0
        elif is_cross and cur_long > cur_short:
            return 1
        else:
            return 2

    def take_action(self, observation, info=None):
        price = np.float32(observation['features'][self._price_feature_pos])
        self._update_windows(price=price)
        signal = self._generate_signal()
        crypto_to_buy = self._wallet_usd / price
        crypto_to_sell = self._wallet_crypto

        action = None
        if signal == 0:  # buy
            action = dict(
                signal=signal,
                value=np.array([crypto_to_buy], dtype=np.float32)
            )
            self._wallet_crypto += crypto_to_buy
            self._wallet_usd = 0
        if signal == 1:  # sell
            action = dict(
                signal=signal,
                value=np.array([crypto_to_sell], dtype=np.float32)
            )
            self._wallet_usd += self._wallet_crypto * price
            self._wallet_crypto = 0
        if signal == 2:  # hold
            action = dict(
                signal=signal,
                value=np.array([0], dtype=np.float32)
            )

        return action
