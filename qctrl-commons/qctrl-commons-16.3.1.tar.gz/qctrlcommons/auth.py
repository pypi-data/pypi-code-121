# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Q-CTRL API authentication module.
"""
from typing import Tuple

from aiohttp.client_reqrep import helpers as aio_helpers
from requests.auth import AuthBase


class ClientAuthBase(aio_helpers.BasicAuth, AuthBase):
    """Base class that defines the signature for other authentication classes
    to be used either synchronously with `requests` or asynchronously with
    `aiohttp`.

    Inherited classes must define `encode(self)` method that returns the
    `Authorization` header value.
    """

    def __new__(  # pylint: disable=signature-differs,unused-argument
        cls, *args
    ) -> Tuple:
        """Overrides `__new__()` from `aiohttp` BasicAuth to allow other
        authentication methods.

        Parameters
        ----------
        *args
            argument list for instantiating ClientAuthBase.

        Returns
        -------
        Tuple
            a ClientAuthBase object accept new authentication methods.
        """
        return tuple.__new__(cls, args)

    def __call__(self, r):
        r.headers["Authorization"] = self.encode()
        return r

    def encode(self) -> str:
        """Method that returns the value to be sent on `Authorization`
        header."""
        raise NotImplementedError()

    def __repr__(self):
        return AuthBase.__repr__(self)
