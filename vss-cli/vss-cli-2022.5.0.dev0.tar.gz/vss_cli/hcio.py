import logging

import requests

from vss_cli.utils.emoji import EMOJI_UNICODE
from vss_cli.vssconst import HEALTHCHECK_IO

hc_io_badge = f"https://healthchecks.io/badge/{HEALTHCHECK_IO}"

_LOGGING = logging.getLogger(__name__)


def check_status():
    status = 'unknown'
    icon = EMOJI_UNICODE.get(':question_mark:')
    try:
        r = requests.get(hc_io_badge)
        _status = r.json()
        status = _status.get('status')
        if status in ['up']:
            status = 'operational'
            icon = EMOJI_UNICODE.get(':white_heavy_check_mark:')
        elif status in ['down']:
            icon = EMOJI_UNICODE.get(':cross_mark:')
    except Exception as ex:
        _LOGGING.warning(f'healthchecks.io lookup failed: {ex}')
    return {"name": "ITS Private Cloud API", "status": status, "icon": icon}
