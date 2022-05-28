"""Uniform agent.
"""

import numpy as np


class UniformAgent(object):
    """An agent that selects actions uniformly at random.

    :attr _num_actions: the number of actions available to the agent in each state.
    """

    def __init__(self, num_actions: int) -> None:
        """Initialise the object.

        :param num_actions: number of actions available to the agent in each state.
        """
        self._num_actions = num_actions

    def predict(self) -> int:
        """Select an action uniformly at random.

        :return: action chosen by the agent.
        """
        return np.random.randint(0, self._num_actions)
