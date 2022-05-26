"""
it4ifree portal clients jsonlib
"""

import sys
import urllib2
import simplejson as json

from .logger import LOGGER

def jsondata(remote, data=None):
    """
    Return json data
    """
    try:
        req = urllib2.Request(remote)
        req.add_header('Content-Type', 'application/json')
        if data is None:
            response = urllib2.urlopen(req)
        else:
            response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        LOGGER.error("Sorry, there was a problem accessing the service. Please try again later.")
        sys.exit(1)

    try:
        jsonout_raw = response.read()
    except BaseException:
        LOGGER.error("Sorry, there was a problem accessing the service. Please try again later.")
        sys.exit(1)

    return json.loads(jsonout_raw)
