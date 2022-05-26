"""Module to create sinergym environments. """

import gym
import sinergym  # pylint: disable=unused-import


def create_env(env_config: dict = None) -> gym.Env:
    """Create sinergym environment.

    Args:
        env_config (dict, optional): configuration kwargs for sinergym. Currently,
            there is only a single key in this dictionary, "name". This sets
            the name of the environment. Defaults to None.

    Returns:
        gym.Env: a configured gym environment.
    """
    env = gym.make(env_config["name"])
    return env
