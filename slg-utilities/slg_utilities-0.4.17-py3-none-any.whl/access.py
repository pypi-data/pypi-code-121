import os
import re
import socket

import slg_utilities.config as cfg

HOSTNAME = socket.gethostname()

def is_production():
    """
    Returns boolean indicating whether host is production. The criteria in
    determining a host is production is that either the PRODUCTION environment
    variable is set to "1" or the word "production" is in the hostname with
    word boundaries on either side. e.g. the host "web-production.io"
    will match, but "reproduction" will not.
    """
    is_prod = cfg.get_runtime_config_value("PRODUCTION")
    if is_prod is None:
        is_prod = cfg.get_local_config_value("PRODUCTION")
    if is_prod is None:
        is_prod = bool(re.match(r".*\bproduction\b", HOSTNAME.lower()))
    # Normalize string value used in environment variables.
    if isinstance(is_prod, str) and is_prod.isdigit():
        is_prod = bool(int(is_prod))
    assert is_prod is not None
    return is_prod