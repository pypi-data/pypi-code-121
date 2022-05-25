import logging


class Default(object):
    WORKSPACE_URL = 'https://sdk.hackle.io/api/v2/workspaces'
    EVENT_URL = 'https://event.hackle.io/api/v2/events'
    SDK_KEY_HEADER = 'X-HACKLE-SDK-KEY'
    SDK_NAME_HEADER = 'X-HACKLE-SDK-NAME'
    SDK_VERSION_HEADER = 'X-HACKLE-SDK-VERSION'
    CONTENT_TYPE_HEADER = 'Content-Type'
    SDK_CONTENT_TYPE = 'application/json'
    DEFAULT_POLL_INTERVAL = 10
    DEFAULT_BLOCKING_TIMEOUT = 5
    REQUEST_TIMEOUT = 60


class HTTPVerbs(object):
    GET = 'GET'
    POST = 'POST'


class DecisionType(object):
    NATURAL = 'NATURAL'
    FORCED = 'FORCED'


class EventType(object):
    EXPOSURE = 'EXPOSURE'
    TRACK = 'TRACK'


class LogLevels(object):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
