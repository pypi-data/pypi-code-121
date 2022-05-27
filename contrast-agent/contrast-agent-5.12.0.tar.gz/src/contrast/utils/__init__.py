# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import pkg_resources
from contrast.agent import scope
from contrast.utils.namespace import Namespace  # noqa: provides a cleaner import
from contrast.utils.profiler import Profiler  # noqa: provides a cleaner import


def get_installed_distributions():
    """
    Wrapper used to get list of installed distributions in current active environment.
    """
    with scope.contrast_scope():
        return [
            d
            for d in pkg_resources.working_set  # pylint: # pylint: disable=not-an-iterable
        ]
