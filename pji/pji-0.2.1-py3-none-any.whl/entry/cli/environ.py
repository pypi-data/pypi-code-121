from typing import List, Tuple, Mapping


def _split_environ(string: str) -> Tuple[str, str]:
    """
    split environment string into name and value
    :param string: original string
    :return: name, value
    """
    _name, _value = string.split('=', 2)
    return _name, _value


def _load_environ(envs: List[str]) -> Mapping[str, str]:
    """
    load environment variables
    :param envs: environments
    :return: env dict
    """
    return dict([_split_environ(env) for env in envs])
