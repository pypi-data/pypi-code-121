import sys
import logging
from datetime import datetime
from datetime import date


def get_log(name):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    return logging.getLogger(name)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


