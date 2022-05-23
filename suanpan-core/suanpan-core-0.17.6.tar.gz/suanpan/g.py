# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.objects import Context
from suanpan.utils import env

g = Context(
    # App
    debug=env.lazyget("SP_DEBUG", type=env.Bool, default=False),
    port=env.lazyget("SP_PSTREAM_PORT", type=env.Int, default=8888),
    timezone=env.lazyget("SP_TIMEZONE", default="UTC"),
    appType=env.lazyget("SP_APP_TYPE", required=True),
    appParams=env.lazyget("SP_PARAM", default=""),
    nodeInfo=env.lazyget("SP_NODE_INFO", default=""),
    userId=env.lazyget("SP_USER_ID", required=True),
    appId=env.lazyget("SP_APP_ID", required=True),
    nodeId=env.lazyget("SP_NODE_ID", required=True),
    nodeGroup=env.lazyget("SP_NODE_GROUP", default="default"),
    # Api
    host=env.lazyget("SP_HOST", required=True),
    hostTls=env.lazyget("SP_HOST_TLS", type=env.Bool, default=False),
    apiHost=env.lazyget("SP_API_HOST", required=True),
    apiHostTls=env.lazyget("SP_API_HOST_TLS", type=env.Bool, default=False),
    affinity=env.lazyget("SP_AFFINITY"),
    accessKey=env.lazyget("SP_ACCESS_KEY", required=True),
    accessSecret=env.lazyget("SP_ACCESS_SECRET", required=True),
    userIdHeaderField=env.lazyget("SP_USER_ID_HEADER_FIELD", default="x-sp-user-id"),
    userSignatureHeaderField=env.lazyget(
        "SP_USER_SIGNATURE_HEADER_FIELD", default="x-sp-signature"
    ),
    userSignVersionHeaderField=env.lazyget(
        "SP_USER_SIGN_VERSION_HEADER_FIELD", default="x-sp-sign-version"
    ),
    # Screenshots
    screenshotsType=env.lazyget("SP_SCREENSHOTS_TYPE", default="index"),
    screenshotsPattern=env.lazyget("SP_SCREENSHOTS_PATTERN"),
    screenshotsStorageKey=env.lazyget("SP_SCREENSHOTS_STORAGE_KEY"),
    screenshotsThumbnailStorageKey=env.lazyget("SP_SCREENSHOTS_THUMBNAIL_STORAGE_KEY"),
    # Logkit
    logkitUri=env.lazyget("SP_LOGKIT_URI", default=""),
    logkitNamespace=env.lazyget("SP_LOGKIT_NAMESPACE", default="/logkit"),
    logkitPath=env.lazyget("SP_LOGKIT_PATH", default=""),
    logkitEventsAppend=env.lazyget("SP_LOGKIT_EVENTS_APPEND", default="append"),
    logkitLogsLevel=env.lazyget("SP_LOGKIT_LOGS_LEVEL", default="warning"),
    # terminate stream
    termPort=env.lazyget("SP_TERM_PORT", type=env.Int, default=8002),
    currentOS=env.lazyget("SP_OS", default="kubernetes"),
    desktopHome=env.lazyget("SP_DESKTOP_HOME", default=""),
    backendPort=env.lazyget("SP_PORT", type=env.Int, default=7000),
    portStart=env.lazyget("SP_PORT_START", type=env.Int, default=10000),
    portEnd=env.lazyget("SP_PORT_END", type=env.Int, default=20000),
    # service disable
    serviceSioDisable=env.lazyget("SP_SERVICE_SIO_DISABLE", type=env.Bool, default=False),
    serviceHttpDisable=env.lazyget("SP_SERVICE_HTTP_DISABLE", type=env.Bool, default=False),
)
