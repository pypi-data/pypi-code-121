# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

from functools import lru_cache

from django.conf import settings


CONFIG_DEFAULTS = {
    'FLAMEGRAPH_SCRIPT_PATH': None,
    'FLAMEGRAPH_SCRIPT_EXTRA_ARGS': [],
    'SAMPLE_INTERVAL': 0.001,
}


@lru_cache()
def get_config():
    return {**CONFIG_DEFAULTS, **getattr(settings, 'PYFLAME_CONFIG', {})}
