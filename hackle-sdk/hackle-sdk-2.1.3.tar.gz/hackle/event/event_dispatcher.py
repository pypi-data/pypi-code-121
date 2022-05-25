import json
import logging
from json import JSONEncoder

import requests
from requests import exceptions as request_exception

from hackle import version
from hackle.commons import enums


class EventEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Serializer(object):
    @staticmethod
    def serialize(obj):
        return json.dumps(obj, default=lambda o: o.__dict__.values()[0])


class EventDispatcher(object):
    def __init__(self):
        self.event_url = enums.Default.EVENT_URL

    def dispatch_event(self, sdk_key, event):
        request_headers = {enums.Default.SDK_KEY_HEADER: sdk_key,
                           enums.Default.SDK_NAME_HEADER: 'python-sdk',
                           enums.Default.SDK_VERSION_HEADER: version.__version__,
                           enums.Default.CONTENT_TYPE_HEADER: enums.Default.SDK_CONTENT_TYPE}

        try:
            requests.post(self.event_url, data=json.dumps(event, cls=EventEncoder), headers=request_headers,
                          timeout=enums.Default.REQUEST_TIMEOUT).raise_for_status()

        except request_exception.RequestException as error:
            logging.error('Dispatch event failed. Error: %s' % str(error))
