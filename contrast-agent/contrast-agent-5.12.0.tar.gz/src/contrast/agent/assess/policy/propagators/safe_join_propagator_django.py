# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.policy.propagators import SafeJoinPropagator


class SafeJoinDjangoPropagator(SafeJoinPropagator):
    """
    Django's safe join propagation is the same as the base safe join except
    for one small detail which is the use of abspath. Django's safe_join
    function has a different behavior when relative paths are included in
    the directory.
    For example,

    ```
    >>> path = '/not/a/real/path/../path/test/'
    >>> file = 'base.html'
    >>>
    >>> flask_safe_join(path, file)
    '/not/a/real/path/../path/test/base.html'

    >>> django_safe_join(path, file)
    '/not/a/real/path/test/base.html'

    Since django simplifies the result, our propagation has to account for that
    when applying the SAFE_PATH tag to the result.
    ```
    """

    use_abspath = True
