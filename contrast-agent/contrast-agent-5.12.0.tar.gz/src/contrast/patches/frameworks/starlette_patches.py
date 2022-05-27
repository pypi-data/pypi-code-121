# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import wrapt

import contrast
from contrast.agent.assess.policy.analysis import analyze
from contrast.agent.policy.loader import Policy
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch


STARLETTE_REQUESTS = "starlette.requests"
SESSION = "session"


class ContrastSessionDictProxy(wrapt.ObjectProxy):
    """
    Custom ObjectProxy we use to wrap dicts returned by starlette's request.session
    property. These proxied dicts have a trigger for trust-boundary-violation on
    __setitem__.
    """

    def __setitem__(self, key, value):
        result = None
        try:
            result = self.__wrapped__.__setitem__(key, value)
        finally:
            analyze_setitem(result, (self, key, value))

        return result


@fail_quietly("Failed to analyze session dict __setitem__")
def analyze_setitem(result, args):
    context = contrast.CS__CONTEXT_TRACKER.current()
    policy = Policy().policy_by_name.get("starlette.sessions.dict.__setitem__")
    analyze(context, policy, result, args, {})


def build_session_patch(orig_prop, patch_policy):
    def session_fget(*args, **kwargs):
        """
        Function used to replace fget for starlette's request.session property.
        This function returns proxied dictionaries - see ContrastSessionDictProxy.
        """
        session_dict = orig_prop.fget(*args, **kwargs)

        context = contrast.CS__CONTEXT_TRACKER.current()
        if context is None:
            return session_dict

        return ContrastSessionDictProxy(session_dict)

    return property(session_fget, orig_prop.fset, orig_prop.fdel)


def patch_starlette_session(requests_module):
    build_and_apply_patch(requests_module.Request, SESSION, build_session_patch)


def register_patches():
    wrapt.register_post_import_hook(patch_starlette_session, STARLETTE_REQUESTS)
