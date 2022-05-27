# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class WsgiComplianceException(Exception):
    """
    Used to indicate that an application or server does not comply
    with the WSGI specification. See https://www.python.org/dev/peps/pep-0333
    """

    pass
