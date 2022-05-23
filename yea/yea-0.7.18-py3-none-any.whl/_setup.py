import importlib
import multiprocessing as mp
import os
from typing import Dict


def _setup_params() -> Dict[str, str]:
    env_names = os.environ.get("YEA_PARAM_NAMES")
    env_values = os.environ.get("YEA_PARAM_VALUES")
    if env_names is None or env_values is None:
        return dict()
    names = env_names.split(",")
    values = env_values.split(",")
    params = dict(zip(names, values))
    return params


def setup_mp(params: Dict[str, str]) -> None:
    start_method = params.get(":yea:start_method")
    if not start_method:
        return
    print(f"INFO: start_method= {start_method}")
    mp.set_start_method(start_method)
    # TODO: check mp setup?


def setup_plugins() -> None:
    env_plugins = os.environ.get("YEA_PLUGINS")
    if env_plugins is None:
        return
    plugins = env_plugins.split(",")
    for plug in plugins:
        mod_name = f"yea_{plug}"
        mod = importlib.import_module(mod_name)
        mod_setup = getattr(mod, "setup", None)
        if not mod_setup:
            continue
        mod_setup()


def setup() -> None:
    p = _setup_params()
    setup_mp(params=p)
    setup_plugins()
