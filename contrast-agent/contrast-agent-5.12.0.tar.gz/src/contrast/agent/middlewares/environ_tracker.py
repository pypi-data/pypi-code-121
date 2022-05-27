# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent import scope
from contrast.agent.assess.policy.analysis import skip_analysis
from contrast.agent.assess.policy.source_node import SourceNode
from contrast.agent.assess.policy.source_policy import cs__apply_source
from contrast.utils.assess.stream_utils import ContrastWsgiStreamProxy
from contrast.utils.decorators import fail_loudly, log_time

# a best effort at translating the types in this document:
# https://bitbucket.org/contrastsecurity/teamserver/src/
# 862d499227e8eac42b6eb7c6b03f10b7f1556218/teamserver-agent-messages/src/main/java/
# contrast/agent/messages/finding/trace/EventSourceTypeDTM.java#lines-8
ENVIRON_SOURCES = {
    "CONTENT_LENGTH": "HEADER",
    "CONTENT_TYPE": "HEADER",
    "PATH_INFO": "URI",
    "QUERY_STRING": "QUERYSTRING",
    "REMOTE_ADDR": "URI",
    "REMOTE_HOST": "URI",
    "REMOTE_USER": "URI",
    "SCRIPT_NAME": "HEADER",
    "SERVER_NAME": "HEADER",
    "SERVER_PORT": "HEADER",
    "SERVER_PROTOCOL": "HEADER",
    "webob.adhoc_attrs": "OTHER",
    "webob.url_encoding": "OTHER",
}

SOURCE_TAGS = {"HEADER": ["NO_NEWLINES"], "PARAMETER": ["CROSS_SITE"]}

SOURCE_DICT = {"module": "wsgi.environ", "instance_method": False, "target": "RETURN"}

WEBOB_KEYS_TO_DELETE = {
    "webob._parsed_query_vars",
    "webob._parsed_post_vars",
    "webob._body_file",
    "webob._parsed_cookies",
    "webob._cache_control",
}


@log_time("tracking cookie sources")
@fail_loudly("failed to track cookie sources")
def track_cookie_sources(framework, context, cookies):
    """track cookie keys and values"""
    if skip_analysis(context):
        return

    with scope.contrast_scope():
        _track_keys_and_values(
            framework, context, cookies, "COOKIE_KEY", "COOKIE", no_cross_site=True
        )


@log_time("tracking environ sources")
@fail_loudly("Failed to track environ sources")
def track_environ_sources(framework, context, environ):
    """
    This method will track necessary information in the environ

    For wsgi frameworks, this is the one true source of (stateless) untrusted data

    :param framework: current application's framework
    :param context: current request context
    :param environ: WSGI environ dict

    :return: None
    """
    if skip_analysis(context):
        return

    with scope.contrast_scope():
        for key, value in environ.items():
            _track_environ_item(framework, context, environ, key, value)

        _make_request_body_seekable(context.request)
        _track_wsgi_input(environ)
        _remove_webob_environ_vars(environ)


def _build_source_node(framework, method_name, source_type, no_cross_site=False):
    """
    Builds a new SourceNode based on the method name and source type

    Since cookie sources are not tagged with CROSS_SITE, callers must indicate whether
    the given source corresponds to a cookie or not.

    :param framework: str framework name for node
    :param method_name: name of the environ key
    :param source_type: type of the source
    :param no_cross_site: boolean indicating whether source tags include CROSS_SITE
    :return: SourceNode for cs__apply_source
    """

    source_dict = SOURCE_DICT.copy()

    tags = [] if no_cross_site else SOURCE_TAGS.get(source_type, ["CROSS_SITE"])

    source_dict["method_name"] = method_name
    source_dict["type"] = source_type
    source_dict["tags"] = tags

    node = SourceNode.from_dict(framework, source_dict)
    node.skip_stacktrace = True

    return node


def _track_keys_and_values(
    framework, context, mapping, key_type, value_type, no_cross_site=False
):
    for key, value in mapping.items():
        if key:
            key_node = _build_source_node(framework, key, key_type, no_cross_site)
            cs__apply_source(
                context, key_node, key, mapping, key, (), {}, source_name=key
            )

        if value:
            value_node = _build_source_node(framework, value, value_type, no_cross_site)
            cs__apply_source(
                context, value_node, value, mapping, value, (), {}, source_name=key
            )


def _track_environ_item(framework, context, environ, key, value):
    source_type = ""
    if key in ENVIRON_SOURCES:
        source_type = ENVIRON_SOURCES[key]

        node = _build_source_node(framework, key, source_type, False)

        cs__apply_source(context, node, value, environ, value, (), {}, source_name=key)
    elif key.startswith("HTTP_"):
        # This is to track custom headers we may not know about
        source_type = "COOKIE" if key == "HTTP_COOKIE" else "HEADER"

        node = _build_source_node(framework, key, source_type, "COOKIE" in key)

        cs__apply_source(context, node, value, environ, value, (), {}, source_name=key)

    # Track HTTP header keys as well
    if key.startswith("HTTP_") or source_type == "HEADER":
        no_cross_site = (source_type == "HEADER") or (key == "HTTP_COOKIE")

        key_node = _build_source_node(framework, key, "HEADER_KEY", no_cross_site)
        cs__apply_source(context, key_node, key, environ, key, (), {}, source_name=key)


def _make_request_body_seekable(request):
    """
    Before we track wsgi.input, we ask our externed webob to manipulate the input stream
    to make it seekable. There is no security risk here, because this simply involves
    reading raw bytes from wsgi.input into a seekable stream.

    We need to do this in case the application or any downstream middleware uses webob:
    1. Correctness: we would lose propagation from the original wsgi.input to the new
       stream if make_body_seekable is called for the first time after environ tracking.
    2. Performance: there's no need to propagate through make_body_seekable since we can
       just make the resulting seekable stream a source.
    Webob knows if this method has ever been called by storing the
    `webob.is_body_seekable` boolean directly in the environ dict.

    There is also no risk to correctness despite the fact that `make_body_seekable`
    resets the stream to position 0. This is because middlewares should not consume this
    stream without resetting it - so if we receive a partially-consumed stream, an
    earlier middleware is at fault.

    We should only track wsgi.input after calling this method.

    :param request: contrast.agent.request.Request instance
    :return: None
    """
    request.make_body_seekable()


def _track_wsgi_input(environ):
    wsgi_input = "wsgi.input"

    if wsgi_input in environ:
        if not hasattr(environ[wsgi_input], "cs__source"):
            environ[wsgi_input] = ContrastWsgiStreamProxy(environ[wsgi_input])

        environ[wsgi_input].cs__source = True
        environ[wsgi_input].cs__source_type = _get_source_by_content_type(environ)
        environ[wsgi_input].cs__source_tags = ["UNTRUSTED", "CROSS_SITE"]


def _get_source_by_content_type(environ):
    """
    Define the wsgi.input source type based on the request content type.
    If no specific content-type, the fault soruce type is BODY.
    """
    source_type = "BODY"

    content_type = environ.get("CONTENT_TYPE", "")
    if content_type == "application/x-www-form-urlencoded":
        source_type = "PARAMETER"
    elif content_type.startswith("multipart/"):
        source_type = (
            "MULTIPART_FORM_DATA"
            if "form-data" in content_type
            else "MULTIPART_CONTENT_DATA"
        )
    return source_type


@fail_loudly("Failed to remove webob environ variables")
def _remove_webob_environ_vars(environ):
    """
    webob adds several variables to the environ for efficiency. For example, if webob
    ever parses wsgi.input to extract request body parameters, it stores them in a
    MultiDict under environ['webob._parsed_post_vars']. This way, if a future middleware
    or application using webob tries to access the post params again, it doesn't need to
    re-parse the request body.

    This is a good idea, but it's really a pain for us. It means that it's not enough
    to simply track wsgi.input, because if it has already been parsed once by the time
    we call the environ tracker, data stored under these special webob.* keys won't be
    tracked. Here, we delete these variables, forcing webob to re-parse any necessary
    info using our now-tracked environ values. In the future, we should instead iterate
    over these entries and track their values explicitly, for the sake of performance.

    Another consequence of deleting these variables is that their values will
    necessarily be webob types for which we have patches. Since our request wrapper is a
    subclass of contrast.extern.webob.BaseRequest, we were ending up with _our_ externed
    webob objects in the application's environ. We don't have or want patches for our
    own externed webob, so this ensures that all of webob's cached environ values will
    have patches.

    We should always check to see if these values are present, even if we're inside
    of a framework that doesn't explicitly use webob. This is because it's possible that
    an earlier middleware used webob, causing the values to be added to environ.

    To the best of our current understanding, the following extra environ items are
    of interest:

    webob._parsed_query_vars
        A 2-tuple
        - first element is a MultiDict of parsed GET parameters
        - second element is the query string that was parsed

    webob._parsed_post_vars
        A 2-tuple
        - the first element is a MultiDict of parsed POST parameters
        - the second is the body stream that was parsed

    webob.adhoc_attrs
        A custom dictionary of arbitrary data passed between middlewares. We make a best
        effort to patch this, and we don't delete it, because we can't know much about
        it.

    webob._body_file
        A 2-tuple
        - first element is a double-wrapper for the raw wsgi.input stream
            BufferedReader(webob.LimitedLengthFile(wsgi.input))
        - second element is the underlying raw wsgi.input stream
            It should be PEP-333 compliant

    webob.is_body_seekable
        A boolean
        - Created/set to True once webob replaces wsgi.input with a seekable file-like
          object
        - Assumed to be False if missing
        - We do not remove this from environ, because we don't want webob to replace
          wsgi.input if possible (since by this point we've made it a source)

    webob._parsed_cookies
        A 2-tuple
        - first element is a dict of cookie keys to cookie values (parsed from
          HTTP_COOKIE)
        - second element is the HTTP_COOKIE string that was parsed to produce element #1

    webob._cache_control
        A 2-tuple
        - first element is the `HTTP_CACHE_CONTROL` header from the WSGI environ
        - second element is webob's parsed representation, a CacheControl object

    webob.url_encoding
        A string
        - Used to store the string encoding of the URL. We don't delete it because it's
          easy to track directly. In the future we might want to look into whether we
          need to track this at all.

    :param environ: WSGI environ dict
    :return: None
    """
    for key in WEBOB_KEYS_TO_DELETE:
        if key in environ:
            del environ[key]
