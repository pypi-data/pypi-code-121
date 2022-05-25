# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import ObjectProxy

from contrast.agent import scope
from contrast.agent.assess.policy import propagation_policy
from contrast.agent.assess.policy.source_policy import apply_stream_source
from contrast.utils.decorators import fail_quietly

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class BaseStreamProxy(ObjectProxy):
    """
    Base class for implementing stream proxies (marking streams as sources).

    Methods are represented as attributes on the proxy itself which enables us to
    "overwrite" methods even on objects that can't be monkey-patched.

    Proxying a stream (as opposed to instrumenting it directly) ensures that we'll
    be able to modify all relevant attributes. We don't necessarily know the type of
    the stream object we're instrumenting, and sometimes its attributes are
    read-only.

    We also can't use a simple class here, because some frameworks (WebOb) set
    additional attributes on wsgi.input, such as `seek`. We want to maintain as much
    of the original object's functionality as possible, so the best way is with an
    object proxy.

    See https://wrapt.readthedocs.io/en/latest/wrappers.html#proxy-object-attributes
    for details about object property attributes.

    TODO: PYT-917 In the future we may want to instrument write and writelines. This
        would require us to treat the stream more like a propagator than a source
        because trusted data could be written to it.

    TODO: PYT-917 We may eventually need to consider the less common __iter__ method,
        which is currently not instrumented. Werkzeug (at least) does not use __iter__
        when parsing wsgi.input; we may have to investigate WebOb's parser as well. It's
        also possible that the underlying implementation of __iter__ calls an already
        instrumented method for BytesIO, StringIO, etc.

    We might eventually be able to align this proxy hierarchy more closely with
    https://docs.python.org/3/library/io.html#class-hierarchy.
    Note that file objects in python 2 do not line up with this inheritance pattern:
    https://docs.python.org/2/library/stdtypes.html#bltin-file-objects.
    """

    CS__METHOD_NAMES = ["read", "readline", "readlines"]

    read = None
    readline = None
    readlines = None

    cs__tracked = False
    cs__source = False
    cs__properties = None
    cs__source_event = None
    cs__source_type = None
    cs__source_tags = None

    def __init__(self, wrapped):
        super().__init__(wrapped)
        for method_name in self.CS__METHOD_NAMES:
            setattr(self, method_name, getattr(wrapped, method_name, None))


class BaseRawIOProxy(BaseStreamProxy):
    """
    Like BaseStremProxy, but designed for streams that inherit from RawIOBase.

    TODO: PYT-917 We may eventually want to instrument `readinto(b)`
    """

    CS__METHOD_NAMES = BaseStreamProxy.CS__METHOD_NAMES + ["readall"]
    readall = None


class ContrastWsgiStreamProxy(BaseStreamProxy):
    """
    A concrete proxy that marks a PEP-333 compliant wsgi.input stream as a source.

    See https://www.python.org/dev/peps/pep-0333/#input-and-error-streams for the
    specification of this stream.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped)
        instrument_source_stream(self)


class ContrastFileProxy(BaseStreamProxy):
    """
    A concrete proxy that marks a file object (py27 exclusive) as a source.

    This class is identical to ContrastWsgiStreamProxy; however, this is because
    the py27 file object class has a nearly identical spec to the wsgi.input stream.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped)
        instrument_source_stream(self)


class ContrastBufferedReaderProxy(BaseStreamProxy):
    """
    A concrete proxy for BufferedReader (and BufferedRandom) streams.
    This has the same API as WSGI streams and PY2 file objects, but for clarity and
    consistency we've made a unique wrapper.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped)
        instrument_source_stream(self)


class ContrastRawIOProxy(BaseRawIOProxy):
    """
    A concrete proxy that marks a RawIOBase stream as a source.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped)
        instrument_source_stream(self)


def stream_patch_body(method_name, orig_func, self, *args, **kwargs):
    # Since we need to make reference to the input multiple times, convert the
    # first argument to a list and use that instead. This prevents any iterators
    # from being exhausted before we can make use of them in propagation.
    if method_name == "writelines" and len(args):
        args_list = [list(args[0])] + list(args[1:])
    else:
        args_list = args

    result = orig_func(*args_list, **kwargs)

    if scope.in_scope():
        return result

    try:
        with scope.propagation_scope():
            propagation_policy.propagate_stream(
                method_name,
                result,
                self,
                result,
                args_list,
                kwargs,
            )
    except Exception as ex:
        logger.debug("failed to propagate %s", method_name, exc_info=ex)
    finally:
        return result


@fail_quietly("Error instrumenting source stream")
def instrument_source_stream(stream):
    """
    Mark the provided stream as a source, and instrument methods that produce tracked
    content. This must be a stream that we have proxied. i.e., it has the
    `CS__METHOD_NAMES` attribute.

    @param stream: stream object proxied by BaseStreamProxy (must have the
        CS__METHOD_NAMES attribute)
    """
    stream.cs__source = True
    for method_name in stream.CS__METHOD_NAMES:
        _instrument_source_stream_method(stream, method_name)


def _instrument_source_stream_method(stream, method_name):
    """
    Instrument a method on a stream object.

    Only this particular stream instance is instrumented, because the patch is not
    applied at the class level.

    @param stream: file-like object conforming to to PEP 333's wsgi.input specification
    @param method_name: string, the name of the method to instrument
    """
    orig_method = getattr(stream, method_name, None)
    if orig_method is None:
        logger.debug(
            "WARNING: source stream missing expected attribute: %s", method_name
        )
        return
    new_method = _build_patch(stream, orig_method)
    setattr(stream, method_name, new_method)


def _build_patch(stream, orig_method):
    """
    Create a patch for the provided stream method. This is an instance method, so it is
    bound to a specific stream instance.

    Note that we cannot pass orig_method.__self__ to apply_stream_source. This is
    because if we're instrumenting a proxied stream, orig_method.__self__ points to the
    wrapped instance, not the wrapper. Only the wrapper has the cs__* attributes that we
    need for source application.

    @param orig_method: original instance method object
    @return method object that is an instrumented version of the original
    """

    def patched_method(*args, **kwargs):
        result = orig_method(*args, **kwargs)
        if not scope.in_scope():
            apply_stream_source(
                orig_method.__name__, result, stream, result, args, kwargs
            )
        return result

    patched_method.__name__ = orig_method.__name__
    return patched_method
