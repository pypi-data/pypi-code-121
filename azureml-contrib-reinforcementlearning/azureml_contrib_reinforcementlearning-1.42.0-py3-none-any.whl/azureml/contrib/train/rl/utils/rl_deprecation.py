# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Reinforcement Learning Service Deprecation warning utilities"""

from functools import wraps
import logging
import types

RL_DECOMMISSIONING_DOC_COMMENT = """DEPRECATED: The ReinforcementLearningEstimator is being
decommissioned. See https://aka.ms/rldeprecation for more information and timelines."""

_warned = set()
_warning_logger = logging.getLogger(__name__)


def warn_rl_is_deprecated(target):
    """ Helper decorator to emit warning about Reinforcement Learning Service Deprecation."""
    if isinstance(target, (types.FunctionType, types.MethodType)):
        # Wrap functions, so deprecation warning is printed when function is called
        target_key = target.__module__ + "." + target.__qualname__

        @wraps(target)
        def wrapper(*args, **kwargs):
            global _warned
            if target_key not in _warned:
                _warned.add(target_key)
                _warning_logger.warning(RL_DECOMMISSIONING_DOC_COMMENT)

            result = target(*args, **kwargs)
            return result
        return wrapper
    else:
        # For other objects, print deprecation warning right away
        target_key = target.__module__ + "." + target.__name__
        global _warned
        if target_key not in _warned:
            _warned.add(target_key)
            _warning_logger.warning(RL_DECOMMISSIONING_DOC_COMMENT)
        return target
