# -*- coding: utf-8 -*-
#
# TARGET arch is: x86_64
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes

class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



# if local wordsize is same as target, keep ctypes pointer function.
if ctypes.sizeof(ctypes.c_void_p) == 8:
    POINTER_T = ctypes.POINTER
else:
    class IncorrectWordSizeError(TypeError):
        pass
    # required to access _ctypes
    import _ctypes
    # Emulate a pointer class using the approriate c_int32/c_int64 type
    # The new class should have :
    # ['__module__', 'from_param', '_type_', '__dict__', '__weakref__', '__doc__']
    # but the class should be submitted to a unique instance for each base type
    # to that if A == B, POINTER_T(A) == POINTER_T(B)
    ctypes._pointer_t_type_cache = {}
    def POINTER_T(pointee):
        # a pointer should have the same length as LONG
        fake_ptr_base_type = ctypes.c_uint64
        # specific case for c_void_p
        if pointee is None: # VOID pointer type. c_void_p.
            pointee = type(None) # ctypes.c_void_p # ctypes.c_ulong
            clsname = 'c_void'
        else:
            clsname = pointee.__name__
        if clsname in ctypes._pointer_t_type_cache:
            return ctypes._pointer_t_type_cache[clsname]
        # make template
        class _T(_ctypes._SimpleCData,):
            _type_ = 'L'
            _subtype_ = pointee
            def _sub_addr_(self):
                return self.value
            def __repr__(self):
                return '%s(%d)'%(clsname, self.value)
            def contents(self):
                raise IncorrectWordSizeError('This is not a ctypes pointer.')
            def __init__(self, **args):
                raise IncorrectWordSizeError('This is not a ctypes pointer. It is not instanciable.')
        _class = type('LP_%d_%s'%(8, clsname), (_T,),{})
        ctypes._pointer_t_type_cache[clsname] = _class
        return _class

def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, POINTER_T(ctypes.c_char))



c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16


_libraries = {}

import os

def _load_library(libname, loader=ctypes.CDLL):
    global _libraries
    _paths = [
        libname,  # globaly installed (/lib, /usr/lib, ...)
        os.path.join(os.path.dirname(__file__), libname),  # venv site-packages/bundle directory
        os.path.join(os.path.dirname(__file__), "..", libname),  # venv site-packages directory
        os.path.join(os.path.dirname(__file__), "../../", libname),  # venv usr/lib directory
    ]
    _last_exception = None
    for path in _paths:
        try:
            return loader(path)
        except OSError as e:
            _last_exception = e
    raise _last_exception

_libraries['libpomp.so'] = _load_library('libpomp.so')
_libraries['libmedia-buffers.so'] = _load_library('libmedia-buffers.so')
_libraries['libmedia-buffers-memory.so'] = _load_library('libmedia-buffers-memory.so')
_libraries['libvideo-defs.so'] = _load_library('libvideo-defs.so')

class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  _load_library('FIXME_STUB')
_libraries['libvideo-metadata.so'] = _load_library('libvideo-metadata.so')
_libraries['libpdraw.so'] = _load_library('libpdraw.so')
_libraries['libarsdk.so'] = _load_library('libarsdk.so')
_libraries['libarsdkctrl.so'] = _load_library('libarsdkctrl.so')
_libraries['libmedia-buffers-memory-generic.so'] = _load_library('libmedia-buffers-memory-generic.so')
_libraries['libmp4.so'] = _load_library('libmp4.so')
_libraries['libmux.so'] = _load_library('libmux.so')



_STDINT_H = (1) # macro
__GLIBC_INTERNAL_STARTING_HEADER_IMPLEMENTATION = True # macro
__intptr_t_defined = True # macro

# macro function __INT64_C

# macro function __UINT64_C
INT8_MIN = (- 128) # macro
INT16_MIN = (- 32767 - 1) # macro
INT32_MIN = (- 2147483647 - 1) # macro
INT64_MIN = (- 9223372036854775807 - 1) # macro
INT8_MAX = (127) # macro
INT16_MAX = (32767) # macro
INT32_MAX = (2147483647) # macro
INT64_MAX = (9223372036854775807) # macro
UINT8_MAX = (255) # macro
UINT16_MAX = (65535) # macro
UINT32_MAX = (4294967295) # macro
UINT64_MAX = (18446744073709551615) # macro
INT_LEAST8_MIN = (- 128) # macro
INT_LEAST16_MIN = (- 32767 - 1) # macro
INT_LEAST32_MIN = (- 2147483647 - 1) # macro
INT_LEAST64_MIN = (- 9223372036854775807 - 1) # macro
INT_LEAST8_MAX = (127) # macro
INT_LEAST16_MAX = (32767) # macro
INT_LEAST32_MAX = (2147483647) # macro
INT_LEAST64_MAX = (9223372036854775807) # macro
UINT_LEAST8_MAX = (255) # macro
UINT_LEAST16_MAX = (65535) # macro
UINT_LEAST32_MAX = (4294967295) # macro
UINT_LEAST64_MAX = (18446744073709551615) # macro
INT_FAST8_MIN = (- 128) # macro
INT_FAST16_MIN = (- 9223372036854775807 - 1) # macro
INT_FAST32_MIN = (- 9223372036854775807 - 1) # macro
INT_FAST64_MIN = (- 9223372036854775807 - 1) # macro
INT_FAST8_MAX = (127) # macro
INT_FAST16_MAX = (9223372036854775807) # macro
INT_FAST32_MAX = (9223372036854775807) # macro
INT_FAST64_MAX = (9223372036854775807) # macro
UINT_FAST8_MAX = (255) # macro
UINT_FAST16_MAX = (18446744073709551615) # macro
UINT_FAST32_MAX = (18446744073709551615) # macro
UINT_FAST64_MAX = (18446744073709551615) # macro
INTPTR_MIN = (- 9223372036854775807 - 1) # macro
INTPTR_MAX = (9223372036854775807) # macro
UINTPTR_MAX = (18446744073709551615) # macro
INTMAX_MIN = (- 9223372036854775807 - 1) # macro
INTMAX_MAX = (9223372036854775807) # macro
UINTMAX_MAX = (18446744073709551615) # macro
PTRDIFF_MIN = (- 9223372036854775807 - 1) # macro
PTRDIFF_MAX = (9223372036854775807) # macro
SIG_ATOMIC_MIN = (- 2147483647 - 1) # macro
SIG_ATOMIC_MAX = (2147483647) # macro
SIZE_MAX = (18446744073709551615) # macro
# WCHAR_MIN = __WCHAR_MIN # macro
# WCHAR_MAX = __WCHAR_MAX # macro
WINT_MIN = (0) # macro
WINT_MAX = (4294967295) # macro

# macro function INT8_C

# macro function INT16_C

# macro function INT32_C

# macro function INT64_C

# macro function UINT8_C

# macro function UINT16_C

# macro function UINT32_C

# macro function UINT64_C

# macro function INTMAX_C

# macro function UINTMAX_C
INT8_WIDTH = (8) # macro
UINT8_WIDTH = (8) # macro
INT16_WIDTH = (16) # macro
UINT16_WIDTH = (16) # macro
INT32_WIDTH = (32) # macro
UINT32_WIDTH = (32) # macro
INT64_WIDTH = (64) # macro
UINT64_WIDTH = (64) # macro
INT_LEAST8_WIDTH = (8) # macro
UINT_LEAST8_WIDTH = (8) # macro
INT_LEAST16_WIDTH = (16) # macro
UINT_LEAST16_WIDTH = (16) # macro
INT_LEAST32_WIDTH = (32) # macro
UINT_LEAST32_WIDTH = (32) # macro
INT_LEAST64_WIDTH = (64) # macro
UINT_LEAST64_WIDTH = (64) # macro
INT_FAST8_WIDTH = (8) # macro
UINT_FAST8_WIDTH = (8) # macro
# INT_FAST16_WIDTH = __WORDSIZE # macro
# UINT_FAST16_WIDTH = __WORDSIZE # macro
# INT_FAST32_WIDTH = __WORDSIZE # macro
# UINT_FAST32_WIDTH = __WORDSIZE # macro
INT_FAST64_WIDTH = (64) # macro
UINT_FAST64_WIDTH = (64) # macro
# INTPTR_WIDTH = __WORDSIZE # macro
# UINTPTR_WIDTH = __WORDSIZE # macro
INTMAX_WIDTH = (64) # macro
UINTMAX_WIDTH = (64) # macro
# PTRDIFF_WIDTH = __WORDSIZE # macro
SIG_ATOMIC_WIDTH = (32) # macro
# SIZE_WIDTH = __WORDSIZE # macro
WCHAR_WIDTH = (32) # macro
WINT_WIDTH = (32) # macro
int_least8_t = ctypes.c_byte
int_least16_t = ctypes.c_int16
int_least32_t = ctypes.c_int32
int_least64_t = ctypes.c_int64
uint_least8_t = ctypes.c_ubyte
uint_least16_t = ctypes.c_uint16
uint_least32_t = ctypes.c_uint32
uint_least64_t = ctypes.c_uint64
int_fast8_t = ctypes.c_byte
int_fast16_t = ctypes.c_int64
int_fast32_t = ctypes.c_int64
int_fast64_t = ctypes.c_int64
uint_fast8_t = ctypes.c_ubyte
uint_fast16_t = ctypes.c_uint64
uint_fast32_t = ctypes.c_uint64
uint_fast64_t = ctypes.c_uint64
intptr_t = ctypes.c_int64
uintptr_t = ctypes.c_uint64
intmax_t = ctypes.c_int64
uintmax_t = ctypes.c_uint64
_LIBPOMP_H_ = True # macro

# macro function POMP_ATTRIBUTE_FORMAT_PRINTF

# macro function POMP_ATTRIBUTE_FORMAT_SCANF
# POMP_API = (None) # macro
class struct_pomp_ctx(Structure):
    pass

class struct_pomp_conn(Structure):
    pass

class struct_pomp_buffer(Structure):
    pass

class struct_pomp_msg(Structure):
    pass

class struct_pomp_loop(Structure):
    pass

class struct_pomp_evt(Structure):
    pass

class struct_pomp_timer(Structure):
    pass

class struct_pomp_sockaddr_storage(Structure):
    pass

struct_pomp_sockaddr_storage._pack_ = True # source:False
struct_pomp_sockaddr_storage._fields_ = [
    ('__data', ctypes.c_char * 128),
]


# values for enumeration 'pomp_event'
pomp_event__enumvalues = {
    0: 'POMP_EVENT_CONNECTED',
    1: 'POMP_EVENT_DISCONNECTED',
    2: 'POMP_EVENT_MSG',
}
POMP_EVENT_CONNECTED = 0
POMP_EVENT_DISCONNECTED = 1
POMP_EVENT_MSG = 2
pomp_event = ctypes.c_uint32 # enum
pomp_event_str = _libraries['libpomp.so'].pomp_event_str
pomp_event_str.restype = POINTER_T(ctypes.c_char)
pomp_event_str.argtypes = [pomp_event]

# values for enumeration 'pomp_fd_event'
pomp_fd_event__enumvalues = {
    1: 'POMP_FD_EVENT_IN',
    2: 'POMP_FD_EVENT_PRI',
    4: 'POMP_FD_EVENT_OUT',
    8: 'POMP_FD_EVENT_ERR',
    16: 'POMP_FD_EVENT_HUP',
}
POMP_FD_EVENT_IN = 1
POMP_FD_EVENT_PRI = 2
POMP_FD_EVENT_OUT = 4
POMP_FD_EVENT_ERR = 8
POMP_FD_EVENT_HUP = 16
pomp_fd_event = ctypes.c_uint32 # enum

# values for enumeration 'pomp_socket_kind'
pomp_socket_kind__enumvalues = {
    0: 'POMP_SOCKET_KIND_SERVER',
    1: 'POMP_SOCKET_KIND_PEER',
    2: 'POMP_SOCKET_KIND_CLIENT',
    3: 'POMP_SOCKET_KIND_DGRAM',
}
POMP_SOCKET_KIND_SERVER = 0
POMP_SOCKET_KIND_PEER = 1
POMP_SOCKET_KIND_CLIENT = 2
POMP_SOCKET_KIND_DGRAM = 3
pomp_socket_kind = ctypes.c_uint32 # enum
pomp_socket_kind_str = _libraries['libpomp.so'].pomp_socket_kind_str
pomp_socket_kind_str.restype = POINTER_T(ctypes.c_char)
pomp_socket_kind_str.argtypes = [pomp_socket_kind]

# values for enumeration 'pomp_send_status'
pomp_send_status__enumvalues = {
    1: 'POMP_SEND_STATUS_OK',
    2: 'POMP_SEND_STATUS_ERROR',
    4: 'POMP_SEND_STATUS_ABORTED',
    8: 'POMP_SEND_STATUS_QUEUE_EMPTY',
}
POMP_SEND_STATUS_OK = 1
POMP_SEND_STATUS_ERROR = 2
POMP_SEND_STATUS_ABORTED = 4
POMP_SEND_STATUS_QUEUE_EMPTY = 8
pomp_send_status = ctypes.c_uint32 # enum
class struct_pomp_cred(Structure):
    pass

struct_pomp_cred._pack_ = True # source:False
struct_pomp_cred._fields_ = [
    ('pid', ctypes.c_uint32),
    ('uid', ctypes.c_uint32),
    ('gid', ctypes.c_uint32),
]

pomp_event_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_ctx), pomp_event, POINTER_T(struct_pomp_conn), POINTER_T(struct_pomp_msg), POINTER_T(None))
pomp_ctx_raw_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_conn), POINTER_T(struct_pomp_buffer), POINTER_T(None))
pomp_socket_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_ctx), ctypes.c_int32, pomp_socket_kind, POINTER_T(None))
pomp_send_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_conn), POINTER_T(struct_pomp_buffer), ctypes.c_uint32, POINTER_T(None), POINTER_T(None))
pomp_fd_event_cb_t = ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.c_uint32, POINTER_T(None))
pomp_evt_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_evt), POINTER_T(None))
pomp_timer_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_timer), POINTER_T(None))
pomp_idle_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(None))
pomp_watchdog_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_pomp_loop), POINTER_T(None))
pomp_ctx_new = _libraries['libpomp.so'].pomp_ctx_new
pomp_ctx_new.restype = POINTER_T(struct_pomp_ctx)
pomp_ctx_new.argtypes = [pomp_event_cb_t, POINTER_T(None)]
pomp_ctx_new_with_loop = _libraries['libpomp.so'].pomp_ctx_new_with_loop
pomp_ctx_new_with_loop.restype = POINTER_T(struct_pomp_ctx)
pomp_ctx_new_with_loop.argtypes = [pomp_event_cb_t, POINTER_T(None), POINTER_T(struct_pomp_loop)]
pomp_ctx_set_raw = _libraries['libpomp.so'].pomp_ctx_set_raw
pomp_ctx_set_raw.restype = ctypes.c_int32
pomp_ctx_set_raw.argtypes = [POINTER_T(struct_pomp_ctx), pomp_ctx_raw_cb_t]
pomp_ctx_set_socket_cb = _libraries['libpomp.so'].pomp_ctx_set_socket_cb
pomp_ctx_set_socket_cb.restype = ctypes.c_int32
pomp_ctx_set_socket_cb.argtypes = [POINTER_T(struct_pomp_ctx), pomp_socket_cb_t]
pomp_ctx_set_send_cb = _libraries['libpomp.so'].pomp_ctx_set_send_cb
pomp_ctx_set_send_cb.restype = ctypes.c_int32
pomp_ctx_set_send_cb.argtypes = [POINTER_T(struct_pomp_ctx), pomp_send_cb_t]
pomp_ctx_setup_keepalive = _libraries['libpomp.so'].pomp_ctx_setup_keepalive
pomp_ctx_setup_keepalive.restype = ctypes.c_int32
pomp_ctx_setup_keepalive.argtypes = [POINTER_T(struct_pomp_ctx), ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
pomp_ctx_destroy = _libraries['libpomp.so'].pomp_ctx_destroy
pomp_ctx_destroy.restype = ctypes.c_int32
pomp_ctx_destroy.argtypes = [POINTER_T(struct_pomp_ctx)]
uint32_t = ctypes.c_uint32
class struct_sockaddr(Structure):
    pass

pomp_ctx_listen = _libraries['libpomp.so'].pomp_ctx_listen
pomp_ctx_listen.restype = ctypes.c_int32
pomp_ctx_listen.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_sockaddr), uint32_t]
pomp_ctx_listen_with_access_mode = _libraries['libpomp.so'].pomp_ctx_listen_with_access_mode
pomp_ctx_listen_with_access_mode.restype = ctypes.c_int32
pomp_ctx_listen_with_access_mode.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_sockaddr), uint32_t, uint32_t]
pomp_ctx_connect = _libraries['libpomp.so'].pomp_ctx_connect
pomp_ctx_connect.restype = ctypes.c_int32
pomp_ctx_connect.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_sockaddr), uint32_t]
pomp_ctx_bind = _libraries['libpomp.so'].pomp_ctx_bind
pomp_ctx_bind.restype = ctypes.c_int32
pomp_ctx_bind.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_sockaddr), uint32_t]
pomp_ctx_stop = _libraries['libpomp.so'].pomp_ctx_stop
pomp_ctx_stop.restype = ctypes.c_int32
pomp_ctx_stop.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_get_loop = _libraries['libpomp.so'].pomp_ctx_get_loop
pomp_ctx_get_loop.restype = POINTER_T(struct_pomp_loop)
pomp_ctx_get_loop.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_get_fd = _libraries['libpomp.so'].pomp_ctx_get_fd
pomp_ctx_get_fd.restype = intptr_t
pomp_ctx_get_fd.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_process_fd = _libraries['libpomp.so'].pomp_ctx_process_fd
pomp_ctx_process_fd.restype = ctypes.c_int32
pomp_ctx_process_fd.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_wait_and_process = _libraries['libpomp.so'].pomp_ctx_wait_and_process
pomp_ctx_wait_and_process.restype = ctypes.c_int32
pomp_ctx_wait_and_process.argtypes = [POINTER_T(struct_pomp_ctx), ctypes.c_int32]
pomp_ctx_wakeup = _libraries['libpomp.so'].pomp_ctx_wakeup
pomp_ctx_wakeup.restype = ctypes.c_int32
pomp_ctx_wakeup.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_get_next_conn = _libraries['libpomp.so'].pomp_ctx_get_next_conn
pomp_ctx_get_next_conn.restype = POINTER_T(struct_pomp_conn)
pomp_ctx_get_next_conn.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_conn)]
pomp_ctx_get_conn = _libraries['libpomp.so'].pomp_ctx_get_conn
pomp_ctx_get_conn.restype = POINTER_T(struct_pomp_conn)
pomp_ctx_get_conn.argtypes = [POINTER_T(struct_pomp_ctx)]
pomp_ctx_get_local_addr = _libraries['libpomp.so'].pomp_ctx_get_local_addr
pomp_ctx_get_local_addr.restype = POINTER_T(struct_sockaddr)
pomp_ctx_get_local_addr.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(ctypes.c_uint32)]
pomp_ctx_send_msg = _libraries['libpomp.so'].pomp_ctx_send_msg
pomp_ctx_send_msg.restype = ctypes.c_int32
pomp_ctx_send_msg.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_msg)]
pomp_ctx_send_msg_to = _libraries['libpomp.so'].pomp_ctx_send_msg_to
pomp_ctx_send_msg_to.restype = ctypes.c_int32
pomp_ctx_send_msg_to.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_msg), POINTER_T(struct_sockaddr), uint32_t]
pomp_ctx_send = _libraries['libpomp.so'].pomp_ctx_send
pomp_ctx_send.restype = ctypes.c_int32
pomp_ctx_send.argtypes = [POINTER_T(struct_pomp_ctx), uint32_t, POINTER_T(ctypes.c_char)]
class struct___va_list_tag(Structure):
    pass

struct___va_list_tag._pack_ = True # source:False
struct___va_list_tag._fields_ = [
    ('gp_offset', ctypes.c_uint32),
    ('fp_offset', ctypes.c_uint32),
    ('overflow_arg_area', POINTER_T(None)),
    ('reg_save_area', POINTER_T(None)),
]

va_list = struct___va_list_tag * 1
pomp_ctx_sendv = _libraries['libpomp.so'].pomp_ctx_sendv
pomp_ctx_sendv.restype = ctypes.c_int32
pomp_ctx_sendv.argtypes = [POINTER_T(struct_pomp_ctx), uint32_t, POINTER_T(ctypes.c_char), va_list]
pomp_ctx_send_raw_buf = _libraries['libpomp.so'].pomp_ctx_send_raw_buf
pomp_ctx_send_raw_buf.restype = ctypes.c_int32
pomp_ctx_send_raw_buf.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_buffer)]
pomp_ctx_send_raw_buf_to = _libraries['libpomp.so'].pomp_ctx_send_raw_buf_to
pomp_ctx_send_raw_buf_to.restype = ctypes.c_int32
pomp_ctx_send_raw_buf_to.argtypes = [POINTER_T(struct_pomp_ctx), POINTER_T(struct_pomp_buffer), POINTER_T(struct_sockaddr), uint32_t]
size_t = ctypes.c_uint64
pomp_ctx_set_read_buffer_len = _libraries['libpomp.so'].pomp_ctx_set_read_buffer_len
pomp_ctx_set_read_buffer_len.restype = ctypes.c_int32
pomp_ctx_set_read_buffer_len.argtypes = [POINTER_T(struct_pomp_ctx), size_t]
pomp_conn_disconnect = _libraries['libpomp.so'].pomp_conn_disconnect
pomp_conn_disconnect.restype = ctypes.c_int32
pomp_conn_disconnect.argtypes = [POINTER_T(struct_pomp_conn)]
pomp_conn_get_local_addr = _libraries['libpomp.so'].pomp_conn_get_local_addr
pomp_conn_get_local_addr.restype = POINTER_T(struct_sockaddr)
pomp_conn_get_local_addr.argtypes = [POINTER_T(struct_pomp_conn), POINTER_T(ctypes.c_uint32)]
pomp_conn_get_peer_addr = _libraries['libpomp.so'].pomp_conn_get_peer_addr
pomp_conn_get_peer_addr.restype = POINTER_T(struct_sockaddr)
pomp_conn_get_peer_addr.argtypes = [POINTER_T(struct_pomp_conn), POINTER_T(ctypes.c_uint32)]
pomp_conn_get_peer_cred = _libraries['libpomp.so'].pomp_conn_get_peer_cred
pomp_conn_get_peer_cred.restype = POINTER_T(struct_pomp_cred)
pomp_conn_get_peer_cred.argtypes = [POINTER_T(struct_pomp_conn)]
pomp_conn_get_fd = _libraries['libpomp.so'].pomp_conn_get_fd
pomp_conn_get_fd.restype = ctypes.c_int32
pomp_conn_get_fd.argtypes = [POINTER_T(struct_pomp_conn)]
pomp_conn_suspend_read = _libraries['libpomp.so'].pomp_conn_suspend_read
pomp_conn_suspend_read.restype = ctypes.c_int32
pomp_conn_suspend_read.argtypes = [POINTER_T(struct_pomp_conn)]
pomp_conn_resume_read = _libraries['libpomp.so'].pomp_conn_resume_read
pomp_conn_resume_read.restype = ctypes.c_int32
pomp_conn_resume_read.argtypes = [POINTER_T(struct_pomp_conn)]
pomp_conn_send_msg = _libraries['libpomp.so'].pomp_conn_send_msg
pomp_conn_send_msg.restype = ctypes.c_int32
pomp_conn_send_msg.argtypes = [POINTER_T(struct_pomp_conn), POINTER_T(struct_pomp_msg)]
pomp_conn_send = _libraries['libpomp.so'].pomp_conn_send
pomp_conn_send.restype = ctypes.c_int32
pomp_conn_send.argtypes = [POINTER_T(struct_pomp_conn), uint32_t, POINTER_T(ctypes.c_char)]
pomp_conn_sendv = _libraries['libpomp.so'].pomp_conn_sendv
pomp_conn_sendv.restype = ctypes.c_int32
pomp_conn_sendv.argtypes = [POINTER_T(struct_pomp_conn), uint32_t, POINTER_T(ctypes.c_char), va_list]
pomp_conn_send_raw_buf = _libraries['libpomp.so'].pomp_conn_send_raw_buf
pomp_conn_send_raw_buf.restype = ctypes.c_int32
pomp_conn_send_raw_buf.argtypes = [POINTER_T(struct_pomp_conn), POINTER_T(struct_pomp_buffer)]
pomp_conn_set_read_buffer_len = _libraries['libpomp.so'].pomp_conn_set_read_buffer_len
pomp_conn_set_read_buffer_len.restype = ctypes.c_int32
pomp_conn_set_read_buffer_len.argtypes = [POINTER_T(struct_pomp_conn), size_t]
pomp_buffer_new = _libraries['libpomp.so'].pomp_buffer_new
pomp_buffer_new.restype = POINTER_T(struct_pomp_buffer)
pomp_buffer_new.argtypes = [size_t]
pomp_buffer_new_copy = _libraries['libpomp.so'].pomp_buffer_new_copy
pomp_buffer_new_copy.restype = POINTER_T(struct_pomp_buffer)
pomp_buffer_new_copy.argtypes = [POINTER_T(struct_pomp_buffer)]
pomp_buffer_new_with_data = _libraries['libpomp.so'].pomp_buffer_new_with_data
pomp_buffer_new_with_data.restype = POINTER_T(struct_pomp_buffer)
pomp_buffer_new_with_data.argtypes = [POINTER_T(None), size_t]
pomp_buffer_new_get_data = _libraries['libpomp.so'].pomp_buffer_new_get_data
pomp_buffer_new_get_data.restype = POINTER_T(struct_pomp_buffer)
pomp_buffer_new_get_data.argtypes = [size_t, POINTER_T(POINTER_T(None))]
pomp_buffer_ref = _libraries['libpomp.so'].pomp_buffer_ref
pomp_buffer_ref.restype = None
pomp_buffer_ref.argtypes = [POINTER_T(struct_pomp_buffer)]
pomp_buffer_unref = _libraries['libpomp.so'].pomp_buffer_unref
pomp_buffer_unref.restype = None
pomp_buffer_unref.argtypes = [POINTER_T(struct_pomp_buffer)]
pomp_buffer_is_shared = _libraries['libpomp.so'].pomp_buffer_is_shared
pomp_buffer_is_shared.restype = ctypes.c_int32
pomp_buffer_is_shared.argtypes = [POINTER_T(struct_pomp_buffer)]
pomp_buffer_set_capacity = _libraries['libpomp.so'].pomp_buffer_set_capacity
pomp_buffer_set_capacity.restype = ctypes.c_int32
pomp_buffer_set_capacity.argtypes = [POINTER_T(struct_pomp_buffer), size_t]
pomp_buffer_ensure_capacity = _libraries['libpomp.so'].pomp_buffer_ensure_capacity
pomp_buffer_ensure_capacity.restype = ctypes.c_int32
pomp_buffer_ensure_capacity.argtypes = [POINTER_T(struct_pomp_buffer), size_t]
pomp_buffer_set_len = _libraries['libpomp.so'].pomp_buffer_set_len
pomp_buffer_set_len.restype = ctypes.c_int32
pomp_buffer_set_len.argtypes = [POINTER_T(struct_pomp_buffer), size_t]
pomp_buffer_get_data = _libraries['libpomp.so'].pomp_buffer_get_data
pomp_buffer_get_data.restype = ctypes.c_int32
pomp_buffer_get_data.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint64)]
pomp_buffer_get_cdata = _libraries['libpomp.so'].pomp_buffer_get_cdata
pomp_buffer_get_cdata.restype = ctypes.c_int32
pomp_buffer_get_cdata.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint64)]
pomp_buffer_append_data = _libraries['libpomp.so'].pomp_buffer_append_data
pomp_buffer_append_data.restype = ctypes.c_int32
pomp_buffer_append_data.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(None), size_t]
pomp_buffer_append_buffer = _libraries['libpomp.so'].pomp_buffer_append_buffer
pomp_buffer_append_buffer.restype = ctypes.c_int32
pomp_buffer_append_buffer.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(struct_pomp_buffer)]
pomp_buffer_write = _libraries['libpomp.so'].pomp_buffer_write
pomp_buffer_write.restype = ctypes.c_int32
pomp_buffer_write.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(ctypes.c_uint64), POINTER_T(None), size_t]
pomp_buffer_read = _libraries['libpomp.so'].pomp_buffer_read
pomp_buffer_read.restype = ctypes.c_int32
pomp_buffer_read.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(ctypes.c_uint64), POINTER_T(None), size_t]
pomp_buffer_cread = _libraries['libpomp.so'].pomp_buffer_cread
pomp_buffer_cread.restype = ctypes.c_int32
pomp_buffer_cread.argtypes = [POINTER_T(struct_pomp_buffer), POINTER_T(ctypes.c_uint64), POINTER_T(POINTER_T(None)), size_t]
pomp_msg_new = _libraries['libpomp.so'].pomp_msg_new
pomp_msg_new.restype = POINTER_T(struct_pomp_msg)
pomp_msg_new.argtypes = []
pomp_msg_new_copy = _libraries['libpomp.so'].pomp_msg_new_copy
pomp_msg_new_copy.restype = POINTER_T(struct_pomp_msg)
pomp_msg_new_copy.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_msg_new_with_buffer = _libraries['libpomp.so'].pomp_msg_new_with_buffer
pomp_msg_new_with_buffer.restype = POINTER_T(struct_pomp_msg)
pomp_msg_new_with_buffer.argtypes = [POINTER_T(struct_pomp_buffer)]
pomp_msg_destroy = _libraries['libpomp.so'].pomp_msg_destroy
pomp_msg_destroy.restype = ctypes.c_int32
pomp_msg_destroy.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_msg_get_id = _libraries['libpomp.so'].pomp_msg_get_id
pomp_msg_get_id.restype = uint32_t
pomp_msg_get_id.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_msg_get_buffer = _libraries['libpomp.so'].pomp_msg_get_buffer
pomp_msg_get_buffer.restype = POINTER_T(struct_pomp_buffer)
pomp_msg_get_buffer.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_msg_write = _libraries['libpomp.so'].pomp_msg_write
pomp_msg_write.restype = ctypes.c_int32
pomp_msg_write.argtypes = [POINTER_T(struct_pomp_msg), uint32_t, POINTER_T(ctypes.c_char)]
pomp_msg_writev = _libraries['libpomp.so'].pomp_msg_writev
pomp_msg_writev.restype = ctypes.c_int32
pomp_msg_writev.argtypes = [POINTER_T(struct_pomp_msg), uint32_t, POINTER_T(ctypes.c_char), va_list]
pomp_msg_write_argv = _libraries['libpomp.so'].pomp_msg_write_argv
pomp_msg_write_argv.restype = ctypes.c_int32
pomp_msg_write_argv.argtypes = [POINTER_T(struct_pomp_msg), uint32_t, POINTER_T(ctypes.c_char), ctypes.c_int32, POINTER_T(POINTER_T(ctypes.c_char))]
pomp_msg_read = _libraries['libpomp.so'].pomp_msg_read
pomp_msg_read.restype = ctypes.c_int32
pomp_msg_read.argtypes = [POINTER_T(struct_pomp_msg), POINTER_T(ctypes.c_char)]
pomp_msg_readv = _libraries['libpomp.so'].pomp_msg_readv
pomp_msg_readv.restype = ctypes.c_int32
pomp_msg_readv.argtypes = [POINTER_T(struct_pomp_msg), POINTER_T(ctypes.c_char), va_list]
pomp_msg_dump = _libraries['libpomp.so'].pomp_msg_dump
pomp_msg_dump.restype = ctypes.c_int32
pomp_msg_dump.argtypes = [POINTER_T(struct_pomp_msg), POINTER_T(ctypes.c_char), uint32_t]
pomp_msg_adump = _libraries['libpomp.so'].pomp_msg_adump
pomp_msg_adump.restype = ctypes.c_int32
pomp_msg_adump.argtypes = [POINTER_T(struct_pomp_msg), POINTER_T(POINTER_T(ctypes.c_char))]
pomp_loop_new = _libraries['libpomp.so'].pomp_loop_new
pomp_loop_new.restype = POINTER_T(struct_pomp_loop)
pomp_loop_new.argtypes = []
pomp_loop_destroy = _libraries['libpomp.so'].pomp_loop_destroy
pomp_loop_destroy.restype = ctypes.c_int32
pomp_loop_destroy.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_loop_add = _libraries['libpomp.so'].pomp_loop_add
pomp_loop_add.restype = ctypes.c_int32
pomp_loop_add.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32, uint32_t, pomp_fd_event_cb_t, POINTER_T(None)]
pomp_loop_update = _libraries['libpomp.so'].pomp_loop_update
pomp_loop_update.restype = ctypes.c_int32
pomp_loop_update.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32, uint32_t]
pomp_loop_update2 = _libraries['libpomp.so'].pomp_loop_update2
pomp_loop_update2.restype = ctypes.c_int32
pomp_loop_update2.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32, uint32_t, uint32_t]
pomp_loop_remove = _libraries['libpomp.so'].pomp_loop_remove
pomp_loop_remove.restype = ctypes.c_int32
pomp_loop_remove.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32]
pomp_loop_has_fd = _libraries['libpomp.so'].pomp_loop_has_fd
pomp_loop_has_fd.restype = ctypes.c_int32
pomp_loop_has_fd.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32]
pomp_loop_get_fd = _libraries['libpomp.so'].pomp_loop_get_fd
pomp_loop_get_fd.restype = intptr_t
pomp_loop_get_fd.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_loop_process_fd = _libraries['libpomp.so'].pomp_loop_process_fd
pomp_loop_process_fd.restype = ctypes.c_int32
pomp_loop_process_fd.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_loop_wait_and_process = _libraries['libpomp.so'].pomp_loop_wait_and_process
pomp_loop_wait_and_process.restype = ctypes.c_int32
pomp_loop_wait_and_process.argtypes = [POINTER_T(struct_pomp_loop), ctypes.c_int32]
pomp_loop_wakeup = _libraries['libpomp.so'].pomp_loop_wakeup
pomp_loop_wakeup.restype = ctypes.c_int32
pomp_loop_wakeup.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_loop_idle_add = _libraries['libpomp.so'].pomp_loop_idle_add
pomp_loop_idle_add.restype = ctypes.c_int32
pomp_loop_idle_add.argtypes = [POINTER_T(struct_pomp_loop), pomp_idle_cb_t, POINTER_T(None)]
pomp_loop_idle_add_with_cookie = _libraries['libpomp.so'].pomp_loop_idle_add_with_cookie
pomp_loop_idle_add_with_cookie.restype = ctypes.c_int32
pomp_loop_idle_add_with_cookie.argtypes = [POINTER_T(struct_pomp_loop), pomp_idle_cb_t, POINTER_T(None), POINTER_T(None)]
pomp_loop_idle_remove = _libraries['libpomp.so'].pomp_loop_idle_remove
pomp_loop_idle_remove.restype = ctypes.c_int32
pomp_loop_idle_remove.argtypes = [POINTER_T(struct_pomp_loop), pomp_idle_cb_t, POINTER_T(None)]
pomp_loop_idle_remove_by_cookie = _libraries['libpomp.so'].pomp_loop_idle_remove_by_cookie
pomp_loop_idle_remove_by_cookie.restype = ctypes.c_int32
pomp_loop_idle_remove_by_cookie.argtypes = [POINTER_T(struct_pomp_loop), POINTER_T(None)]
pomp_loop_idle_flush = _libraries['libpomp.so'].pomp_loop_idle_flush
pomp_loop_idle_flush.restype = ctypes.c_int32
pomp_loop_idle_flush.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_loop_idle_flush_by_cookie = _libraries['libpomp.so'].pomp_loop_idle_flush_by_cookie
pomp_loop_idle_flush_by_cookie.restype = ctypes.c_int32
pomp_loop_idle_flush_by_cookie.argtypes = [POINTER_T(struct_pomp_loop), POINTER_T(None)]
pomp_loop_watchdog_enable = _libraries['libpomp.so'].pomp_loop_watchdog_enable
pomp_loop_watchdog_enable.restype = ctypes.c_int32
pomp_loop_watchdog_enable.argtypes = [POINTER_T(struct_pomp_loop), uint32_t, pomp_watchdog_cb_t, POINTER_T(None)]
pomp_loop_watchdog_disable = _libraries['libpomp.so'].pomp_loop_watchdog_disable
pomp_loop_watchdog_disable.restype = ctypes.c_int32
pomp_loop_watchdog_disable.argtypes = [POINTER_T(struct_pomp_loop)]
pomp_evt_new = _libraries['libpomp.so'].pomp_evt_new
pomp_evt_new.restype = POINTER_T(struct_pomp_evt)
pomp_evt_new.argtypes = []
pomp_evt_destroy = _libraries['libpomp.so'].pomp_evt_destroy
pomp_evt_destroy.restype = ctypes.c_int32
pomp_evt_destroy.argtypes = [POINTER_T(struct_pomp_evt)]
pomp_evt_attach_to_loop = _libraries['libpomp.so'].pomp_evt_attach_to_loop
pomp_evt_attach_to_loop.restype = ctypes.c_int32
pomp_evt_attach_to_loop.argtypes = [POINTER_T(struct_pomp_evt), POINTER_T(struct_pomp_loop), pomp_evt_cb_t, POINTER_T(None)]
pomp_evt_detach_from_loop = _libraries['libpomp.so'].pomp_evt_detach_from_loop
pomp_evt_detach_from_loop.restype = ctypes.c_int32
pomp_evt_detach_from_loop.argtypes = [POINTER_T(struct_pomp_evt), POINTER_T(struct_pomp_loop)]
pomp_evt_is_attached = _libraries['libpomp.so'].pomp_evt_is_attached
pomp_evt_is_attached.restype = ctypes.c_int32
pomp_evt_is_attached.argtypes = [POINTER_T(struct_pomp_evt), POINTER_T(struct_pomp_loop)]
pomp_evt_signal = _libraries['libpomp.so'].pomp_evt_signal
pomp_evt_signal.restype = ctypes.c_int32
pomp_evt_signal.argtypes = [POINTER_T(struct_pomp_evt)]
pomp_evt_clear = _libraries['libpomp.so'].pomp_evt_clear
pomp_evt_clear.restype = ctypes.c_int32
pomp_evt_clear.argtypes = [POINTER_T(struct_pomp_evt)]
pomp_timer_new = _libraries['libpomp.so'].pomp_timer_new
pomp_timer_new.restype = POINTER_T(struct_pomp_timer)
pomp_timer_new.argtypes = [POINTER_T(struct_pomp_loop), pomp_timer_cb_t, POINTER_T(None)]
pomp_timer_destroy = _libraries['libpomp.so'].pomp_timer_destroy
pomp_timer_destroy.restype = ctypes.c_int32
pomp_timer_destroy.argtypes = [POINTER_T(struct_pomp_timer)]
pomp_timer_set = _libraries['libpomp.so'].pomp_timer_set
pomp_timer_set.restype = ctypes.c_int32
pomp_timer_set.argtypes = [POINTER_T(struct_pomp_timer), uint32_t]
pomp_timer_set_periodic = _libraries['libpomp.so'].pomp_timer_set_periodic
pomp_timer_set_periodic.restype = ctypes.c_int32
pomp_timer_set_periodic.argtypes = [POINTER_T(struct_pomp_timer), uint32_t, uint32_t]
pomp_timer_clear = _libraries['libpomp.so'].pomp_timer_clear
pomp_timer_clear.restype = ctypes.c_int32
pomp_timer_clear.argtypes = [POINTER_T(struct_pomp_timer)]
pomp_addr_parse = _libraries['libpomp.so'].pomp_addr_parse
pomp_addr_parse.restype = ctypes.c_int32
pomp_addr_parse.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_sockaddr), POINTER_T(ctypes.c_uint32)]
pomp_addr_format = _libraries['libpomp.so'].pomp_addr_format
pomp_addr_format.restype = ctypes.c_int32
pomp_addr_format.argtypes = [POINTER_T(ctypes.c_char), uint32_t, POINTER_T(struct_sockaddr), uint32_t]
pomp_addr_is_unix = _libraries['libpomp.so'].pomp_addr_is_unix
pomp_addr_is_unix.restype = ctypes.c_int32
pomp_addr_is_unix.argtypes = [POINTER_T(struct_sockaddr), uint32_t]
pomp_addr_get_real_addr = _libraries['libpomp.so'].pomp_addr_get_real_addr
pomp_addr_get_real_addr.restype = ctypes.c_int32
pomp_addr_get_real_addr.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(ctypes.c_char))]
class struct_pomp_encoder(Structure):
    pass

class struct_pomp_decoder(Structure):
    pass

class struct_pomp_prot(Structure):
    pass

pomp_msg_init = _libraries['libpomp.so'].pomp_msg_init
pomp_msg_init.restype = ctypes.c_int32
pomp_msg_init.argtypes = [POINTER_T(struct_pomp_msg), uint32_t]
pomp_msg_finish = _libraries['libpomp.so'].pomp_msg_finish
pomp_msg_finish.restype = ctypes.c_int32
pomp_msg_finish.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_msg_clear = _libraries['libpomp.so'].pomp_msg_clear
pomp_msg_clear.restype = ctypes.c_int32
pomp_msg_clear.argtypes = [POINTER_T(struct_pomp_msg)]
pomp_encoder_new = _libraries['libpomp.so'].pomp_encoder_new
pomp_encoder_new.restype = POINTER_T(struct_pomp_encoder)
pomp_encoder_new.argtypes = []
pomp_encoder_destroy = _libraries['libpomp.so'].pomp_encoder_destroy
pomp_encoder_destroy.restype = ctypes.c_int32
pomp_encoder_destroy.argtypes = [POINTER_T(struct_pomp_encoder)]
pomp_encoder_init = _libraries['libpomp.so'].pomp_encoder_init
pomp_encoder_init.restype = ctypes.c_int32
pomp_encoder_init.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(struct_pomp_msg)]
pomp_encoder_clear = _libraries['libpomp.so'].pomp_encoder_clear
pomp_encoder_clear.restype = ctypes.c_int32
pomp_encoder_clear.argtypes = [POINTER_T(struct_pomp_encoder)]
pomp_encoder_write = _libraries['libpomp.so'].pomp_encoder_write
pomp_encoder_write.restype = ctypes.c_int32
pomp_encoder_write.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(ctypes.c_char)]
pomp_encoder_writev = _libraries['libpomp.so'].pomp_encoder_writev
pomp_encoder_writev.restype = ctypes.c_int32
pomp_encoder_writev.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(ctypes.c_char), va_list]
pomp_encoder_write_argv = _libraries['libpomp.so'].pomp_encoder_write_argv
pomp_encoder_write_argv.restype = ctypes.c_int32
pomp_encoder_write_argv.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(ctypes.c_char), ctypes.c_int32, POINTER_T(POINTER_T(ctypes.c_char))]
int8_t = ctypes.c_int8
pomp_encoder_write_i8 = _libraries['libpomp.so'].pomp_encoder_write_i8
pomp_encoder_write_i8.restype = ctypes.c_int32
pomp_encoder_write_i8.argtypes = [POINTER_T(struct_pomp_encoder), int8_t]
uint8_t = ctypes.c_uint8
pomp_encoder_write_u8 = _libraries['libpomp.so'].pomp_encoder_write_u8
pomp_encoder_write_u8.restype = ctypes.c_int32
pomp_encoder_write_u8.argtypes = [POINTER_T(struct_pomp_encoder), uint8_t]
int16_t = ctypes.c_int16
pomp_encoder_write_i16 = _libraries['libpomp.so'].pomp_encoder_write_i16
pomp_encoder_write_i16.restype = ctypes.c_int32
pomp_encoder_write_i16.argtypes = [POINTER_T(struct_pomp_encoder), int16_t]
uint16_t = ctypes.c_uint16
pomp_encoder_write_u16 = _libraries['libpomp.so'].pomp_encoder_write_u16
pomp_encoder_write_u16.restype = ctypes.c_int32
pomp_encoder_write_u16.argtypes = [POINTER_T(struct_pomp_encoder), uint16_t]
int32_t = ctypes.c_int32
pomp_encoder_write_i32 = _libraries['libpomp.so'].pomp_encoder_write_i32
pomp_encoder_write_i32.restype = ctypes.c_int32
pomp_encoder_write_i32.argtypes = [POINTER_T(struct_pomp_encoder), int32_t]
pomp_encoder_write_u32 = _libraries['libpomp.so'].pomp_encoder_write_u32
pomp_encoder_write_u32.restype = ctypes.c_int32
pomp_encoder_write_u32.argtypes = [POINTER_T(struct_pomp_encoder), uint32_t]
int64_t = ctypes.c_int64
pomp_encoder_write_i64 = _libraries['libpomp.so'].pomp_encoder_write_i64
pomp_encoder_write_i64.restype = ctypes.c_int32
pomp_encoder_write_i64.argtypes = [POINTER_T(struct_pomp_encoder), int64_t]
uint64_t = ctypes.c_uint64
pomp_encoder_write_u64 = _libraries['libpomp.so'].pomp_encoder_write_u64
pomp_encoder_write_u64.restype = ctypes.c_int32
pomp_encoder_write_u64.argtypes = [POINTER_T(struct_pomp_encoder), uint64_t]
pomp_encoder_write_str = _libraries['libpomp.so'].pomp_encoder_write_str
pomp_encoder_write_str.restype = ctypes.c_int32
pomp_encoder_write_str.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(ctypes.c_char)]
pomp_encoder_write_buf = _libraries['libpomp.so'].pomp_encoder_write_buf
pomp_encoder_write_buf.restype = ctypes.c_int32
pomp_encoder_write_buf.argtypes = [POINTER_T(struct_pomp_encoder), POINTER_T(None), uint32_t]
pomp_encoder_write_f32 = _libraries['libpomp.so'].pomp_encoder_write_f32
pomp_encoder_write_f32.restype = ctypes.c_int32
pomp_encoder_write_f32.argtypes = [POINTER_T(struct_pomp_encoder), ctypes.c_float]
pomp_encoder_write_f64 = _libraries['libpomp.so'].pomp_encoder_write_f64
pomp_encoder_write_f64.restype = ctypes.c_int32
pomp_encoder_write_f64.argtypes = [POINTER_T(struct_pomp_encoder), ctypes.c_double]
pomp_encoder_write_fd = _libraries['libpomp.so'].pomp_encoder_write_fd
pomp_encoder_write_fd.restype = ctypes.c_int32
pomp_encoder_write_fd.argtypes = [POINTER_T(struct_pomp_encoder), ctypes.c_int32]
pomp_decoder_new = _libraries['libpomp.so'].pomp_decoder_new
pomp_decoder_new.restype = POINTER_T(struct_pomp_decoder)
pomp_decoder_new.argtypes = []
pomp_decoder_destroy = _libraries['libpomp.so'].pomp_decoder_destroy
pomp_decoder_destroy.restype = ctypes.c_int32
pomp_decoder_destroy.argtypes = [POINTER_T(struct_pomp_decoder)]
pomp_decoder_init = _libraries['libpomp.so'].pomp_decoder_init
pomp_decoder_init.restype = ctypes.c_int32
pomp_decoder_init.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(struct_pomp_msg)]
pomp_decoder_clear = _libraries['libpomp.so'].pomp_decoder_clear
pomp_decoder_clear.restype = ctypes.c_int32
pomp_decoder_clear.argtypes = [POINTER_T(struct_pomp_decoder)]
pomp_decoder_read = _libraries['libpomp.so'].pomp_decoder_read
pomp_decoder_read.restype = ctypes.c_int32
pomp_decoder_read.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_char)]
pomp_decoder_readv = _libraries['libpomp.so'].pomp_decoder_readv
pomp_decoder_readv.restype = ctypes.c_int32
pomp_decoder_readv.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_char), va_list]
pomp_decoder_dump = _libraries['libpomp.so'].pomp_decoder_dump
pomp_decoder_dump.restype = ctypes.c_int32
pomp_decoder_dump.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_char), uint32_t]
pomp_decoder_adump = _libraries['libpomp.so'].pomp_decoder_adump
pomp_decoder_adump.restype = ctypes.c_int32
pomp_decoder_adump.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(POINTER_T(ctypes.c_char))]
pomp_decoder_read_i8 = _libraries['libpomp.so'].pomp_decoder_read_i8
pomp_decoder_read_i8.restype = ctypes.c_int32
pomp_decoder_read_i8.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_byte)]
pomp_decoder_read_u8 = _libraries['libpomp.so'].pomp_decoder_read_u8
pomp_decoder_read_u8.restype = ctypes.c_int32
pomp_decoder_read_u8.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_ubyte)]
pomp_decoder_read_i16 = _libraries['libpomp.so'].pomp_decoder_read_i16
pomp_decoder_read_i16.restype = ctypes.c_int32
pomp_decoder_read_i16.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_int16)]
pomp_decoder_read_u16 = _libraries['libpomp.so'].pomp_decoder_read_u16
pomp_decoder_read_u16.restype = ctypes.c_int32
pomp_decoder_read_u16.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_uint16)]
pomp_decoder_read_i32 = _libraries['libpomp.so'].pomp_decoder_read_i32
pomp_decoder_read_i32.restype = ctypes.c_int32
pomp_decoder_read_i32.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_int32)]
pomp_decoder_read_u32 = _libraries['libpomp.so'].pomp_decoder_read_u32
pomp_decoder_read_u32.restype = ctypes.c_int32
pomp_decoder_read_u32.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_uint32)]
pomp_decoder_read_i64 = _libraries['libpomp.so'].pomp_decoder_read_i64
pomp_decoder_read_i64.restype = ctypes.c_int32
pomp_decoder_read_i64.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_int64)]
pomp_decoder_read_u64 = _libraries['libpomp.so'].pomp_decoder_read_u64
pomp_decoder_read_u64.restype = ctypes.c_int32
pomp_decoder_read_u64.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_uint64)]
pomp_decoder_read_str = _libraries['libpomp.so'].pomp_decoder_read_str
pomp_decoder_read_str.restype = ctypes.c_int32
pomp_decoder_read_str.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(POINTER_T(ctypes.c_char))]
pomp_decoder_read_cstr = _libraries['libpomp.so'].pomp_decoder_read_cstr
pomp_decoder_read_cstr.restype = ctypes.c_int32
pomp_decoder_read_cstr.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(POINTER_T(ctypes.c_char))]
pomp_decoder_read_buf = _libraries['libpomp.so'].pomp_decoder_read_buf
pomp_decoder_read_buf.restype = ctypes.c_int32
pomp_decoder_read_buf.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint32)]
pomp_decoder_read_cbuf = _libraries['libpomp.so'].pomp_decoder_read_cbuf
pomp_decoder_read_cbuf.restype = ctypes.c_int32
pomp_decoder_read_cbuf.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint32)]
pomp_decoder_read_f32 = _libraries['libpomp.so'].pomp_decoder_read_f32
pomp_decoder_read_f32.restype = ctypes.c_int32
pomp_decoder_read_f32.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_float)]
pomp_decoder_read_f64 = _libraries['libpomp.so'].pomp_decoder_read_f64
pomp_decoder_read_f64.restype = ctypes.c_int32
pomp_decoder_read_f64.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_double)]
pomp_decoder_read_fd = _libraries['libpomp.so'].pomp_decoder_read_fd
pomp_decoder_read_fd.restype = ctypes.c_int32
pomp_decoder_read_fd.argtypes = [POINTER_T(struct_pomp_decoder), POINTER_T(ctypes.c_int32)]
pomp_prot_new = _libraries['libpomp.so'].pomp_prot_new
pomp_prot_new.restype = POINTER_T(struct_pomp_prot)
pomp_prot_new.argtypes = []
pomp_prot_destroy = _libraries['libpomp.so'].pomp_prot_destroy
pomp_prot_destroy.restype = ctypes.c_int32
pomp_prot_destroy.argtypes = [POINTER_T(struct_pomp_prot)]
pomp_prot_decode_msg = _libraries['libpomp.so'].pomp_prot_decode_msg
pomp_prot_decode_msg.restype = ctypes.c_int32
pomp_prot_decode_msg.argtypes = [POINTER_T(struct_pomp_prot), POINTER_T(None), size_t, POINTER_T(POINTER_T(struct_pomp_msg))]
pomp_prot_release_msg = _libraries['libpomp.so'].pomp_prot_release_msg
pomp_prot_release_msg.restype = ctypes.c_int32
pomp_prot_release_msg.argtypes = [POINTER_T(struct_pomp_prot), POINTER_T(struct_pomp_msg)]

# values for enumeration 'pomp_loop_impl'
pomp_loop_impl__enumvalues = {
    0: 'POMP_LOOP_IMPL_EPOLL',
    1: 'POMP_LOOP_IMPL_POLL',
    2: 'POMP_LOOP_IMPL_WIN32',
}
POMP_LOOP_IMPL_EPOLL = 0
POMP_LOOP_IMPL_POLL = 1
POMP_LOOP_IMPL_WIN32 = 2
pomp_loop_impl = ctypes.c_uint32 # enum

# values for enumeration 'pomp_timer_impl'
pomp_timer_impl__enumvalues = {
    0: 'POMP_TIMER_IMPL_TIMER_FD',
    1: 'POMP_TIMER_IMPL_KQUEUE',
    2: 'POMP_TIMER_IMPL_POSIX',
    3: 'POMP_TIMER_IMPL_WIN32',
}
POMP_TIMER_IMPL_TIMER_FD = 0
POMP_TIMER_IMPL_KQUEUE = 1
POMP_TIMER_IMPL_POSIX = 2
POMP_TIMER_IMPL_WIN32 = 3
pomp_timer_impl = ctypes.c_uint32 # enum
pomp_internal_set_loop_impl = _libraries['libpomp.so'].pomp_internal_set_loop_impl
pomp_internal_set_loop_impl.restype = ctypes.c_int32
pomp_internal_set_loop_impl.argtypes = [pomp_loop_impl]
pomp_internal_set_timer_impl = _libraries['libpomp.so'].pomp_internal_set_timer_impl
pomp_internal_set_timer_impl.restype = ctypes.c_int32
pomp_internal_set_timer_impl.argtypes = [pomp_timer_impl]
_PDRAW_H_ = True # macro
_PDRAW_DEFS_H_ = True # macro
# PDRAW_API = (None) # macro
PDRAW_API_VAR = True # macro
_MBUF_CODED_VIDEO_FRAME_H_ = True # macro
_MBUF_ANCILLARY_DATA_H_ = True # macro
# MBUF_API = (None) # macro
_MBUF_MEM_H_ = True # macro
_VDEFS_H_ = True # macro
# VDEF_API = (None) # macro

# macro function VDEF_ALIGN_MASK

# macro function VDEF_ALIGN

# macro function VDEF_IS_ALIGNED

# macro function VDEF_ROUND_UP

# macro function VDEF_ROUND

# macro function VDEF_ROUND_DOWN
VDEF_RAW_MIME_TYPE = ("video/raw") # macro
VDEF_RAW_MAX_PLANE_COUNT = (4) # macro
VDEF_RAW_FORMAT_TO_STR_FMT = ("%s/%s/%s/%u/%s/%s/%s/%u") # macro

# macro function VDEF_RAW_FORMAT_TO_STR_ARG
VDEF_CODED_FORMAT_TO_STR_FMT = ("%s/%s") # macro

# macro function VDEF_CODED_FORMAT_TO_STR_ARG
_VMETA_H_ = True # macro
# VMETA_API = (None) # macro
VMETA_API_VERSION = (2) # macro

# macro function VMETA_LOCATION_INVALID_SV_COUNT
_VMETA_FRAME_H_ = True # macro
VMETA_FRAME_MAX_SIZE = (140) # macro
VMETA_FRAME_EXT_TIMESTAMP_ID = (17713) # macro
VMETA_FRAME_EXT_FOLLOWME_ID = (17714) # macro
VMETA_FRAME_EXT_AUTOMATION_ID = (17715) # macro
VMETA_FRAME_EXT_THERMAL_ID = (17716) # macro
_VMETA_FRAME_PROTO_H_ = True # macro
VMETA_FRAME_PROTO_RTP_EXT_ID = (20578) # macro
VMETA_FRAME_PROTO_MIME_TYPE = ("application/octet-stream;type=com.parrot.videometadataproto") # macro
VMETA_FRAME_PROTO_CONTENT_ENCODING = ("") # macro
_VMETA_FRAME_V1_H_ = True # macro
VMETA_FRAME_V1_STREAMING_BASIC_SIZE = (28) # macro
VMETA_FRAME_V1_STREAMING_EXTENDED_SIZE = (56) # macro
VMETA_FRAME_V1_RECORDING_SIZE = (60) # macro
VMETA_FRAME_V1_STREAMING_ID = (20529) # macro
VMETA_FRAME_V1_RECORDING_MIME_TYPE = ("application/octet-stream;type=com.parrot.videometadata1") # macro
VMETA_FRAME_V1_RECORDING_CONTENT_ENCODING = ("") # macro
_VMETA_FRAME_V2_H_ = True # macro
VMETA_FRAME_V2_MAX_SIZE = (96) # macro
VMETA_FRAME_V2_BASE_ID = (20530) # macro
VMETA_FRAME_V2_MIME_TYPE = ("application/octet-stream;type=com.parrot.videometadata2") # macro
VMETA_FRAME_V2_CONTENT_ENCODING = ("") # macro
_VMETA_FRAME_V3_H_ = True # macro
VMETA_FRAME_V3_MAX_SIZE = (140) # macro
VMETA_FRAME_V3_BASE_ID = (20531) # macro
VMETA_FRAME_V3_MIME_TYPE = ("application/octet-stream;type=com.parrot.videometadata3") # macro
VMETA_FRAME_V3_CONTENT_ENCODING = ("") # macro
_VMETA_SESSION_H_ = True # macro
VMETA_SESSION_DATE_MAX_LEN = (26) # macro
VMETA_SESSION_LOCATION_FORMAT_CSV = ("%.8,%.8,%.3") # macro
VMETA_SESSION_LOCATION_FORMAT_ISO6709 = ("%+10.8%+11.8%+.2/") # macro
VMETA_SESSION_LOCATION_FORMAT_XYZ = ("%+08.4%+09.4/") # macro
VMETA_SESSION_LOCATION_MAX_LEN = (40) # macro
VMETA_SESSION_FOV_FORMAT = ("%.2,%.2") # macro
VMETA_SESSION_FOV_MAX_LEN = (14) # macro
VMETA_SESSION_THERMAL_ALIGNMENT_FORMAT = ("%.3,%.3,%.3") # macro
VMETA_SESSION_THERMAL_ALIGNMENT_MAX_LEN = (25) # macro
VMETA_SESSION_THERMAL_CONVERSION_FORMAT = ("%.6,%.1,%.1,%.3,%.1,%.1,%.1,%.2") # macro
VMETA_SESSION_THERMAL_CONVERSION_MAX_LEN = (100) # macro
VMETA_SESSION_THERMAL_SCALE_FACTOR_FORMAT = ("%.6") # macro
VMETA_SESSION_THERMAL_SCALE_FACTOR_MAX_LEN = (10) # macro
VMETA_STRM_SDES_KEY_MEDIA_DATE = ("media_date") # macro
VMETA_STRM_SDES_KEY_RUN_DATE = ("run_date") # macro
VMETA_STRM_SDES_KEY_RUN_ID = ("run_id") # macro
VMETA_STRM_SDES_KEY_BOOT_ID = ("boot_id") # macro
VMETA_STRM_SDES_KEY_FLIGHT_ID = ("flight_id") # macro
VMETA_STRM_SDES_KEY_CUSTOM_ID = ("custom_id") # macro
VMETA_STRM_SDES_KEY_MAKER = ("maker") # macro
VMETA_STRM_SDES_KEY_MODEL = ("model") # macro
VMETA_STRM_SDES_KEY_MODEL_ID = ("model_id") # macro
VMETA_STRM_SDES_KEY_BUILD_ID = ("build_id") # macro
VMETA_STRM_SDES_KEY_TITLE = ("title") # macro
VMETA_STRM_SDES_KEY_COMMENT = ("comment") # macro
VMETA_STRM_SDES_KEY_COPYRIGHT = ("copyright") # macro
VMETA_STRM_SDES_KEY_PICTURE_HORZ_FOV = ("picture_hfov") # macro
VMETA_STRM_SDES_KEY_PICTURE_VERT_FOV = ("picture_vfov") # macro
VMETA_STRM_SDES_KEY_PICTURE_FOV = ("picture_fov") # macro
VMETA_STRM_SDES_KEY_THERMAL_METAVERSION = ("thermal_metaversion") # macro
VMETA_STRM_SDES_KEY_THERMAL_CAMSERIAL = ("thermal_camserial") # macro
VMETA_STRM_SDES_KEY_THERMAL_ALIGNMENT = ("thermal_alignment") # macro
VMETA_STRM_SDES_KEY_THERMAL_CONV_LOW = ("thermal_conv_low") # macro
VMETA_STRM_SDES_KEY_THERMAL_CONV_HIGH = ("thermal_conv_high") # macro
VMETA_STRM_SDES_KEY_THERMAL_SCALE_FACTOR = ("thermal_scale_factor") # macro
VMETA_STRM_SDES_KEY_CAMERA_TYPE = ("camera_type") # macro
VMETA_STRM_SDES_KEY_VIDEO_MODE = ("video_mode") # macro
VMETA_STRM_SDES_KEY_VIDEO_STOP_REASON = ("video_stop_reason") # macro
VMETA_STRM_SDES_KEY_DYNAMIC_RANGE = ("dynamic_range") # macro
VMETA_STRM_SDES_KEY_TONE_MAPPING = ("tone_mapping") # macro
VMETA_STRM_SDP_KEY_MEDIA_DATE = ("X-com-parrot-media-date") # macro
VMETA_STRM_SDP_KEY_RUN_DATE = ("X-com-parrot-run-date") # macro
VMETA_STRM_SDP_KEY_RUN_ID = ("X-com-parrot-run-id") # macro
VMETA_STRM_SDP_KEY_BOOT_ID = ("X-com-parrot-boot-id") # macro
VMETA_STRM_SDP_KEY_FLIGHT_ID = ("X-com-parrot-flight-id") # macro
VMETA_STRM_SDP_KEY_CUSTOM_ID = ("X-com-parrot-custom-id") # macro
VMETA_STRM_SDP_KEY_MAKER = ("X-com-parrot-maker") # macro
VMETA_STRM_SDP_KEY_MODEL = ("X-com-parrot-model") # macro
VMETA_STRM_SDP_KEY_MODEL_ID = ("X-com-parrot-model-id") # macro
VMETA_STRM_SDP_KEY_SERIAL_NUMBER = ("X-com-parrot-serial") # macro
VMETA_STRM_SDP_KEY_BUILD_ID = ("X-com-parrot-build-id") # macro
VMETA_STRM_SDP_KEY_COMMENT = ("X-com-parrot-comment") # macro
VMETA_STRM_SDP_KEY_COPYRIGHT = ("X-com-parrot-copyright") # macro
VMETA_STRM_SDP_KEY_TAKEOFF_LOC = ("X-com-parrot-takeoff-loc") # macro
VMETA_STRM_SDP_KEY_PICTURE_FOV = ("X-com-parrot-picture-fov") # macro
VMETA_STRM_SDP_KEY_THERMAL_METAVERSION = ("X-com-parrot-thermal-metaversion") # macro
VMETA_STRM_SDP_KEY_THERMAL_CAMSERIAL = ("X-com-parrot-thermal-camserial") # macro
VMETA_STRM_SDP_KEY_THERMAL_ALIGNMENT = ("X-com-parrot-thermal-alignment") # macro
VMETA_STRM_SDP_KEY_THERMAL_CONV_LOW = ("X-com-parrot-thermal-conv-low") # macro
VMETA_STRM_SDP_KEY_THERMAL_CONV_HIGH = ("X-com-parrot-thermal-conv-high") # macro
VMETA_STRM_SDP_KEY_THERMAL_SCALE_FACTOR = ("X-com-parrot-thermal-scale-factor") # macro
VMETA_STRM_SDP_KEY_CAMERA_TYPE = ("X-com-parrot-camera-type") # macro
VMETA_STRM_SDP_KEY_VIDEO_MODE = ("X-com-parrot-video-mode") # macro
VMETA_STRM_SDP_KEY_VIDEO_STOP_REASON = ("X-com-parrot-video-stop-reason") # macro
VMETA_STRM_SDP_KEY_DYNAMIC_RANGE = ("X-com-parrot-dynamic-range") # macro
VMETA_STRM_SDP_KEY_TONE_MAPPING = ("X-com-parrot-tone-mapping") # macro
VMETA_REC_META_KEY_FRIENDLY_NAME = ("com.apple.quicktime.artist") # macro
VMETA_REC_META_KEY_TITLE = ("com.apple.quicktime.title") # macro
VMETA_REC_META_KEY_COMMENT = ("com.apple.quicktime.comment") # macro
VMETA_REC_META_KEY_COPYRIGHT = ("com.apple.quicktime.copyright") # macro
VMETA_REC_META_KEY_MEDIA_DATE = ("com.apple.quicktime.creationdate") # macro
VMETA_REC_META_KEY_TAKEOFF_LOC = ("com.apple.quicktime.location.ISO6709") # macro
VMETA_REC_META_KEY_MAKER = ("com.apple.quicktime.make") # macro
VMETA_REC_META_KEY_MODEL = ("com.apple.quicktime.model") # macro
VMETA_REC_META_KEY_SOFTWARE_VERSION = ("com.apple.quicktime.software") # macro
VMETA_REC_META_KEY_SERIAL_NUMBER = ("com.parrot.serial") # macro
VMETA_REC_META_KEY_MODEL_ID = ("com.parrot.model.id") # macro
VMETA_REC_META_KEY_BUILD_ID = ("com.parrot.build.id") # macro
VMETA_REC_META_KEY_RUN_ID = ("com.parrot.run.id") # macro
VMETA_REC_META_KEY_RUN_DATE = ("com.parrot.run.date") # macro
VMETA_REC_META_KEY_BOOT_ID = ("com.parrot.boot.id") # macro
VMETA_REC_META_KEY_FLIGHT_ID = ("com.parrot.flight.id") # macro
VMETA_REC_META_KEY_CUSTOM_ID = ("com.parrot.custom.id") # macro
VMETA_REC_META_KEY_PICTURE_HORZ_FOV = ("com.parrot.picture.hfov") # macro
VMETA_REC_META_KEY_PICTURE_VERT_FOV = ("com.parrot.picture.vfov") # macro
VMETA_REC_META_KEY_PICTURE_FOV = ("com.parrot.picture.fov") # macro
VMETA_REC_META_KEY_THERMAL_METAVERSION = ("com.parrot.thermal.metaversion") # macro
VMETA_REC_META_KEY_THERMAL_CAMSERIAL = ("com.parrot.thermal.camserial") # macro
VMETA_REC_META_KEY_THERMAL_ALIGNMENT = ("com.parrot.thermal.alignment") # macro
VMETA_REC_META_KEY_THERMAL_CONV_LOW = ("com.parrot.thermal.conv.low") # macro
VMETA_REC_META_KEY_THERMAL_CONV_HIGH = ("com.parrot.thermal.conv.high") # macro
VMETA_REC_META_KEY_THERMAL_SCALE_FACTOR = ("com.parrot.thermal.scalefactor") # macro
VMETA_REC_META_KEY_CAMERA_TYPE = ("com.parrot.camera.type") # macro
VMETA_REC_META_KEY_VIDEO_MODE = ("com.parrot.video.mode") # macro
VMETA_REC_META_KEY_VIDEO_STOP_REASON = ("com.parrot.video.stop.reason") # macro
VMETA_REC_META_KEY_DYNAMIC_RANGE = ("com.parrot.dynamic.range") # macro
VMETA_REC_META_KEY_TONE_MAPPING = ("com.parrot.tone.mapping") # macro
VMETA_REC_UDTA_KEY_FRIENDLY_NAME = ("\251ART") # macro
VMETA_REC_UDTA_KEY_TITLE = ("\251nam") # macro
VMETA_REC_UDTA_KEY_COMMENT = ("\251cmt") # macro
VMETA_REC_UDTA_KEY_COPYRIGHT = ("\251cpy") # macro
VMETA_REC_UDTA_KEY_MEDIA_DATE = ("\251day") # macro
VMETA_REC_UDTA_KEY_TAKEOFF_LOC = ("\251xyz") # macro
VMETA_REC_UDTA_KEY_MAKER = ("\251mak") # macro
VMETA_REC_UDTA_KEY_MODEL = ("\251mod") # macro
VMETA_REC_UDTA_KEY_SOFTWARE_VERSION = ("\251swr") # macro
VMETA_REC_UDTA_KEY_SERIAL_NUMBER = ("\251too") # macro
VMETA_REC_UDTA_JSON_KEY_SOFTWARE_VERSION = ("software_version") # macro
VMETA_REC_UDTA_JSON_KEY_RUN_ID = ("run_uuid") # macro
VMETA_REC_UDTA_JSON_KEY_TAKEOFF_LOC = ("takeoff_position") # macro
VMETA_REC_UDTA_JSON_KEY_MEDIA_DATE = ("media_date") # macro
VMETA_REC_UDTA_JSON_KEY_PICTURE_HORZ_FOV = ("picture_hfov") # macro
VMETA_REC_UDTA_JSON_KEY_PICTURE_VERT_FOV = ("picture_vfov") # macro
_MBUF_RAW_VIDEO_FRAME_H_ = True # macro
PDRAW_PLAY_SPEED_MAX = (1000.) # macro
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_ALL = (4294967295) # macro
struct_sockaddr._pack_ = True # source:False
struct_sockaddr._fields_ = [
    ('sa_family', ctypes.c_uint16),
    ('sa_data', ctypes.c_char * 14),
]

MBUF_ANCILLARY_KEY_USERDATA_SEI = (POINTER_T(ctypes.c_char)).in_dll(_libraries['libmedia-buffers.so'], 'MBUF_ANCILLARY_KEY_USERDATA_SEI')
class struct_mbuf_ancillary_data(Structure):
    pass

mbuf_ancillary_data_cb_t = ctypes.CFUNCTYPE(ctypes.c_bool, POINTER_T(struct_mbuf_ancillary_data), POINTER_T(None))
mbuf_ancillary_data_ref = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_ref
mbuf_ancillary_data_ref.restype = ctypes.c_int32
mbuf_ancillary_data_ref.argtypes = [POINTER_T(struct_mbuf_ancillary_data)]
mbuf_ancillary_data_unref = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_unref
mbuf_ancillary_data_unref.restype = ctypes.c_int32
mbuf_ancillary_data_unref.argtypes = [POINTER_T(struct_mbuf_ancillary_data)]
mbuf_ancillary_data_get_name = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_get_name
mbuf_ancillary_data_get_name.restype = POINTER_T(ctypes.c_char)
mbuf_ancillary_data_get_name.argtypes = [POINTER_T(struct_mbuf_ancillary_data)]
mbuf_ancillary_data_is_string = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_is_string
mbuf_ancillary_data_is_string.restype = ctypes.c_bool
mbuf_ancillary_data_is_string.argtypes = [POINTER_T(struct_mbuf_ancillary_data)]
mbuf_ancillary_data_get_string = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_get_string
mbuf_ancillary_data_get_string.restype = POINTER_T(ctypes.c_char)
mbuf_ancillary_data_get_string.argtypes = [POINTER_T(struct_mbuf_ancillary_data)]
mbuf_ancillary_data_get_buffer = _libraries['libmedia-buffers.so'].mbuf_ancillary_data_get_buffer
mbuf_ancillary_data_get_buffer.restype = POINTER_T(None)
mbuf_ancillary_data_get_buffer.argtypes = [POINTER_T(struct_mbuf_ancillary_data), POINTER_T(ctypes.c_uint64)]
class struct_mbuf_mem(Structure):
    pass

class struct_mbuf_mem_implem(Structure):
    pass

class struct_mbuf_pool(Structure):
    pass


# values for enumeration 'mbuf_pool_grow_policy'
mbuf_pool_grow_policy__enumvalues = {
    0: 'MBUF_POOL_NO_GROW',
    1: 'MBUF_POOL_GROW',
    2: 'MBUF_POOL_SMART_GROW',
    3: 'MBUF_POOL_LOW_MEM_GROW',
}
MBUF_POOL_NO_GROW = 0
MBUF_POOL_GROW = 1
MBUF_POOL_SMART_GROW = 2
MBUF_POOL_LOW_MEM_GROW = 3
mbuf_pool_grow_policy = ctypes.c_uint32 # enum
class struct_mbuf_mem_info(Structure):
    pass

struct_mbuf_mem_info._pack_ = True # source:False
struct_mbuf_mem_info._fields_ = [
    ('cookie', ctypes.c_uint64),
    ('specific', POINTER_T(None)),
]

mbuf_pool_new = _libraries['libmedia-buffers-memory.so'].mbuf_pool_new
mbuf_pool_new.restype = ctypes.c_int32
mbuf_pool_new.argtypes = [POINTER_T(struct_mbuf_mem_implem), size_t, size_t, mbuf_pool_grow_policy, size_t, POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_mbuf_pool))]
mbuf_pool_get_name = _libraries['libmedia-buffers-memory.so'].mbuf_pool_get_name
mbuf_pool_get_name.restype = POINTER_T(ctypes.c_char)
mbuf_pool_get_name.argtypes = [POINTER_T(struct_mbuf_pool)]
mbuf_pool_get = _libraries['libmedia-buffers-memory.so'].mbuf_pool_get
mbuf_pool_get.restype = ctypes.c_int32
mbuf_pool_get.argtypes = [POINTER_T(struct_mbuf_pool), POINTER_T(POINTER_T(struct_mbuf_mem))]
mbuf_pool_get_count = _libraries['libmedia-buffers-memory.so'].mbuf_pool_get_count
mbuf_pool_get_count.restype = ctypes.c_int32
mbuf_pool_get_count.argtypes = [POINTER_T(struct_mbuf_pool), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint64)]
mbuf_pool_destroy = _libraries['libmedia-buffers-memory.so'].mbuf_pool_destroy
mbuf_pool_destroy.restype = ctypes.c_int32
mbuf_pool_destroy.argtypes = [POINTER_T(struct_mbuf_pool)]
mbuf_mem_ref = _libraries['libmedia-buffers-memory.so'].mbuf_mem_ref
mbuf_mem_ref.restype = ctypes.c_int32
mbuf_mem_ref.argtypes = [POINTER_T(struct_mbuf_mem)]
mbuf_mem_unref = _libraries['libmedia-buffers-memory.so'].mbuf_mem_unref
mbuf_mem_unref.restype = ctypes.c_int32
mbuf_mem_unref.argtypes = [POINTER_T(struct_mbuf_mem)]
mbuf_mem_get_data = _libraries['libmedia-buffers-memory.so'].mbuf_mem_get_data
mbuf_mem_get_data.restype = ctypes.c_int32
mbuf_mem_get_data.argtypes = [POINTER_T(struct_mbuf_mem), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
class struct_json_object(Structure):
    pass


# values for enumeration 'vdef_frame_type'
vdef_frame_type__enumvalues = {
    0: 'VDEF_FRAME_TYPE_UNKNOWN',
    1: 'VDEF_FRAME_TYPE_RAW',
    2: 'VDEF_FRAME_TYPE_CODED',
}
VDEF_FRAME_TYPE_UNKNOWN = 0
VDEF_FRAME_TYPE_RAW = 1
VDEF_FRAME_TYPE_CODED = 2
vdef_frame_type = ctypes.c_uint32 # enum

# values for enumeration 'vdef_color_primaries'
vdef_color_primaries__enumvalues = {
    0: 'VDEF_COLOR_PRIMARIES_UNKNOWN',
    1: 'VDEF_COLOR_PRIMARIES_BT601_525',
    2: 'VDEF_COLOR_PRIMARIES_BT601_625',
    3: 'VDEF_COLOR_PRIMARIES_BT709',
    3: 'VDEF_COLOR_PRIMARIES_SRGB',
    4: 'VDEF_COLOR_PRIMARIES_BT2020',
    4: 'VDEF_COLOR_PRIMARIES_BT2100',
    5: 'VDEF_COLOR_PRIMARIES_DCI_P3',
    6: 'VDEF_COLOR_PRIMARIES_DISPLAY_P3',
    7: 'VDEF_COLOR_PRIMARIES_MAX',
}
VDEF_COLOR_PRIMARIES_UNKNOWN = 0
VDEF_COLOR_PRIMARIES_BT601_525 = 1
VDEF_COLOR_PRIMARIES_BT601_625 = 2
VDEF_COLOR_PRIMARIES_BT709 = 3
VDEF_COLOR_PRIMARIES_SRGB = 3
VDEF_COLOR_PRIMARIES_BT2020 = 4
VDEF_COLOR_PRIMARIES_BT2100 = 4
VDEF_COLOR_PRIMARIES_DCI_P3 = 5
VDEF_COLOR_PRIMARIES_DISPLAY_P3 = 6
VDEF_COLOR_PRIMARIES_MAX = 7
vdef_color_primaries = ctypes.c_uint32 # enum
class struct_vdef_color_primaries_value_0(Structure):
    pass

struct_vdef_color_primaries_value_0._pack_ = True # source:False
struct_vdef_color_primaries_value_0._fields_ = [
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
]

class struct_vdef_color_primaries_value_1(Structure):
    pass

struct_vdef_color_primaries_value_1._pack_ = True # source:False
struct_vdef_color_primaries_value_1._fields_ = [
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
]

class struct_vdef_color_primaries_value(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('color_primaries', struct_vdef_color_primaries_value_0 * 3),
        ('white_point', struct_vdef_color_primaries_value_1),
    ]

vdef_color_primaries_values = (struct_vdef_color_primaries_value * 7).in_dll(_libraries['libvideo-defs.so'], 'vdef_color_primaries_values')

# values for enumeration 'vdef_transfer_function'
vdef_transfer_function__enumvalues = {
    0: 'VDEF_TRANSFER_FUNCTION_UNKNOWN',
    1: 'VDEF_TRANSFER_FUNCTION_BT601',
    2: 'VDEF_TRANSFER_FUNCTION_BT709',
    3: 'VDEF_TRANSFER_FUNCTION_BT2020',
    4: 'VDEF_TRANSFER_FUNCTION_PQ',
    5: 'VDEF_TRANSFER_FUNCTION_HLG',
    6: 'VDEF_TRANSFER_FUNCTION_SRGB',
    7: 'VDEF_TRANSFER_FUNCTION_MAX',
}
VDEF_TRANSFER_FUNCTION_UNKNOWN = 0
VDEF_TRANSFER_FUNCTION_BT601 = 1
VDEF_TRANSFER_FUNCTION_BT709 = 2
VDEF_TRANSFER_FUNCTION_BT2020 = 3
VDEF_TRANSFER_FUNCTION_PQ = 4
VDEF_TRANSFER_FUNCTION_HLG = 5
VDEF_TRANSFER_FUNCTION_SRGB = 6
VDEF_TRANSFER_FUNCTION_MAX = 7
vdef_transfer_function = ctypes.c_uint32 # enum

# values for enumeration 'vdef_matrix_coefs'
vdef_matrix_coefs__enumvalues = {
    0: 'VDEF_MATRIX_COEFS_UNKNOWN',
    1: 'VDEF_MATRIX_COEFS_IDENTITY',
    1: 'VDEF_MATRIX_COEFS_SRGB',
    2: 'VDEF_MATRIX_COEFS_BT601_525',
    3: 'VDEF_MATRIX_COEFS_BT601_625',
    4: 'VDEF_MATRIX_COEFS_BT709',
    5: 'VDEF_MATRIX_COEFS_BT2020_NON_CST',
    5: 'VDEF_MATRIX_COEFS_BT2100',
    6: 'VDEF_MATRIX_COEFS_BT2020_CST',
    7: 'VDEF_MATRIX_COEFS_MAX',
}
VDEF_MATRIX_COEFS_UNKNOWN = 0
VDEF_MATRIX_COEFS_IDENTITY = 1
VDEF_MATRIX_COEFS_SRGB = 1
VDEF_MATRIX_COEFS_BT601_525 = 2
VDEF_MATRIX_COEFS_BT601_625 = 3
VDEF_MATRIX_COEFS_BT709 = 4
VDEF_MATRIX_COEFS_BT2020_NON_CST = 5
VDEF_MATRIX_COEFS_BT2100 = 5
VDEF_MATRIX_COEFS_BT2020_CST = 6
VDEF_MATRIX_COEFS_MAX = 7
vdef_matrix_coefs = ctypes.c_uint32 # enum

# values for enumeration 'vdef_dynamic_range'
vdef_dynamic_range__enumvalues = {
    0: 'VDEF_DYNAMIC_RANGE_UNKNOWN',
    1: 'VDEF_DYNAMIC_RANGE_SDR',
    2: 'VDEF_DYNAMIC_RANGE_HDR8',
    3: 'VDEF_DYNAMIC_RANGE_HDR10',
    4: 'VDEF_DYNAMIC_RANGE_MAX',
}
VDEF_DYNAMIC_RANGE_UNKNOWN = 0
VDEF_DYNAMIC_RANGE_SDR = 1
VDEF_DYNAMIC_RANGE_HDR8 = 2
VDEF_DYNAMIC_RANGE_HDR10 = 3
VDEF_DYNAMIC_RANGE_MAX = 4
vdef_dynamic_range = ctypes.c_uint32 # enum

# values for enumeration 'vdef_tone_mapping'
vdef_tone_mapping__enumvalues = {
    0: 'VDEF_TONE_MAPPING_UNKNOWN',
    1: 'VDEF_TONE_MAPPING_STANDARD',
    2: 'VDEF_TONE_MAPPING_P_LOG',
    3: 'VDEF_TONE_MAPPING_MAX',
}
VDEF_TONE_MAPPING_UNKNOWN = 0
VDEF_TONE_MAPPING_STANDARD = 1
VDEF_TONE_MAPPING_P_LOG = 2
VDEF_TONE_MAPPING_MAX = 3
vdef_tone_mapping = ctypes.c_uint32 # enum
vdef_rgb_to_yuv_norm_offset = (ctypes.c_float * 3 * 2 * 7).in_dll(_libraries['libvideo-defs.so'], 'vdef_rgb_to_yuv_norm_offset')
vdef_rgb_to_yuv_norm_matrix = (ctypes.c_float * 9 * 2 * 7).in_dll(_libraries['libvideo-defs.so'], 'vdef_rgb_to_yuv_norm_matrix')
vdef_yuv_to_rgb_norm_offset = (ctypes.c_float * 3 * 2 * 7).in_dll(_libraries['libvideo-defs.so'], 'vdef_yuv_to_rgb_norm_offset')
vdef_yuv_to_rgb_norm_matrix = (ctypes.c_float * 9 * 2 * 7).in_dll(_libraries['libvideo-defs.so'], 'vdef_yuv_to_rgb_norm_matrix')
vdef_bt709_to_bt2020_matrix = (ctypes.c_float * 9).in_dll(_libraries['libvideo-defs.so'], 'vdef_bt709_to_bt2020_matrix')
vdef_bt2020_to_bt709_matrix = (ctypes.c_float * 9).in_dll(_libraries['libvideo-defs.so'], 'vdef_bt2020_to_bt709_matrix')

# values for enumeration 'vdef_frame_flag'
vdef_frame_flag__enumvalues = {
    0: 'VDEF_FRAME_FLAG_NONE',
    1: 'VDEF_FRAME_FLAG_NOT_MAPPED',
    2: 'VDEF_FRAME_FLAG_DATA_ERROR',
    4: 'VDEF_FRAME_FLAG_NO_CACHE_INVALIDATE',
    8: 'VDEF_FRAME_FLAG_NO_CACHE_CLEAN',
    16: 'VDEF_FRAME_FLAG_VISUAL_ERROR',
    32: 'VDEF_FRAME_FLAG_SILENT',
    64: 'VDEF_FRAME_FLAG_USES_LTR',
}
VDEF_FRAME_FLAG_NONE = 0
VDEF_FRAME_FLAG_NOT_MAPPED = 1
VDEF_FRAME_FLAG_DATA_ERROR = 2
VDEF_FRAME_FLAG_NO_CACHE_INVALIDATE = 4
VDEF_FRAME_FLAG_NO_CACHE_CLEAN = 8
VDEF_FRAME_FLAG_VISUAL_ERROR = 16
VDEF_FRAME_FLAG_SILENT = 32
VDEF_FRAME_FLAG_USES_LTR = 64
vdef_frame_flag = ctypes.c_uint32 # enum
class struct_vdef_dim(Structure):
    pass

struct_vdef_dim._pack_ = True # source:False
struct_vdef_dim._fields_ = [
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
]

class struct_vdef_rect(Structure):
    pass

struct_vdef_rect._pack_ = True # source:False
struct_vdef_rect._fields_ = [
    ('left', ctypes.c_int32),
    ('top', ctypes.c_int32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
]

class struct_vdef_frac(Structure):
    pass

struct_vdef_frac._pack_ = True # source:False
struct_vdef_frac._fields_ = [
    ('num', ctypes.c_uint32),
    ('den', ctypes.c_uint32),
]

class struct_vdef_format_info_0(Structure):
    pass

struct_vdef_format_info_0._pack_ = True # source:False
struct_vdef_format_info_0._fields_ = [
    ('display_primaries', vdef_color_primaries),
    ('display_primaries_val', struct_vdef_color_primaries_value),
    ('max_display_mastering_luminance', ctypes.c_float),
    ('min_display_mastering_luminance', ctypes.c_float),
]

class struct_vdef_format_info_1(Structure):
    pass

struct_vdef_format_info_1._pack_ = True # source:False
struct_vdef_format_info_1._fields_ = [
    ('max_cll', ctypes.c_uint32),
    ('max_fall', ctypes.c_uint32),
]

class struct_vdef_format_info(Structure):
    pass

struct_vdef_format_info._pack_ = True # source:False
struct_vdef_format_info._fields_ = [
    ('framerate', struct_vdef_frac),
    ('bit_depth', ctypes.c_uint32),
    ('full_range', ctypes.c_bool),
    ('PADDING_0', ctypes.c_ubyte * 3),
    ('color_primaries', vdef_color_primaries),
    ('transfer_function', vdef_transfer_function),
    ('matrix_coefs', vdef_matrix_coefs),
    ('dynamic_range', vdef_dynamic_range),
    ('tone_mapping', vdef_tone_mapping),
    ('resolution', struct_vdef_dim),
    ('sar', struct_vdef_dim),
    ('mdcv', struct_vdef_format_info_0),
    ('cll', struct_vdef_format_info_1),
]

class struct_vdef_frame_info(Structure):
    pass

struct_vdef_frame_info._pack_ = True # source:False
struct_vdef_frame_info._fields_ = [
    ('timestamp', ctypes.c_uint64),
    ('timescale', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('capture_timestamp', ctypes.c_uint64),
    ('index', ctypes.c_uint32),
    ('bit_depth', ctypes.c_uint32),
    ('full_range', ctypes.c_bool),
    ('PADDING_1', ctypes.c_ubyte * 3),
    ('color_primaries', vdef_color_primaries),
    ('transfer_function', vdef_transfer_function),
    ('matrix_coefs', vdef_matrix_coefs),
    ('dynamic_range', vdef_dynamic_range),
    ('tone_mapping', vdef_tone_mapping),
    ('resolution', struct_vdef_dim),
    ('sar', struct_vdef_dim),
    ('flags', ctypes.c_uint64),
]


# values for enumeration 'vdef_raw_pix_format'
vdef_raw_pix_format__enumvalues = {
    0: 'VDEF_RAW_PIX_FORMAT_UNKNOWN',
    0: 'VDEF_RAW_PIX_FORMAT_RAW',
    1: 'VDEF_RAW_PIX_FORMAT_YUV420',
    2: 'VDEF_RAW_PIX_FORMAT_YUV422',
    3: 'VDEF_RAW_PIX_FORMAT_YUV444',
    4: 'VDEF_RAW_PIX_FORMAT_GRAY',
    5: 'VDEF_RAW_PIX_FORMAT_RGB24',
    6: 'VDEF_RAW_PIX_FORMAT_RGBA32',
    7: 'VDEF_RAW_PIX_FORMAT_BAYER',
    8: 'VDEF_RAW_PIX_FORMAT_DEPTH',
    9: 'VDEF_RAW_PIX_FORMAT_DEPTH_FLOAT',
}
VDEF_RAW_PIX_FORMAT_UNKNOWN = 0
VDEF_RAW_PIX_FORMAT_RAW = 0
VDEF_RAW_PIX_FORMAT_YUV420 = 1
VDEF_RAW_PIX_FORMAT_YUV422 = 2
VDEF_RAW_PIX_FORMAT_YUV444 = 3
VDEF_RAW_PIX_FORMAT_GRAY = 4
VDEF_RAW_PIX_FORMAT_RGB24 = 5
VDEF_RAW_PIX_FORMAT_RGBA32 = 6
VDEF_RAW_PIX_FORMAT_BAYER = 7
VDEF_RAW_PIX_FORMAT_DEPTH = 8
VDEF_RAW_PIX_FORMAT_DEPTH_FLOAT = 9
vdef_raw_pix_format = ctypes.c_uint32 # enum

# values for enumeration 'vdef_raw_pix_order'
vdef_raw_pix_order__enumvalues = {
    0: 'VDEF_RAW_PIX_ORDER_UNKNOWN',
    1: 'VDEF_RAW_PIX_ORDER_ABCD',
    1: 'VDEF_RAW_PIX_ORDER_ABC',
    1: 'VDEF_RAW_PIX_ORDER_AB',
    1: 'VDEF_RAW_PIX_ORDER_A',
    1: 'VDEF_RAW_PIX_ORDER_RGB',
    1: 'VDEF_RAW_PIX_ORDER_RGBA',
    1: 'VDEF_RAW_PIX_ORDER_YUYV',
    1: 'VDEF_RAW_PIX_ORDER_YUV',
    1: 'VDEF_RAW_PIX_ORDER_RGGB',
    2: 'VDEF_RAW_PIX_ORDER_ABDC',
    3: 'VDEF_RAW_PIX_ORDER_ACBD',
    3: 'VDEF_RAW_PIX_ORDER_ACB',
    3: 'VDEF_RAW_PIX_ORDER_YVYU',
    3: 'VDEF_RAW_PIX_ORDER_YVU',
    4: 'VDEF_RAW_PIX_ORDER_ACDB',
    5: 'VDEF_RAW_PIX_ORDER_ADBC',
    6: 'VDEF_RAW_PIX_ORDER_ADCB',
    7: 'VDEF_RAW_PIX_ORDER_BACD',
    7: 'VDEF_RAW_PIX_ORDER_BAC',
    7: 'VDEF_RAW_PIX_ORDER_BA',
    8: 'VDEF_RAW_PIX_ORDER_BADC',
    8: 'VDEF_RAW_PIX_ORDER_GRBG',
    9: 'VDEF_RAW_PIX_ORDER_BCAD',
    9: 'VDEF_RAW_PIX_ORDER_BCA',
    10: 'VDEF_RAW_PIX_ORDER_BCDA',
    11: 'VDEF_RAW_PIX_ORDER_BDAC',
    12: 'VDEF_RAW_PIX_ORDER_BDCA',
    13: 'VDEF_RAW_PIX_ORDER_CABD',
    13: 'VDEF_RAW_PIX_ORDER_CAB',
    14: 'VDEF_RAW_PIX_ORDER_CADB',
    15: 'VDEF_RAW_PIX_ORDER_CBAD',
    15: 'VDEF_RAW_PIX_ORDER_CBA',
    15: 'VDEF_RAW_PIX_ORDER_BGR',
    15: 'VDEF_RAW_PIX_ORDER_BGRA',
    16: 'VDEF_RAW_PIX_ORDER_CBDA',
    17: 'VDEF_RAW_PIX_ORDER_CDAB',
    17: 'VDEF_RAW_PIX_ORDER_GBRG',
    18: 'VDEF_RAW_PIX_ORDER_CDBA',
    19: 'VDEF_RAW_PIX_ORDER_DABC',
    20: 'VDEF_RAW_PIX_ORDER_DACB',
    21: 'VDEF_RAW_PIX_ORDER_DBAC',
    22: 'VDEF_RAW_PIX_ORDER_DBCA',
    23: 'VDEF_RAW_PIX_ORDER_DCAB',
    24: 'VDEF_RAW_PIX_ORDER_DCBA',
    24: 'VDEF_RAW_PIX_ORDER_ABGR',
    24: 'VDEF_RAW_PIX_ORDER_BGGR',
}
VDEF_RAW_PIX_ORDER_UNKNOWN = 0
VDEF_RAW_PIX_ORDER_ABCD = 1
VDEF_RAW_PIX_ORDER_ABC = 1
VDEF_RAW_PIX_ORDER_AB = 1
VDEF_RAW_PIX_ORDER_A = 1
VDEF_RAW_PIX_ORDER_RGB = 1
VDEF_RAW_PIX_ORDER_RGBA = 1
VDEF_RAW_PIX_ORDER_YUYV = 1
VDEF_RAW_PIX_ORDER_YUV = 1
VDEF_RAW_PIX_ORDER_RGGB = 1
VDEF_RAW_PIX_ORDER_ABDC = 2
VDEF_RAW_PIX_ORDER_ACBD = 3
VDEF_RAW_PIX_ORDER_ACB = 3
VDEF_RAW_PIX_ORDER_YVYU = 3
VDEF_RAW_PIX_ORDER_YVU = 3
VDEF_RAW_PIX_ORDER_ACDB = 4
VDEF_RAW_PIX_ORDER_ADBC = 5
VDEF_RAW_PIX_ORDER_ADCB = 6
VDEF_RAW_PIX_ORDER_BACD = 7
VDEF_RAW_PIX_ORDER_BAC = 7
VDEF_RAW_PIX_ORDER_BA = 7
VDEF_RAW_PIX_ORDER_BADC = 8
VDEF_RAW_PIX_ORDER_GRBG = 8
VDEF_RAW_PIX_ORDER_BCAD = 9
VDEF_RAW_PIX_ORDER_BCA = 9
VDEF_RAW_PIX_ORDER_BCDA = 10
VDEF_RAW_PIX_ORDER_BDAC = 11
VDEF_RAW_PIX_ORDER_BDCA = 12
VDEF_RAW_PIX_ORDER_CABD = 13
VDEF_RAW_PIX_ORDER_CAB = 13
VDEF_RAW_PIX_ORDER_CADB = 14
VDEF_RAW_PIX_ORDER_CBAD = 15
VDEF_RAW_PIX_ORDER_CBA = 15
VDEF_RAW_PIX_ORDER_BGR = 15
VDEF_RAW_PIX_ORDER_BGRA = 15
VDEF_RAW_PIX_ORDER_CBDA = 16
VDEF_RAW_PIX_ORDER_CDAB = 17
VDEF_RAW_PIX_ORDER_GBRG = 17
VDEF_RAW_PIX_ORDER_CDBA = 18
VDEF_RAW_PIX_ORDER_DABC = 19
VDEF_RAW_PIX_ORDER_DACB = 20
VDEF_RAW_PIX_ORDER_DBAC = 21
VDEF_RAW_PIX_ORDER_DBCA = 22
VDEF_RAW_PIX_ORDER_DCAB = 23
VDEF_RAW_PIX_ORDER_DCBA = 24
VDEF_RAW_PIX_ORDER_ABGR = 24
VDEF_RAW_PIX_ORDER_BGGR = 24
vdef_raw_pix_order = ctypes.c_uint32 # enum

# values for enumeration 'vdef_raw_pix_layout'
vdef_raw_pix_layout__enumvalues = {
    0: 'VDEF_RAW_PIX_LAYOUT_UNKNOWN',
    1: 'VDEF_RAW_PIX_LAYOUT_LINEAR',
    2: 'VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16',
    3: 'VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16_COMPRESSED',
}
VDEF_RAW_PIX_LAYOUT_UNKNOWN = 0
VDEF_RAW_PIX_LAYOUT_LINEAR = 1
VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16 = 2
VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16_COMPRESSED = 3
vdef_raw_pix_layout = ctypes.c_uint32 # enum

# values for enumeration 'vdef_raw_data_layout'
vdef_raw_data_layout__enumvalues = {
    0: 'VDEF_RAW_DATA_LAYOUT_UNKNOWN',
    1: 'VDEF_RAW_DATA_LAYOUT_PACKED',
    1: 'VDEF_RAW_DATA_LAYOUT_RGB24',
    1: 'VDEF_RAW_DATA_LAYOUT_RGBA32',
    2: 'VDEF_RAW_DATA_LAYOUT_PLANAR',
    2: 'VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B',
    2: 'VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B_A',
    2: 'VDEF_RAW_DATA_LAYOUT_PLANAR_Y_U_V',
    3: 'VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR',
    3: 'VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR_Y_UV',
    4: 'VDEF_RAW_DATA_LAYOUT_INTERLEAVED',
    4: 'VDEF_RAW_DATA_LAYOUT_YUYV',
    5: 'VDEF_RAW_DATA_LAYOUT_OPAQUE',
}
VDEF_RAW_DATA_LAYOUT_UNKNOWN = 0
VDEF_RAW_DATA_LAYOUT_PACKED = 1
VDEF_RAW_DATA_LAYOUT_RGB24 = 1
VDEF_RAW_DATA_LAYOUT_RGBA32 = 1
VDEF_RAW_DATA_LAYOUT_PLANAR = 2
VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B = 2
VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B_A = 2
VDEF_RAW_DATA_LAYOUT_PLANAR_Y_U_V = 2
VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR = 3
VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR_Y_UV = 3
VDEF_RAW_DATA_LAYOUT_INTERLEAVED = 4
VDEF_RAW_DATA_LAYOUT_YUYV = 4
VDEF_RAW_DATA_LAYOUT_OPAQUE = 5
vdef_raw_data_layout = ctypes.c_uint32 # enum
class struct_vdef_raw_format(Structure):
    pass

struct_vdef_raw_format._pack_ = True # source:False
struct_vdef_raw_format._fields_ = [
    ('pix_format', vdef_raw_pix_format),
    ('pix_order', vdef_raw_pix_order),
    ('pix_layout', vdef_raw_pix_layout),
    ('pix_size', ctypes.c_uint32),
    ('data_layout', vdef_raw_data_layout),
    ('data_pad_low', ctypes.c_bool),
    ('data_little_endian', ctypes.c_bool),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('data_size', ctypes.c_uint32),
]

vdef_raw8 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw8')
vdef_raw10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw10_packed')
vdef_raw10 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw10')
vdef_raw12_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw12_packed')
vdef_raw12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw12')
vdef_raw14_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw14_packed')
vdef_raw14 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw14')
vdef_raw16 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw16')
vdef_raw32 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_raw32')
vdef_gray = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_gray')
vdef_gray16 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_gray16')
vdef_i420 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_i420')
vdef_i420_10_16le = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_i420_10_16le')
vdef_i420_10_16be = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_i420_10_16be')
vdef_i420_10_16le_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_i420_10_16le_high')
vdef_i420_10_16be_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_i420_10_16be_high')
vdef_yv12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_yv12')
vdef_yv12_10_16le = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_yv12_10_16le')
vdef_yv12_10_16be = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_yv12_10_16be')
vdef_yv12_10_16le_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_yv12_10_16le_high')
vdef_yv12_10_16be_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_yv12_10_16be_high')
vdef_nv12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12')
vdef_nv12_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12_10_packed')
vdef_nv12_10_16be = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12_10_16be')
vdef_nv12_10_16le = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12_10_16le')
vdef_nv12_10_16be_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12_10_16be_high')
vdef_nv12_10_16le_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv12_10_16le_high')
vdef_nv21 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21')
vdef_nv21_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_10_packed')
vdef_nv21_10_16le = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_10_16le')
vdef_nv21_10_16be = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_10_16be')
vdef_nv21_10_16le_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_10_16le_high')
vdef_nv21_10_16be_high = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_10_16be_high')
vdef_rgb = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_rgb')
vdef_bgr = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bgr')
vdef_rgba = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_rgba')
vdef_bgra = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bgra')
vdef_abgr = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_abgr')
vdef_bayer_rggb = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb')
vdef_bayer_bggr = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr')
vdef_bayer_grbg = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg')
vdef_bayer_gbrg = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg')
vdef_bayer_rggb_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_10_packed')
vdef_bayer_bggr_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_10_packed')
vdef_bayer_grbg_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_10_packed')
vdef_bayer_gbrg_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_10_packed')
vdef_bayer_rggb_10 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_10')
vdef_bayer_bggr_10 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_10')
vdef_bayer_grbg_10 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_10')
vdef_bayer_gbrg_10 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_10')
vdef_bayer_rggb_12_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_12_packed')
vdef_bayer_bggr_12_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_12_packed')
vdef_bayer_grbg_12_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_12_packed')
vdef_bayer_gbrg_12_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_12_packed')
vdef_bayer_rggb_12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_12')
vdef_bayer_bggr_12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_12')
vdef_bayer_grbg_12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_12')
vdef_bayer_gbrg_12 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_12')
vdef_bayer_rggb_14_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_14_packed')
vdef_bayer_bggr_14_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_14_packed')
vdef_bayer_grbg_14_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_14_packed')
vdef_bayer_gbrg_14_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_14_packed')
vdef_bayer_rggb_14 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_rggb_14')
vdef_bayer_bggr_14 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_bggr_14')
vdef_bayer_grbg_14 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_grbg_14')
vdef_bayer_gbrg_14 = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_bayer_gbrg_14')
vdef_nv21_hisi_tile = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_hisi_tile')
vdef_nv21_hisi_tile_compressed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_hisi_tile_compressed')
vdef_nv21_hisi_tile_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_hisi_tile_10_packed')
vdef_nv21_hisi_tile_compressed_10_packed = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_nv21_hisi_tile_compressed_10_packed')
vdef_mmal_opaque = (struct_vdef_raw_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_mmal_opaque')
class struct_vdef_raw_frame(Structure):
    pass

struct_vdef_raw_frame._pack_ = True # source:False
struct_vdef_raw_frame._fields_ = [
    ('format', struct_vdef_raw_format),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('info', struct_vdef_frame_info),
    ('plane_stride', ctypes.c_uint64 * 4),
]


# values for enumeration 'vdef_encoding'
vdef_encoding__enumvalues = {
    0: 'VDEF_ENCODING_UNKNOWN',
    1: 'VDEF_ENCODING_JPEG',
    1: 'VDEF_ENCODING_MJPEG',
    2: 'VDEF_ENCODING_H264',
    2: 'VDEF_ENCODING_AVC',
    3: 'VDEF_ENCODING_H265',
    3: 'VDEF_ENCODING_HEVC',
}
VDEF_ENCODING_UNKNOWN = 0
VDEF_ENCODING_JPEG = 1
VDEF_ENCODING_MJPEG = 1
VDEF_ENCODING_H264 = 2
VDEF_ENCODING_AVC = 2
VDEF_ENCODING_H265 = 3
VDEF_ENCODING_HEVC = 3
vdef_encoding = ctypes.c_uint32 # enum

# values for enumeration 'vdef_coded_data_format'
vdef_coded_data_format__enumvalues = {
    0: 'VDEF_CODED_DATA_FORMAT_UNKNOWN',
    1: 'VDEF_CODED_DATA_FORMAT_JFIF',
    2: 'VDEF_CODED_DATA_FORMAT_RAW_NALU',
    3: 'VDEF_CODED_DATA_FORMAT_BYTE_STREAM',
    4: 'VDEF_CODED_DATA_FORMAT_AVCC',
    4: 'VDEF_CODED_DATA_FORMAT_HVCC',
}
VDEF_CODED_DATA_FORMAT_UNKNOWN = 0
VDEF_CODED_DATA_FORMAT_JFIF = 1
VDEF_CODED_DATA_FORMAT_RAW_NALU = 2
VDEF_CODED_DATA_FORMAT_BYTE_STREAM = 3
VDEF_CODED_DATA_FORMAT_AVCC = 4
VDEF_CODED_DATA_FORMAT_HVCC = 4
vdef_coded_data_format = ctypes.c_uint32 # enum
class struct_vdef_coded_format(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('encoding', vdef_encoding),
        ('data_format', vdef_coded_data_format),
    ]

vdef_h264_raw_nalu = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h264_raw_nalu')
vdef_h264_byte_stream = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h264_byte_stream')
vdef_h264_avcc = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h264_avcc')
vdef_h265_raw_nalu = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h265_raw_nalu')
vdef_h265_byte_stream = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h265_byte_stream')
vdef_h265_hvcc = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_h265_hvcc')
vdef_jpeg_jfif = (struct_vdef_coded_format).in_dll(_libraries['libvideo-defs.so'], 'vdef_jpeg_jfif')

# values for enumeration 'vdef_coded_frame_type'
vdef_coded_frame_type__enumvalues = {
    0: 'VDEF_CODED_FRAME_TYPE_UNKNOWN',
    1: 'VDEF_CODED_FRAME_TYPE_NOT_CODED',
    2: 'VDEF_CODED_FRAME_TYPE_IDR',
    2: 'VDEF_CODED_FRAME_TYPE_CODED',
    3: 'VDEF_CODED_FRAME_TYPE_I',
    4: 'VDEF_CODED_FRAME_TYPE_P_IR_START',
    5: 'VDEF_CODED_FRAME_TYPE_P',
    6: 'VDEF_CODED_FRAME_TYPE_P_NON_REF',
}
VDEF_CODED_FRAME_TYPE_UNKNOWN = 0
VDEF_CODED_FRAME_TYPE_NOT_CODED = 1
VDEF_CODED_FRAME_TYPE_IDR = 2
VDEF_CODED_FRAME_TYPE_CODED = 2
VDEF_CODED_FRAME_TYPE_I = 3
VDEF_CODED_FRAME_TYPE_P_IR_START = 4
VDEF_CODED_FRAME_TYPE_P = 5
VDEF_CODED_FRAME_TYPE_P_NON_REF = 6
vdef_coded_frame_type = ctypes.c_uint32 # enum

# values for enumeration 'h264_nalu_type'
h264_nalu_type__enumvalues = {
    0: 'H264_NALU_TYPE_UNKNOWN',
    1: 'H264_NALU_TYPE_SLICE',
    2: 'H264_NALU_TYPE_SLICE_DPA',
    3: 'H264_NALU_TYPE_SLICE_DPB',
    4: 'H264_NALU_TYPE_SLICE_DPC',
    5: 'H264_NALU_TYPE_SLICE_IDR',
    6: 'H264_NALU_TYPE_SEI',
    7: 'H264_NALU_TYPE_SPS',
    8: 'H264_NALU_TYPE_PPS',
    9: 'H264_NALU_TYPE_AUD',
    10: 'H264_NALU_TYPE_END_OF_SEQ',
    11: 'H264_NALU_TYPE_END_OF_STREAM',
    12: 'H264_NALU_TYPE_FILLER',
}
H264_NALU_TYPE_UNKNOWN = 0
H264_NALU_TYPE_SLICE = 1
H264_NALU_TYPE_SLICE_DPA = 2
H264_NALU_TYPE_SLICE_DPB = 3
H264_NALU_TYPE_SLICE_DPC = 4
H264_NALU_TYPE_SLICE_IDR = 5
H264_NALU_TYPE_SEI = 6
H264_NALU_TYPE_SPS = 7
H264_NALU_TYPE_PPS = 8
H264_NALU_TYPE_AUD = 9
H264_NALU_TYPE_END_OF_SEQ = 10
H264_NALU_TYPE_END_OF_STREAM = 11
H264_NALU_TYPE_FILLER = 12
h264_nalu_type = ctypes.c_uint32 # enum

# values for enumeration 'h264_slice_type'
h264_slice_type__enumvalues = {
    -1: 'H264_SLICE_TYPE_UNKNOWN',
    0: 'H264_SLICE_TYPE_P',
    1: 'H264_SLICE_TYPE_B',
    2: 'H264_SLICE_TYPE_I',
    3: 'H264_SLICE_TYPE_SP',
    4: 'H264_SLICE_TYPE_SI',
}
H264_SLICE_TYPE_UNKNOWN = -1
H264_SLICE_TYPE_P = 0
H264_SLICE_TYPE_B = 1
H264_SLICE_TYPE_I = 2
H264_SLICE_TYPE_SP = 3
H264_SLICE_TYPE_SI = 4
h264_slice_type = ctypes.c_int32 # enum
class struct_vdef_nalu_0_0(Structure):
    pass

struct_vdef_nalu_0_0._pack_ = True # source:False
struct_vdef_nalu_0_0._fields_ = [
    ('type', h264_nalu_type),
    ('slice_type', h264_slice_type),
    ('slice_mb_count', ctypes.c_uint32),
]


# values for enumeration 'h265_nalu_type'
h265_nalu_type__enumvalues = {
    -1: 'H265_NALU_TYPE_UNKNOWN',
    0: 'H265_NALU_TYPE_TRAIL_N',
    1: 'H265_NALU_TYPE_TRAIL_R',
    2: 'H265_NALU_TYPE_TSA_N',
    3: 'H265_NALU_TYPE_TSA_R',
    4: 'H265_NALU_TYPE_STSA_N',
    5: 'H265_NALU_TYPE_STSA_R',
    6: 'H265_NALU_TYPE_RADL_N',
    7: 'H265_NALU_TYPE_RADL_R',
    8: 'H265_NALU_TYPE_RASL_N',
    9: 'H265_NALU_TYPE_RASL_R',
    10: 'H265_NALU_TYPE_RSV_VCL_N10',
    11: 'H265_NALU_TYPE_RSV_VCL_R11',
    12: 'H265_NALU_TYPE_RSV_VCL_N12',
    13: 'H265_NALU_TYPE_RSV_VCL_R13',
    14: 'H265_NALU_TYPE_RSV_VCL_N14',
    15: 'H265_NALU_TYPE_RSV_VCL_R15',
    16: 'H265_NALU_TYPE_BLA_W_LP',
    17: 'H265_NALU_TYPE_BLA_W_RADL',
    18: 'H265_NALU_TYPE_BLA_N_LP',
    19: 'H265_NALU_TYPE_IDR_W_RADL',
    20: 'H265_NALU_TYPE_IDR_N_LP',
    21: 'H265_NALU_TYPE_CRA_NUT',
    22: 'H265_NALU_TYPE_RSV_IRAP_VCL22',
    23: 'H265_NALU_TYPE_RSV_IRAP_VCL23',
    24: 'H265_NALU_TYPE_RSV_VCL24',
    25: 'H265_NALU_TYPE_RSV_VCL25',
    26: 'H265_NALU_TYPE_RSV_VCL26',
    27: 'H265_NALU_TYPE_RSV_VCL27',
    28: 'H265_NALU_TYPE_RSV_VCL28',
    29: 'H265_NALU_TYPE_RSV_VCL29',
    30: 'H265_NALU_TYPE_RSV_VCL30',
    31: 'H265_NALU_TYPE_RSV_VCL31',
    32: 'H265_NALU_TYPE_VPS_NUT',
    33: 'H265_NALU_TYPE_SPS_NUT',
    34: 'H265_NALU_TYPE_PPS_NUT',
    35: 'H265_NALU_TYPE_AUD_NUT',
    36: 'H265_NALU_TYPE_EOS_NUT',
    37: 'H265_NALU_TYPE_EOB_NUT',
    38: 'H265_NALU_TYPE_FD_NUT',
    39: 'H265_NALU_TYPE_PREFIX_SEI_NUT',
    40: 'H265_NALU_TYPE_SUFFIX_SEI_NUT',
    41: 'H265_NALU_TYPE_RSV_NVCL41',
    42: 'H265_NALU_TYPE_RSV_NVCL42',
    43: 'H265_NALU_TYPE_RSV_NVCL43',
    44: 'H265_NALU_TYPE_RSV_NVCL44',
    45: 'H265_NALU_TYPE_RSV_NVCL45',
    46: 'H265_NALU_TYPE_RSV_NVCL46',
    47: 'H265_NALU_TYPE_RSV_NVCL47',
    48: 'H265_NALU_TYPE_UNSPEC48',
    49: 'H265_NALU_TYPE_UNSPEC49',
    50: 'H265_NALU_TYPE_UNSPEC50',
    51: 'H265_NALU_TYPE_UNSPEC51',
    52: 'H265_NALU_TYPE_UNSPEC52',
    53: 'H265_NALU_TYPE_UNSPEC53',
    54: 'H265_NALU_TYPE_UNSPEC54',
    55: 'H265_NALU_TYPE_UNSPEC55',
    56: 'H265_NALU_TYPE_UNSPEC56',
    57: 'H265_NALU_TYPE_UNSPEC57',
    58: 'H265_NALU_TYPE_UNSPEC58',
    59: 'H265_NALU_TYPE_UNSPEC59',
    60: 'H265_NALU_TYPE_UNSPEC60',
    61: 'H265_NALU_TYPE_UNSPEC61',
    62: 'H265_NALU_TYPE_UNSPEC62',
    63: 'H265_NALU_TYPE_UNSPEC63',
}
H265_NALU_TYPE_UNKNOWN = -1
H265_NALU_TYPE_TRAIL_N = 0
H265_NALU_TYPE_TRAIL_R = 1
H265_NALU_TYPE_TSA_N = 2
H265_NALU_TYPE_TSA_R = 3
H265_NALU_TYPE_STSA_N = 4
H265_NALU_TYPE_STSA_R = 5
H265_NALU_TYPE_RADL_N = 6
H265_NALU_TYPE_RADL_R = 7
H265_NALU_TYPE_RASL_N = 8
H265_NALU_TYPE_RASL_R = 9
H265_NALU_TYPE_RSV_VCL_N10 = 10
H265_NALU_TYPE_RSV_VCL_R11 = 11
H265_NALU_TYPE_RSV_VCL_N12 = 12
H265_NALU_TYPE_RSV_VCL_R13 = 13
H265_NALU_TYPE_RSV_VCL_N14 = 14
H265_NALU_TYPE_RSV_VCL_R15 = 15
H265_NALU_TYPE_BLA_W_LP = 16
H265_NALU_TYPE_BLA_W_RADL = 17
H265_NALU_TYPE_BLA_N_LP = 18
H265_NALU_TYPE_IDR_W_RADL = 19
H265_NALU_TYPE_IDR_N_LP = 20
H265_NALU_TYPE_CRA_NUT = 21
H265_NALU_TYPE_RSV_IRAP_VCL22 = 22
H265_NALU_TYPE_RSV_IRAP_VCL23 = 23
H265_NALU_TYPE_RSV_VCL24 = 24
H265_NALU_TYPE_RSV_VCL25 = 25
H265_NALU_TYPE_RSV_VCL26 = 26
H265_NALU_TYPE_RSV_VCL27 = 27
H265_NALU_TYPE_RSV_VCL28 = 28
H265_NALU_TYPE_RSV_VCL29 = 29
H265_NALU_TYPE_RSV_VCL30 = 30
H265_NALU_TYPE_RSV_VCL31 = 31
H265_NALU_TYPE_VPS_NUT = 32
H265_NALU_TYPE_SPS_NUT = 33
H265_NALU_TYPE_PPS_NUT = 34
H265_NALU_TYPE_AUD_NUT = 35
H265_NALU_TYPE_EOS_NUT = 36
H265_NALU_TYPE_EOB_NUT = 37
H265_NALU_TYPE_FD_NUT = 38
H265_NALU_TYPE_PREFIX_SEI_NUT = 39
H265_NALU_TYPE_SUFFIX_SEI_NUT = 40
H265_NALU_TYPE_RSV_NVCL41 = 41
H265_NALU_TYPE_RSV_NVCL42 = 42
H265_NALU_TYPE_RSV_NVCL43 = 43
H265_NALU_TYPE_RSV_NVCL44 = 44
H265_NALU_TYPE_RSV_NVCL45 = 45
H265_NALU_TYPE_RSV_NVCL46 = 46
H265_NALU_TYPE_RSV_NVCL47 = 47
H265_NALU_TYPE_UNSPEC48 = 48
H265_NALU_TYPE_UNSPEC49 = 49
H265_NALU_TYPE_UNSPEC50 = 50
H265_NALU_TYPE_UNSPEC51 = 51
H265_NALU_TYPE_UNSPEC52 = 52
H265_NALU_TYPE_UNSPEC53 = 53
H265_NALU_TYPE_UNSPEC54 = 54
H265_NALU_TYPE_UNSPEC55 = 55
H265_NALU_TYPE_UNSPEC56 = 56
H265_NALU_TYPE_UNSPEC57 = 57
H265_NALU_TYPE_UNSPEC58 = 58
H265_NALU_TYPE_UNSPEC59 = 59
H265_NALU_TYPE_UNSPEC60 = 60
H265_NALU_TYPE_UNSPEC61 = 61
H265_NALU_TYPE_UNSPEC62 = 62
H265_NALU_TYPE_UNSPEC63 = 63
h265_nalu_type = ctypes.c_int32 # enum
class struct_vdef_nalu_0_1(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('type', h265_nalu_type),
    ]

class union_vdef_nalu_0(Union):
    pass

union_vdef_nalu_0._pack_ = True # source:False
union_vdef_nalu_0._fields_ = [
    ('h264', struct_vdef_nalu_0_0),
    ('h265', struct_vdef_nalu_0_1),
    ('PADDING_0', ctypes.c_ubyte * 8),
]

class struct_vdef_nalu(Structure):
    pass

struct_vdef_nalu._pack_ = True # source:False
struct_vdef_nalu._fields_ = [
    ('size', ctypes.c_uint64),
    ('vdef_nalu_0', union_vdef_nalu_0),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_vdef_coded_frame(Structure):
    pass

struct_vdef_coded_frame._pack_ = True # source:False
struct_vdef_coded_frame._fields_ = [
    ('format', struct_vdef_coded_format),
    ('info', struct_vdef_frame_info),
    ('type', vdef_coded_frame_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

vdef_is_raw_format_valid = _libraries['libvideo-defs.so'].vdef_is_raw_format_valid
vdef_is_raw_format_valid.restype = ctypes.c_bool
vdef_is_raw_format_valid.argtypes = [POINTER_T(struct_vdef_raw_format)]
vdef_raw_format_cmp = _libraries['libvideo-defs.so'].vdef_raw_format_cmp
vdef_raw_format_cmp.restype = ctypes.c_bool
vdef_raw_format_cmp.argtypes = [POINTER_T(struct_vdef_raw_format), POINTER_T(struct_vdef_raw_format)]
vdef_raw_format_intersect = _libraries['libvideo-defs.so'].vdef_raw_format_intersect
vdef_raw_format_intersect.restype = ctypes.c_bool
vdef_raw_format_intersect.argtypes = [POINTER_T(struct_vdef_raw_format), POINTER_T(struct_vdef_raw_format), ctypes.c_uint32]
vdef_is_coded_format_valid = _libraries['libvideo-defs.so'].vdef_is_coded_format_valid
vdef_is_coded_format_valid.restype = ctypes.c_bool
vdef_is_coded_format_valid.argtypes = [POINTER_T(struct_vdef_coded_format)]
vdef_coded_format_cmp = _libraries['libvideo-defs.so'].vdef_coded_format_cmp
vdef_coded_format_cmp.restype = ctypes.c_bool
vdef_coded_format_cmp.argtypes = [POINTER_T(struct_vdef_coded_format), POINTER_T(struct_vdef_coded_format)]
vdef_coded_format_intersect = _libraries['libvideo-defs.so'].vdef_coded_format_intersect
vdef_coded_format_intersect.restype = ctypes.c_bool
vdef_coded_format_intersect.argtypes = [POINTER_T(struct_vdef_coded_format), POINTER_T(struct_vdef_coded_format), ctypes.c_uint32]
vdef_frame_type_from_str = _libraries['libvideo-defs.so'].vdef_frame_type_from_str
vdef_frame_type_from_str.restype = vdef_frame_type
vdef_frame_type_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_frame_type_to_str = _libraries['libvideo-defs.so'].vdef_frame_type_to_str
vdef_frame_type_to_str.restype = POINTER_T(ctypes.c_char)
vdef_frame_type_to_str.argtypes = [vdef_frame_type]
vdef_raw_pix_format_from_str = _libraries['libvideo-defs.so'].vdef_raw_pix_format_from_str
vdef_raw_pix_format_from_str.restype = vdef_raw_pix_format
vdef_raw_pix_format_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_raw_pix_format_to_str = _libraries['libvideo-defs.so'].vdef_raw_pix_format_to_str
vdef_raw_pix_format_to_str.restype = POINTER_T(ctypes.c_char)
vdef_raw_pix_format_to_str.argtypes = [vdef_raw_pix_format]
vdef_raw_pix_order_from_str = _libraries['libvideo-defs.so'].vdef_raw_pix_order_from_str
vdef_raw_pix_order_from_str.restype = vdef_raw_pix_order
vdef_raw_pix_order_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_raw_pix_order_to_str = _libraries['libvideo-defs.so'].vdef_raw_pix_order_to_str
vdef_raw_pix_order_to_str.restype = POINTER_T(ctypes.c_char)
vdef_raw_pix_order_to_str.argtypes = [vdef_raw_pix_order]
vdef_raw_pix_layout_from_str = _libraries['libvideo-defs.so'].vdef_raw_pix_layout_from_str
vdef_raw_pix_layout_from_str.restype = vdef_raw_pix_layout
vdef_raw_pix_layout_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_raw_pix_layout_to_str = _libraries['libvideo-defs.so'].vdef_raw_pix_layout_to_str
vdef_raw_pix_layout_to_str.restype = POINTER_T(ctypes.c_char)
vdef_raw_pix_layout_to_str.argtypes = [vdef_raw_pix_layout]
vdef_raw_data_layout_from_str = _libraries['libvideo-defs.so'].vdef_raw_data_layout_from_str
vdef_raw_data_layout_from_str.restype = vdef_raw_data_layout
vdef_raw_data_layout_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_raw_data_layout_to_str = _libraries['libvideo-defs.so'].vdef_raw_data_layout_to_str
vdef_raw_data_layout_to_str.restype = POINTER_T(ctypes.c_char)
vdef_raw_data_layout_to_str.argtypes = [vdef_raw_data_layout]
vdef_raw_format_from_str = _libraries['libvideo-defs.so'].vdef_raw_format_from_str
vdef_raw_format_from_str.restype = ctypes.c_int32
vdef_raw_format_from_str.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vdef_raw_format)]
vdef_raw_format_to_str = _libraries['libvideo-defs.so'].vdef_raw_format_to_str
vdef_raw_format_to_str.restype = POINTER_T(ctypes.c_char)
vdef_raw_format_to_str.argtypes = [POINTER_T(struct_vdef_raw_format)]
vdef_get_raw_frame_plane_count = _libraries['libvideo-defs.so'].vdef_get_raw_frame_plane_count
vdef_get_raw_frame_plane_count.restype = ctypes.c_uint32
vdef_get_raw_frame_plane_count.argtypes = [POINTER_T(struct_vdef_raw_format)]
vdef_calc_raw_frame_size = _libraries['libvideo-defs.so'].vdef_calc_raw_frame_size
vdef_calc_raw_frame_size.restype = ctypes.c_int32
vdef_calc_raw_frame_size.argtypes = [POINTER_T(struct_vdef_raw_format), POINTER_T(struct_vdef_dim), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint32), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint32), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint32)]
ssize_t = ctypes.c_int64
vdef_calc_raw_contiguous_frame_size = _libraries['libvideo-defs.so'].vdef_calc_raw_contiguous_frame_size
vdef_calc_raw_contiguous_frame_size.restype = ssize_t
vdef_calc_raw_contiguous_frame_size.argtypes = [POINTER_T(struct_vdef_raw_format), POINTER_T(struct_vdef_dim), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint32), POINTER_T(ctypes.c_uint64), POINTER_T(ctypes.c_uint32), POINTER_T(ctypes.c_uint32)]
vdef_encoding_from_str = _libraries['libvideo-defs.so'].vdef_encoding_from_str
vdef_encoding_from_str.restype = vdef_encoding
vdef_encoding_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_encoding_to_str = _libraries['libvideo-defs.so'].vdef_encoding_to_str
vdef_encoding_to_str.restype = POINTER_T(ctypes.c_char)
vdef_encoding_to_str.argtypes = [vdef_encoding]
vdef_get_encoding_mime_type = _libraries['libvideo-defs.so'].vdef_get_encoding_mime_type
vdef_get_encoding_mime_type.restype = POINTER_T(ctypes.c_char)
vdef_get_encoding_mime_type.argtypes = [vdef_encoding]
vdef_coded_data_format_from_str = _libraries['libvideo-defs.so'].vdef_coded_data_format_from_str
vdef_coded_data_format_from_str.restype = vdef_coded_data_format
vdef_coded_data_format_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_coded_data_format_to_str = _libraries['libvideo-defs.so'].vdef_coded_data_format_to_str
vdef_coded_data_format_to_str.restype = POINTER_T(ctypes.c_char)
vdef_coded_data_format_to_str.argtypes = [vdef_coded_data_format]
vdef_coded_format_from_str = _libraries['libvideo-defs.so'].vdef_coded_format_from_str
vdef_coded_format_from_str.restype = ctypes.c_int32
vdef_coded_format_from_str.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vdef_coded_format)]
vdef_coded_format_to_str = _libraries['libvideo-defs.so'].vdef_coded_format_to_str
vdef_coded_format_to_str.restype = POINTER_T(ctypes.c_char)
vdef_coded_format_to_str.argtypes = [POINTER_T(struct_vdef_coded_format)]
vdef_coded_frame_type_from_str = _libraries['libvideo-defs.so'].vdef_coded_frame_type_from_str
vdef_coded_frame_type_from_str.restype = vdef_coded_frame_type
vdef_coded_frame_type_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_coded_frame_type_to_str = _libraries['libvideo-defs.so'].vdef_coded_frame_type_to_str
vdef_coded_frame_type_to_str.restype = POINTER_T(ctypes.c_char)
vdef_coded_frame_type_to_str.argtypes = [vdef_coded_frame_type]
vdef_color_primaries_from_h264 = _libraries['libvideo-defs.so'].vdef_color_primaries_from_h264
vdef_color_primaries_from_h264.restype = vdef_color_primaries
vdef_color_primaries_from_h264.argtypes = [uint32_t]
vdef_color_primaries_to_h264 = _libraries['libvideo-defs.so'].vdef_color_primaries_to_h264
vdef_color_primaries_to_h264.restype = uint32_t
vdef_color_primaries_to_h264.argtypes = [vdef_color_primaries]
vdef_color_primaries_from_h265 = _libraries['libvideo-defs.so'].vdef_color_primaries_from_h265
vdef_color_primaries_from_h265.restype = vdef_color_primaries
vdef_color_primaries_from_h265.argtypes = [uint32_t]
vdef_color_primaries_to_h265 = _libraries['libvideo-defs.so'].vdef_color_primaries_to_h265
vdef_color_primaries_to_h265.restype = uint32_t
vdef_color_primaries_to_h265.argtypes = [vdef_color_primaries]
vdef_color_primaries_from_str = _libraries['libvideo-defs.so'].vdef_color_primaries_from_str
vdef_color_primaries_from_str.restype = vdef_color_primaries
vdef_color_primaries_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_color_primaries_to_str = _libraries['libvideo-defs.so'].vdef_color_primaries_to_str
vdef_color_primaries_to_str.restype = POINTER_T(ctypes.c_char)
vdef_color_primaries_to_str.argtypes = [vdef_color_primaries]
vdef_color_primaries_from_values = _libraries['libvideo-defs.so'].vdef_color_primaries_from_values
vdef_color_primaries_from_values.restype = vdef_color_primaries
vdef_color_primaries_from_values.argtypes = [POINTER_T(struct_vdef_color_primaries_value)]
vdef_transfer_function_from_h264 = _libraries['libvideo-defs.so'].vdef_transfer_function_from_h264
vdef_transfer_function_from_h264.restype = vdef_transfer_function
vdef_transfer_function_from_h264.argtypes = [uint32_t]
vdef_transfer_function_to_h264 = _libraries['libvideo-defs.so'].vdef_transfer_function_to_h264
vdef_transfer_function_to_h264.restype = uint32_t
vdef_transfer_function_to_h264.argtypes = [vdef_transfer_function]
vdef_transfer_function_from_h265 = _libraries['libvideo-defs.so'].vdef_transfer_function_from_h265
vdef_transfer_function_from_h265.restype = vdef_transfer_function
vdef_transfer_function_from_h265.argtypes = [uint32_t]
vdef_transfer_function_to_h265 = _libraries['libvideo-defs.so'].vdef_transfer_function_to_h265
vdef_transfer_function_to_h265.restype = uint32_t
vdef_transfer_function_to_h265.argtypes = [vdef_transfer_function]
vdef_transfer_function_from_str = _libraries['libvideo-defs.so'].vdef_transfer_function_from_str
vdef_transfer_function_from_str.restype = vdef_transfer_function
vdef_transfer_function_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_transfer_function_to_str = _libraries['libvideo-defs.so'].vdef_transfer_function_to_str
vdef_transfer_function_to_str.restype = POINTER_T(ctypes.c_char)
vdef_transfer_function_to_str.argtypes = [vdef_transfer_function]
vdef_matrix_coefs_from_h264 = _libraries['libvideo-defs.so'].vdef_matrix_coefs_from_h264
vdef_matrix_coefs_from_h264.restype = vdef_matrix_coefs
vdef_matrix_coefs_from_h264.argtypes = [uint32_t]
vdef_matrix_coefs_to_h264 = _libraries['libvideo-defs.so'].vdef_matrix_coefs_to_h264
vdef_matrix_coefs_to_h264.restype = uint32_t
vdef_matrix_coefs_to_h264.argtypes = [vdef_matrix_coefs]
vdef_matrix_coefs_from_h265 = _libraries['libvideo-defs.so'].vdef_matrix_coefs_from_h265
vdef_matrix_coefs_from_h265.restype = vdef_matrix_coefs
vdef_matrix_coefs_from_h265.argtypes = [uint32_t]
vdef_matrix_coefs_to_h265 = _libraries['libvideo-defs.so'].vdef_matrix_coefs_to_h265
vdef_matrix_coefs_to_h265.restype = uint32_t
vdef_matrix_coefs_to_h265.argtypes = [vdef_matrix_coefs]
vdef_matrix_coefs_from_str = _libraries['libvideo-defs.so'].vdef_matrix_coefs_from_str
vdef_matrix_coefs_from_str.restype = vdef_matrix_coefs
vdef_matrix_coefs_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_matrix_coefs_to_str = _libraries['libvideo-defs.so'].vdef_matrix_coefs_to_str
vdef_matrix_coefs_to_str.restype = POINTER_T(ctypes.c_char)
vdef_matrix_coefs_to_str.argtypes = [vdef_matrix_coefs]
vdef_dynamic_range_from_str = _libraries['libvideo-defs.so'].vdef_dynamic_range_from_str
vdef_dynamic_range_from_str.restype = vdef_dynamic_range
vdef_dynamic_range_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_dynamic_range_to_str = _libraries['libvideo-defs.so'].vdef_dynamic_range_to_str
vdef_dynamic_range_to_str.restype = POINTER_T(ctypes.c_char)
vdef_dynamic_range_to_str.argtypes = [vdef_dynamic_range]
vdef_tone_mapping_from_str = _libraries['libvideo-defs.so'].vdef_tone_mapping_from_str
vdef_tone_mapping_from_str.restype = vdef_tone_mapping
vdef_tone_mapping_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vdef_tone_mapping_to_str = _libraries['libvideo-defs.so'].vdef_tone_mapping_to_str
vdef_tone_mapping_to_str.restype = POINTER_T(ctypes.c_char)
vdef_tone_mapping_to_str.argtypes = [vdef_tone_mapping]
vdef_dim_cmp = _libraries['FIXME_STUB'].vdef_dim_cmp
vdef_dim_cmp.restype = ctypes.c_bool
vdef_dim_cmp.argtypes = [POINTER_T(struct_vdef_dim), POINTER_T(struct_vdef_dim)]
vdef_dim_is_null = _libraries['FIXME_STUB'].vdef_dim_is_null
vdef_dim_is_null.restype = ctypes.c_bool
vdef_dim_is_null.argtypes = [POINTER_T(struct_vdef_dim)]
vdef_dim_is_aligned = _libraries['libvideo-defs.so'].vdef_dim_is_aligned
vdef_dim_is_aligned.restype = ctypes.c_bool
vdef_dim_is_aligned.argtypes = [POINTER_T(struct_vdef_dim), POINTER_T(struct_vdef_dim)]
vdef_frac_diff = _libraries['FIXME_STUB'].vdef_frac_diff
vdef_frac_diff.restype = ctypes.c_int32
vdef_frac_diff.argtypes = [POINTER_T(struct_vdef_frac), POINTER_T(struct_vdef_frac)]
vdef_frac_is_null = _libraries['FIXME_STUB'].vdef_frac_is_null
vdef_frac_is_null.restype = ctypes.c_bool
vdef_frac_is_null.argtypes = [POINTER_T(struct_vdef_frac)]
vdef_rect_cmp = _libraries['FIXME_STUB'].vdef_rect_cmp
vdef_rect_cmp.restype = ctypes.c_bool
vdef_rect_cmp.argtypes = [POINTER_T(struct_vdef_rect), POINTER_T(struct_vdef_rect)]
vdef_rect_fit = _libraries['libvideo-defs.so'].vdef_rect_fit
vdef_rect_fit.restype = ctypes.c_bool
vdef_rect_fit.argtypes = [POINTER_T(struct_vdef_rect), POINTER_T(struct_vdef_rect)]
vdef_rect_is_aligned = _libraries['libvideo-defs.so'].vdef_rect_is_aligned
vdef_rect_is_aligned.restype = ctypes.c_bool
vdef_rect_is_aligned.argtypes = [POINTER_T(struct_vdef_rect), POINTER_T(struct_vdef_rect)]
vdef_rect_align = _libraries['libvideo-defs.so'].vdef_rect_align
vdef_rect_align.restype = None
vdef_rect_align.argtypes = [POINTER_T(struct_vdef_rect), POINTER_T(struct_vdef_rect), ctypes.c_bool, ctypes.c_bool]
vdef_format_to_frame_info = _libraries['libvideo-defs.so'].vdef_format_to_frame_info
vdef_format_to_frame_info.restype = None
vdef_format_to_frame_info.argtypes = [POINTER_T(struct_vdef_format_info), POINTER_T(struct_vdef_frame_info)]
vdef_frame_to_format_info = _libraries['libvideo-defs.so'].vdef_frame_to_format_info
vdef_frame_to_format_info.restype = None
vdef_frame_to_format_info.argtypes = [POINTER_T(struct_vdef_frame_info), POINTER_T(struct_vdef_format_info)]
vdef_format_info_to_json = _libraries['libvideo-defs.so'].vdef_format_info_to_json
vdef_format_info_to_json.restype = ctypes.c_int32
vdef_format_info_to_json.argtypes = [POINTER_T(struct_vdef_format_info), POINTER_T(struct_json_object)]
vdef_frame_info_to_json = _libraries['libvideo-defs.so'].vdef_frame_info_to_json
vdef_frame_info_to_json.restype = ctypes.c_int32
vdef_frame_info_to_json.argtypes = [POINTER_T(struct_vdef_frame_info), ctypes.c_bool, POINTER_T(struct_json_object)]
vdef_raw_format_to_csv = _libraries['libvideo-defs.so'].vdef_raw_format_to_csv
vdef_raw_format_to_csv.restype = ctypes.c_int32
vdef_raw_format_to_csv.argtypes = [POINTER_T(struct_vdef_raw_format), POINTER_T(POINTER_T(ctypes.c_char))]
vdef_raw_format_from_csv = _libraries['libvideo-defs.so'].vdef_raw_format_from_csv
vdef_raw_format_from_csv.restype = ctypes.c_int32
vdef_raw_format_from_csv.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vdef_raw_format)]
vdef_coded_format_to_csv = _libraries['libvideo-defs.so'].vdef_coded_format_to_csv
vdef_coded_format_to_csv.restype = ctypes.c_int32
vdef_coded_format_to_csv.argtypes = [POINTER_T(struct_vdef_coded_format), POINTER_T(POINTER_T(ctypes.c_char))]
vdef_coded_format_from_csv = _libraries['libvideo-defs.so'].vdef_coded_format_from_csv
vdef_coded_format_from_csv.restype = ctypes.c_int32
vdef_coded_format_from_csv.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vdef_coded_format)]
vdef_format_info_to_csv = _libraries['libvideo-defs.so'].vdef_format_info_to_csv
vdef_format_info_to_csv.restype = ctypes.c_int32
vdef_format_info_to_csv.argtypes = [POINTER_T(struct_vdef_format_info), POINTER_T(POINTER_T(ctypes.c_char))]
vdef_format_info_from_csv = _libraries['libvideo-defs.so'].vdef_format_info_from_csv
vdef_format_info_from_csv.restype = ctypes.c_int32
vdef_format_info_from_csv.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vdef_format_info)]

# values for enumeration 'vmeta_camera_type'
vmeta_camera_type__enumvalues = {
    0: 'VMETA_CAMERA_TYPE_UNKNOWN',
    1: 'VMETA_CAMERA_TYPE_FRONT',
    2: 'VMETA_CAMERA_TYPE_FRONT_STEREO_LEFT',
    3: 'VMETA_CAMERA_TYPE_FRONT_STEREO_RIGHT',
    4: 'VMETA_CAMERA_TYPE_VERTICAL',
    5: 'VMETA_CAMERA_TYPE_DISPARITY',
}
VMETA_CAMERA_TYPE_UNKNOWN = 0
VMETA_CAMERA_TYPE_FRONT = 1
VMETA_CAMERA_TYPE_FRONT_STEREO_LEFT = 2
VMETA_CAMERA_TYPE_FRONT_STEREO_RIGHT = 3
VMETA_CAMERA_TYPE_VERTICAL = 4
VMETA_CAMERA_TYPE_DISPARITY = 5
vmeta_camera_type = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_video_mode'
vmeta_video_mode__enumvalues = {
    0: 'VMETA_VIDEO_MODE_UNKNOWN',
    1: 'VMETA_VIDEO_MODE_STANDARD',
    2: 'VMETA_VIDEO_MODE_HYPERLAPSE',
    3: 'VMETA_VIDEO_MODE_SLOWMOTION',
}
VMETA_VIDEO_MODE_UNKNOWN = 0
VMETA_VIDEO_MODE_STANDARD = 1
VMETA_VIDEO_MODE_HYPERLAPSE = 2
VMETA_VIDEO_MODE_SLOWMOTION = 3
vmeta_video_mode = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_video_stop_reason'
vmeta_video_stop_reason__enumvalues = {
    0: 'VMETA_VIDEO_STOP_REASON_UNKNOWN',
    1: 'VMETA_VIDEO_STOP_REASON_USER',
    2: 'VMETA_VIDEO_STOP_REASON_RECONFIGURATION',
    3: 'VMETA_VIDEO_STOP_REASON_POOR_STORAGE_PERF',
    4: 'VMETA_VIDEO_STOP_REASON_STORAGE_FULL',
    5: 'VMETA_VIDEO_STOP_REASON_RECOVERY',
    6: 'VMETA_VIDEO_STOP_REASON_END_OF_STREAM',
    7: 'VMETA_VIDEO_STOP_REASON_SHUTDOWN',
}
VMETA_VIDEO_STOP_REASON_UNKNOWN = 0
VMETA_VIDEO_STOP_REASON_USER = 1
VMETA_VIDEO_STOP_REASON_RECONFIGURATION = 2
VMETA_VIDEO_STOP_REASON_POOR_STORAGE_PERF = 3
VMETA_VIDEO_STOP_REASON_STORAGE_FULL = 4
VMETA_VIDEO_STOP_REASON_RECOVERY = 5
VMETA_VIDEO_STOP_REASON_END_OF_STREAM = 6
VMETA_VIDEO_STOP_REASON_SHUTDOWN = 7
vmeta_video_stop_reason = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_dynamic_range'
vmeta_dynamic_range__enumvalues = {
    0: 'VMETA_DYNAMIC_RANGE_UNKNOWN',
    1: 'VMETA_DYNAMIC_RANGE_SDR',
    2: 'VMETA_DYNAMIC_RANGE_HDR8',
    3: 'VMETA_DYNAMIC_RANGE_HDR10',
}
VMETA_DYNAMIC_RANGE_UNKNOWN = 0
VMETA_DYNAMIC_RANGE_SDR = 1
VMETA_DYNAMIC_RANGE_HDR8 = 2
VMETA_DYNAMIC_RANGE_HDR10 = 3
vmeta_dynamic_range = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_tone_mapping'
vmeta_tone_mapping__enumvalues = {
    0: 'VMETA_TONE_MAPPING_UNKNOWN',
    1: 'VMETA_TONE_MAPPING_STANDARD',
    2: 'VMETA_TONE_MAPPING_P_LOG',
}
VMETA_TONE_MAPPING_UNKNOWN = 0
VMETA_TONE_MAPPING_STANDARD = 1
VMETA_TONE_MAPPING_P_LOG = 2
vmeta_tone_mapping = ctypes.c_uint32 # enum
class union_vmeta_buffer_0(Union):
    pass

union_vmeta_buffer_0._pack_ = True # source:False
union_vmeta_buffer_0._fields_ = [
    ('data', POINTER_T(ctypes.c_ubyte)),
    ('cdata', POINTER_T(ctypes.c_ubyte)),
]

class struct_vmeta_buffer(Structure):
    pass

struct_vmeta_buffer._pack_ = True # source:False
struct_vmeta_buffer._fields_ = [
    ('vmeta_buffer_0', union_vmeta_buffer_0),
    ('len', ctypes.c_uint64),
    ('pos', ctypes.c_uint64),
]

vmeta_buffer_set_data = _libraries['FIXME_STUB'].vmeta_buffer_set_data
vmeta_buffer_set_data.restype = None
vmeta_buffer_set_data.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(ctypes.c_ubyte), size_t, size_t]
vmeta_buffer_set_cdata = _libraries['FIXME_STUB'].vmeta_buffer_set_cdata
vmeta_buffer_set_cdata.restype = None
vmeta_buffer_set_cdata.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(ctypes.c_ubyte), size_t, size_t]
class struct_vmeta_quaternion(Structure):
    pass

struct_vmeta_quaternion._pack_ = True # source:False
struct_vmeta_quaternion._fields_ = [
    ('w', ctypes.c_float),
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('z', ctypes.c_float),
]

class union_vmeta_euler_0(Union):
    pass

union_vmeta_euler_0._pack_ = True # source:False
union_vmeta_euler_0._fields_ = [
    ('yaw', ctypes.c_float),
    ('psi', ctypes.c_float),
]

class union_vmeta_euler_1(Union):
    pass

union_vmeta_euler_1._pack_ = True # source:False
union_vmeta_euler_1._fields_ = [
    ('pitch', ctypes.c_float),
    ('theta', ctypes.c_float),
]

class union_vmeta_euler_2(Union):
    pass

union_vmeta_euler_2._pack_ = True # source:False
union_vmeta_euler_2._fields_ = [
    ('roll', ctypes.c_float),
    ('phi', ctypes.c_float),
]

class struct_vmeta_euler(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('vmeta_euler_0', union_vmeta_euler_0),
        ('vmeta_euler_1', union_vmeta_euler_1),
        ('vmeta_euler_2', union_vmeta_euler_2),
    ]

class struct_vmeta_xyz(Structure):
    pass

struct_vmeta_xyz._pack_ = True # source:False
struct_vmeta_xyz._fields_ = [
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('z', ctypes.c_float),
]

class struct_vmeta_ned(Structure):
    pass

struct_vmeta_ned._pack_ = True # source:False
struct_vmeta_ned._fields_ = [
    ('north', ctypes.c_float),
    ('east', ctypes.c_float),
    ('down', ctypes.c_float),
]

class struct_vmeta_fov(Structure):
    pass

struct_vmeta_fov._pack_ = True # source:False
struct_vmeta_fov._fields_ = [
    ('horz', ctypes.c_float),
    ('vert', ctypes.c_float),
    ('has_horz', ctypes.c_uint32, 1),
    ('has_vert', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint32, 30),
]

class struct_vmeta_thermal_spot(Structure):
    pass

struct_vmeta_thermal_spot._pack_ = True # source:False
struct_vmeta_thermal_spot._fields_ = [
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('temp', ctypes.c_float),
    ('valid', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_vmeta_location(Structure):
    pass

struct_vmeta_location._pack_ = True # source:False
struct_vmeta_location._fields_ = [
    ('latitude', ctypes.c_double),
    ('longitude', ctypes.c_double),
    ('altitude', ctypes.c_double),
    ('horizontal_accuracy', ctypes.c_float),
    ('vertical_accuracy', ctypes.c_float),
    ('sv_count', ctypes.c_ubyte),
    ('valid', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 6),
]

vmeta_euler_to_quat = _libraries['libvideo-metadata.so'].vmeta_euler_to_quat
vmeta_euler_to_quat.restype = None
vmeta_euler_to_quat.argtypes = [POINTER_T(struct_vmeta_euler), POINTER_T(struct_vmeta_quaternion)]
vmeta_quat_to_euler = _libraries['libvideo-metadata.so'].vmeta_quat_to_euler
vmeta_quat_to_euler.restype = None
vmeta_quat_to_euler.argtypes = [POINTER_T(struct_vmeta_quaternion), POINTER_T(struct_vmeta_euler)]
vmeta_camera_type_from_str = _libraries['libvideo-metadata.so'].vmeta_camera_type_from_str
vmeta_camera_type_from_str.restype = vmeta_camera_type
vmeta_camera_type_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vmeta_camera_type_to_str = _libraries['libvideo-metadata.so'].vmeta_camera_type_to_str
vmeta_camera_type_to_str.restype = POINTER_T(ctypes.c_char)
vmeta_camera_type_to_str.argtypes = [vmeta_camera_type]
vmeta_video_mode_from_str = _libraries['libvideo-metadata.so'].vmeta_video_mode_from_str
vmeta_video_mode_from_str.restype = vmeta_video_mode
vmeta_video_mode_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vmeta_video_mode_to_str = _libraries['libvideo-metadata.so'].vmeta_video_mode_to_str
vmeta_video_mode_to_str.restype = POINTER_T(ctypes.c_char)
vmeta_video_mode_to_str.argtypes = [vmeta_video_mode]
vmeta_video_stop_reason_from_str = _libraries['libvideo-metadata.so'].vmeta_video_stop_reason_from_str
vmeta_video_stop_reason_from_str.restype = vmeta_video_stop_reason
vmeta_video_stop_reason_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vmeta_video_stop_reason_to_str = _libraries['libvideo-metadata.so'].vmeta_video_stop_reason_to_str
vmeta_video_stop_reason_to_str.restype = POINTER_T(ctypes.c_char)
vmeta_video_stop_reason_to_str.argtypes = [vmeta_video_stop_reason]
vmeta_dynamic_range_from_str = _libraries['libvideo-metadata.so'].vmeta_dynamic_range_from_str
vmeta_dynamic_range_from_str.restype = vmeta_dynamic_range
vmeta_dynamic_range_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vmeta_dynamic_range_to_str = _libraries['libvideo-metadata.so'].vmeta_dynamic_range_to_str
vmeta_dynamic_range_to_str.restype = POINTER_T(ctypes.c_char)
vmeta_dynamic_range_to_str.argtypes = [vmeta_dynamic_range]
vmeta_tone_mapping_from_str = _libraries['libvideo-metadata.so'].vmeta_tone_mapping_from_str
vmeta_tone_mapping_from_str.restype = vmeta_tone_mapping
vmeta_tone_mapping_from_str.argtypes = [POINTER_T(ctypes.c_char)]
vmeta_tone_mapping_to_str = _libraries['libvideo-metadata.so'].vmeta_tone_mapping_to_str
vmeta_tone_mapping_to_str.restype = POINTER_T(ctypes.c_char)
vmeta_tone_mapping_to_str.argtypes = [vmeta_tone_mapping]

# values for enumeration 'vmeta_flying_state'
vmeta_flying_state__enumvalues = {
    0: 'VMETA_FLYING_STATE_LANDED',
    1: 'VMETA_FLYING_STATE_TAKINGOFF',
    2: 'VMETA_FLYING_STATE_HOVERING',
    3: 'VMETA_FLYING_STATE_FLYING',
    4: 'VMETA_FLYING_STATE_LANDING',
    5: 'VMETA_FLYING_STATE_EMERGENCY',
    6: 'VMETA_FLYING_STATE_USER_TAKEOFF',
    7: 'VMETA_FLYING_STATE_MOTOR_RAMPING',
    8: 'VMETA_FLYING_STATE_EMERGENCY_LANDING',
}
VMETA_FLYING_STATE_LANDED = 0
VMETA_FLYING_STATE_TAKINGOFF = 1
VMETA_FLYING_STATE_HOVERING = 2
VMETA_FLYING_STATE_FLYING = 3
VMETA_FLYING_STATE_LANDING = 4
VMETA_FLYING_STATE_EMERGENCY = 5
VMETA_FLYING_STATE_USER_TAKEOFF = 6
VMETA_FLYING_STATE_MOTOR_RAMPING = 7
VMETA_FLYING_STATE_EMERGENCY_LANDING = 8
vmeta_flying_state = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_piloting_mode'
vmeta_piloting_mode__enumvalues = {
    0: 'VMETA_PILOTING_MODE_MANUAL',
    1: 'VMETA_PILOTING_MODE_RETURN_HOME',
    2: 'VMETA_PILOTING_MODE_FLIGHT_PLAN',
    3: 'VMETA_PILOTING_MODE_TRACKING',
    3: 'VMETA_PILOTING_MODE_FOLLOW_ME',
    4: 'VMETA_PILOTING_MODE_MAGIC_CARPET',
    5: 'VMETA_PILOTING_MODE_MOVE_TO',
}
VMETA_PILOTING_MODE_MANUAL = 0
VMETA_PILOTING_MODE_RETURN_HOME = 1
VMETA_PILOTING_MODE_FLIGHT_PLAN = 2
VMETA_PILOTING_MODE_TRACKING = 3
VMETA_PILOTING_MODE_FOLLOW_ME = 3
VMETA_PILOTING_MODE_MAGIC_CARPET = 4
VMETA_PILOTING_MODE_MOVE_TO = 5
vmeta_piloting_mode = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_followme_anim'
vmeta_followme_anim__enumvalues = {
    0: 'VMETA_FOLLOWME_ANIM_NONE',
    1: 'VMETA_FOLLOWME_ANIM_ORBIT',
    2: 'VMETA_FOLLOWME_ANIM_BOOMERANG',
    3: 'VMETA_FOLLOWME_ANIM_PARABOLA',
    4: 'VMETA_FOLLOWME_ANIM_ZENITH',
}
VMETA_FOLLOWME_ANIM_NONE = 0
VMETA_FOLLOWME_ANIM_ORBIT = 1
VMETA_FOLLOWME_ANIM_BOOMERANG = 2
VMETA_FOLLOWME_ANIM_PARABOLA = 3
VMETA_FOLLOWME_ANIM_ZENITH = 4
vmeta_followme_anim = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_automation_anim'
vmeta_automation_anim__enumvalues = {
    0: 'VMETA_AUTOMATION_ANIM_NONE',
    1: 'VMETA_AUTOMATION_ANIM_ORBIT',
    2: 'VMETA_AUTOMATION_ANIM_BOOMERANG',
    3: 'VMETA_AUTOMATION_ANIM_PARABOLA',
    4: 'VMETA_AUTOMATION_ANIM_DOLLY_SLIDE',
    5: 'VMETA_AUTOMATION_ANIM_DOLLY_ZOOM',
    6: 'VMETA_AUTOMATION_ANIM_REVEAL_VERT',
    7: 'VMETA_AUTOMATION_ANIM_REVEAL_HORZ',
    8: 'VMETA_AUTOMATION_ANIM_PANORAMA_HORZ',
    9: 'VMETA_AUTOMATION_ANIM_CANDLE',
    10: 'VMETA_AUTOMATION_ANIM_FLIP_FRONT',
    11: 'VMETA_AUTOMATION_ANIM_FLIP_BACK',
    12: 'VMETA_AUTOMATION_ANIM_FLIP_LEFT',
    13: 'VMETA_AUTOMATION_ANIM_FLIP_RIGHT',
    14: 'VMETA_AUTOMATION_ANIM_TWISTUP',
    15: 'VMETA_AUTOMATION_ANIM_POSITION_TWISTUP',
}
VMETA_AUTOMATION_ANIM_NONE = 0
VMETA_AUTOMATION_ANIM_ORBIT = 1
VMETA_AUTOMATION_ANIM_BOOMERANG = 2
VMETA_AUTOMATION_ANIM_PARABOLA = 3
VMETA_AUTOMATION_ANIM_DOLLY_SLIDE = 4
VMETA_AUTOMATION_ANIM_DOLLY_ZOOM = 5
VMETA_AUTOMATION_ANIM_REVEAL_VERT = 6
VMETA_AUTOMATION_ANIM_REVEAL_HORZ = 7
VMETA_AUTOMATION_ANIM_PANORAMA_HORZ = 8
VMETA_AUTOMATION_ANIM_CANDLE = 9
VMETA_AUTOMATION_ANIM_FLIP_FRONT = 10
VMETA_AUTOMATION_ANIM_FLIP_BACK = 11
VMETA_AUTOMATION_ANIM_FLIP_LEFT = 12
VMETA_AUTOMATION_ANIM_FLIP_RIGHT = 13
VMETA_AUTOMATION_ANIM_TWISTUP = 14
VMETA_AUTOMATION_ANIM_POSITION_TWISTUP = 15
vmeta_automation_anim = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_thermal_calib_state'
vmeta_thermal_calib_state__enumvalues = {
    0: 'VMETA_THERMAL_CALIB_STATE_DONE',
    1: 'VMETA_THERMAL_CALIB_STATE_REQUESTED',
    2: 'VMETA_THERMAL_CALIB_STATE_IN_PROGRESS',
}
VMETA_THERMAL_CALIB_STATE_DONE = 0
VMETA_THERMAL_CALIB_STATE_REQUESTED = 1
VMETA_THERMAL_CALIB_STATE_IN_PROGRESS = 2
vmeta_thermal_calib_state = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_frame_type'
vmeta_frame_type__enumvalues = {
    0: 'VMETA_FRAME_TYPE_NONE',
    1: 'VMETA_FRAME_TYPE_V1_RECORDING',
    2: 'VMETA_FRAME_TYPE_V1_STREAMING_BASIC',
    3: 'VMETA_FRAME_TYPE_V1_STREAMING_EXTENDED',
    4: 'VMETA_FRAME_TYPE_V2',
    5: 'VMETA_FRAME_TYPE_V3',
    6: 'VMETA_FRAME_TYPE_PROTO',
}
VMETA_FRAME_TYPE_NONE = 0
VMETA_FRAME_TYPE_V1_RECORDING = 1
VMETA_FRAME_TYPE_V1_STREAMING_BASIC = 2
VMETA_FRAME_TYPE_V1_STREAMING_EXTENDED = 3
VMETA_FRAME_TYPE_V2 = 4
VMETA_FRAME_TYPE_V3 = 5
VMETA_FRAME_TYPE_PROTO = 6
vmeta_frame_type = ctypes.c_uint32 # enum
class struct_vmeta_frame_ext_timestamp(Structure):
    pass

struct_vmeta_frame_ext_timestamp._pack_ = True # source:False
struct_vmeta_frame_ext_timestamp._fields_ = [
    ('frame_timestamp', ctypes.c_uint64),
]

class struct_vmeta_frame_ext_followme(Structure):
    pass

struct_vmeta_frame_ext_followme._pack_ = True # source:False
struct_vmeta_frame_ext_followme._fields_ = [
    ('target', struct_vmeta_location),
    ('enabled', ctypes.c_uint32, 1),
    ('mode', ctypes.c_uint32, 1),
    ('angle_locked', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint32, 29),
    ('animation', vmeta_followme_anim),
]

class struct_vmeta_frame_ext_automation(Structure):
    pass

struct_vmeta_frame_ext_automation._pack_ = True # source:False
struct_vmeta_frame_ext_automation._fields_ = [
    ('framing_target', struct_vmeta_location),
    ('flight_destination', struct_vmeta_location),
    ('followme_enabled', ctypes.c_uint32, 1),
    ('lookatme_enabled', ctypes.c_uint32, 1),
    ('angle_locked', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint32, 29),
    ('animation', vmeta_automation_anim),
]

class struct_vmeta_frame_ext_thermal(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('calib_state', vmeta_thermal_calib_state),
        ('min', struct_vmeta_thermal_spot),
        ('max', struct_vmeta_thermal_spot),
        ('probe', struct_vmeta_thermal_spot),
    ]

vmeta_flying_state_str = _libraries['libvideo-metadata.so'].vmeta_flying_state_str
vmeta_flying_state_str.restype = POINTER_T(ctypes.c_char)
vmeta_flying_state_str.argtypes = [vmeta_flying_state]
vmeta_piloting_mode_str = _libraries['libvideo-metadata.so'].vmeta_piloting_mode_str
vmeta_piloting_mode_str.restype = POINTER_T(ctypes.c_char)
vmeta_piloting_mode_str.argtypes = [vmeta_piloting_mode]
vmeta_followme_anim_str = _libraries['libvideo-metadata.so'].vmeta_followme_anim_str
vmeta_followme_anim_str.restype = POINTER_T(ctypes.c_char)
vmeta_followme_anim_str.argtypes = [vmeta_followme_anim]
vmeta_automation_anim_str = _libraries['libvideo-metadata.so'].vmeta_automation_anim_str
vmeta_automation_anim_str.restype = POINTER_T(ctypes.c_char)
vmeta_automation_anim_str.argtypes = [vmeta_automation_anim]
vmeta_thermal_calib_state_str = _libraries['libvideo-metadata.so'].vmeta_thermal_calib_state_str
vmeta_thermal_calib_state_str.restype = POINTER_T(ctypes.c_char)
vmeta_thermal_calib_state_str.argtypes = [vmeta_thermal_calib_state]
vmeta_frame_type_str = _libraries['libvideo-metadata.so'].vmeta_frame_type_str
vmeta_frame_type_str.restype = POINTER_T(ctypes.c_char)
vmeta_frame_type_str.argtypes = [vmeta_frame_type]
class struct_vmeta_frame_proto(Structure):
    pass


# values for enumeration 'c__EA_ProtobufCLabel'
c__EA_ProtobufCLabel__enumvalues = {
    0: 'PROTOBUF_C_LABEL_REQUIRED',
    1: 'PROTOBUF_C_LABEL_OPTIONAL',
    2: 'PROTOBUF_C_LABEL_REPEATED',
    3: 'PROTOBUF_C_LABEL_NONE',
}
PROTOBUF_C_LABEL_REQUIRED = 0
PROTOBUF_C_LABEL_OPTIONAL = 1
PROTOBUF_C_LABEL_REPEATED = 2
PROTOBUF_C_LABEL_NONE = 3
c__EA_ProtobufCLabel = ctypes.c_uint32 # enum

# values for enumeration 'c__EA_ProtobufCType'
c__EA_ProtobufCType__enumvalues = {
    0: 'PROTOBUF_C_TYPE_INT32',
    1: 'PROTOBUF_C_TYPE_SINT32',
    2: 'PROTOBUF_C_TYPE_SFIXED32',
    3: 'PROTOBUF_C_TYPE_INT64',
    4: 'PROTOBUF_C_TYPE_SINT64',
    5: 'PROTOBUF_C_TYPE_SFIXED64',
    6: 'PROTOBUF_C_TYPE_UINT32',
    7: 'PROTOBUF_C_TYPE_FIXED32',
    8: 'PROTOBUF_C_TYPE_UINT64',
    9: 'PROTOBUF_C_TYPE_FIXED64',
    10: 'PROTOBUF_C_TYPE_FLOAT',
    11: 'PROTOBUF_C_TYPE_DOUBLE',
    12: 'PROTOBUF_C_TYPE_BOOL',
    13: 'PROTOBUF_C_TYPE_ENUM',
    14: 'PROTOBUF_C_TYPE_STRING',
    15: 'PROTOBUF_C_TYPE_BYTES',
    16: 'PROTOBUF_C_TYPE_MESSAGE',
}
PROTOBUF_C_TYPE_INT32 = 0
PROTOBUF_C_TYPE_SINT32 = 1
PROTOBUF_C_TYPE_SFIXED32 = 2
PROTOBUF_C_TYPE_INT64 = 3
PROTOBUF_C_TYPE_SINT64 = 4
PROTOBUF_C_TYPE_SFIXED64 = 5
PROTOBUF_C_TYPE_UINT32 = 6
PROTOBUF_C_TYPE_FIXED32 = 7
PROTOBUF_C_TYPE_UINT64 = 8
PROTOBUF_C_TYPE_FIXED64 = 9
PROTOBUF_C_TYPE_FLOAT = 10
PROTOBUF_C_TYPE_DOUBLE = 11
PROTOBUF_C_TYPE_BOOL = 12
PROTOBUF_C_TYPE_ENUM = 13
PROTOBUF_C_TYPE_STRING = 14
PROTOBUF_C_TYPE_BYTES = 15
PROTOBUF_C_TYPE_MESSAGE = 16
c__EA_ProtobufCType = ctypes.c_uint32 # enum
class struct_ProtobufCFieldDescriptor(Structure):
    pass

struct_ProtobufCFieldDescriptor._pack_ = True # source:False
struct_ProtobufCFieldDescriptor._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('id', ctypes.c_uint32),
    ('label', c__EA_ProtobufCLabel),
    ('type', c__EA_ProtobufCType),
    ('quantifier_offset', ctypes.c_uint32),
    ('offset', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('descriptor', POINTER_T(None)),
    ('default_value', POINTER_T(None)),
    ('flags', ctypes.c_uint32),
    ('reserved_flags', ctypes.c_uint32),
    ('reserved2', POINTER_T(None)),
    ('reserved3', POINTER_T(None)),
]

class struct_ProtobufCIntRange(Structure):
    pass

struct_ProtobufCIntRange._pack_ = True # source:False
struct_ProtobufCIntRange._fields_ = [
    ('start_value', ctypes.c_int32),
    ('orig_index', ctypes.c_uint32),
]

class struct_ProtobufCMessageDescriptor(Structure):
    pass

class struct_ProtobufCMessage(Structure):
    pass

struct_ProtobufCMessageDescriptor._pack_ = True # source:False
struct_ProtobufCMessageDescriptor._fields_ = [
    ('magic', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('name', POINTER_T(ctypes.c_char)),
    ('short_name', POINTER_T(ctypes.c_char)),
    ('c_name', POINTER_T(ctypes.c_char)),
    ('package_name', POINTER_T(ctypes.c_char)),
    ('sizeof_message', ctypes.c_uint64),
    ('n_fields', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('fields', POINTER_T(struct_ProtobufCFieldDescriptor)),
    ('fields_sorted_by_name', POINTER_T(ctypes.c_uint32)),
    ('n_field_ranges', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('field_ranges', POINTER_T(struct_ProtobufCIntRange)),
    ('message_init', ctypes.CFUNCTYPE(None, POINTER_T(struct_ProtobufCMessage))),
    ('reserved1', POINTER_T(None)),
    ('reserved2', POINTER_T(None)),
    ('reserved3', POINTER_T(None)),
]


# values for enumeration 'c__EA_ProtobufCWireType'
c__EA_ProtobufCWireType__enumvalues = {
    0: 'PROTOBUF_C_WIRE_TYPE_VARINT',
    1: 'PROTOBUF_C_WIRE_TYPE_64BIT',
    2: 'PROTOBUF_C_WIRE_TYPE_LENGTH_PREFIXED',
    5: 'PROTOBUF_C_WIRE_TYPE_32BIT',
}
PROTOBUF_C_WIRE_TYPE_VARINT = 0
PROTOBUF_C_WIRE_TYPE_64BIT = 1
PROTOBUF_C_WIRE_TYPE_LENGTH_PREFIXED = 2
PROTOBUF_C_WIRE_TYPE_32BIT = 5
c__EA_ProtobufCWireType = ctypes.c_uint32 # enum
class struct_ProtobufCMessageUnknownField(Structure):
    pass

struct_ProtobufCMessageUnknownField._pack_ = True # source:False
struct_ProtobufCMessageUnknownField._fields_ = [
    ('tag', ctypes.c_uint32),
    ('wire_type', c__EA_ProtobufCWireType),
    ('len', ctypes.c_uint64),
    ('data', POINTER_T(ctypes.c_ubyte)),
]

struct_ProtobufCMessage._pack_ = True # source:False
struct_ProtobufCMessage._fields_ = [
    ('descriptor', POINTER_T(struct_ProtobufCMessageDescriptor)),
    ('n_unknown_fields', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('unknown_fields', POINTER_T(struct_ProtobufCMessageUnknownField)),
]

class struct__Vmeta__Quaternion(Structure):
    pass

struct__Vmeta__Quaternion._pack_ = True # source:False
struct__Vmeta__Quaternion._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('w', ctypes.c_float),
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('z', ctypes.c_float),
]

class struct__Vmeta__Location(Structure):
    pass

struct__Vmeta__Location._pack_ = True # source:False
struct__Vmeta__Location._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('latitude', ctypes.c_double),
    ('longitude', ctypes.c_double),
    ('altitude', ctypes.c_double),
    ('horizontal_accuracy', ctypes.c_float),
    ('vertical_accuracy', ctypes.c_float),
    ('sv_count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct__Vmeta__NED(Structure):
    pass

struct__Vmeta__NED._pack_ = True # source:False
struct__Vmeta__NED._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('north', ctypes.c_float),
    ('east', ctypes.c_float),
    ('down', ctypes.c_float),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct__Vmeta__Vector3(Structure):
    pass

struct__Vmeta__Vector3._pack_ = True # source:False
struct__Vmeta__Vector3._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('z', ctypes.c_float),
    ('PADDING_0', ctypes.c_ubyte * 4),
]


# values for enumeration '_Vmeta__FlyingState'
_Vmeta__FlyingState__enumvalues = {
    0: 'VMETA__FLYING_STATE__FS_LANDED',
    1: 'VMETA__FLYING_STATE__FS_TAKINGOFF',
    2: 'VMETA__FLYING_STATE__FS_HOVERING',
    3: 'VMETA__FLYING_STATE__FS_FLYING',
    4: 'VMETA__FLYING_STATE__FS_LANDING',
    5: 'VMETA__FLYING_STATE__FS_EMERGENCY',
    2147483647: '_VMETA__FLYING_STATE_IS_INT_SIZE',
}
VMETA__FLYING_STATE__FS_LANDED = 0
VMETA__FLYING_STATE__FS_TAKINGOFF = 1
VMETA__FLYING_STATE__FS_HOVERING = 2
VMETA__FLYING_STATE__FS_FLYING = 3
VMETA__FLYING_STATE__FS_LANDING = 4
VMETA__FLYING_STATE__FS_EMERGENCY = 5
_VMETA__FLYING_STATE_IS_INT_SIZE = 2147483647
_Vmeta__FlyingState = ctypes.c_uint32 # enum
class struct__Vmeta__DroneMetadata(Structure):
    pass

struct__Vmeta__DroneMetadata._pack_ = True # source:False
struct__Vmeta__DroneMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('quat', POINTER_T(struct__Vmeta__Quaternion)),
    ('location', POINTER_T(struct__Vmeta__Location)),
    ('ground_distance', ctypes.c_double),
    ('position', POINTER_T(struct__Vmeta__NED)),
    ('local_position', POINTER_T(struct__Vmeta__Vector3)),
    ('speed', POINTER_T(struct__Vmeta__NED)),
    ('battery_percentage', ctypes.c_int32),
    ('flying_state', _Vmeta__FlyingState),
]

class struct__Vmeta__CameraMetadata(Structure):
    pass

struct__Vmeta__CameraMetadata._pack_ = True # source:False
struct__Vmeta__CameraMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('timestamp', ctypes.c_uint64),
    ('utc_timestamp', ctypes.c_uint64),
    ('utc_timestamp_accuracy', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('base_quat', POINTER_T(struct__Vmeta__Quaternion)),
    ('quat', POINTER_T(struct__Vmeta__Quaternion)),
    ('exposure_time', ctypes.c_float),
    ('iso_gain', ctypes.c_uint32),
    ('awb_r_gain', ctypes.c_float),
    ('awb_b_gain', ctypes.c_float),
    ('hfov', ctypes.c_float),
    ('vfov', ctypes.c_float),
]


# values for enumeration 'c__EA_Vmeta__LinkMetadata__ProtocolCase'
c__EA_Vmeta__LinkMetadata__ProtocolCase__enumvalues = {
    0: 'VMETA__LINK_METADATA__PROTOCOL__NOT_SET',
    1: 'VMETA__LINK_METADATA__PROTOCOL_WIFI',
    2: 'VMETA__LINK_METADATA__PROTOCOL_STARFISH',
    2147483647: '_VMETA__LINK_METADATA__PROTOCOL_IS_INT_SIZE',
}
VMETA__LINK_METADATA__PROTOCOL__NOT_SET = 0
VMETA__LINK_METADATA__PROTOCOL_WIFI = 1
VMETA__LINK_METADATA__PROTOCOL_STARFISH = 2
_VMETA__LINK_METADATA__PROTOCOL_IS_INT_SIZE = 2147483647
c__EA_Vmeta__LinkMetadata__ProtocolCase = ctypes.c_uint32 # enum
class struct__Vmeta__WifiLinkMetadata(Structure):
    pass

struct__Vmeta__WifiLinkMetadata._pack_ = True # source:False
struct__Vmeta__WifiLinkMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('goodput', ctypes.c_uint32),
    ('quality', ctypes.c_uint32),
    ('rssi', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]


# values for enumeration '_Vmeta__LinkType'
_Vmeta__LinkType__enumvalues = {
    0: 'VMETA__LINK_TYPE__LINK_TYPE_UNKNOWN',
    1: 'VMETA__LINK_TYPE__LINK_TYPE_LO',
    2: 'VMETA__LINK_TYPE__LINK_TYPE_LAN',
    3: 'VMETA__LINK_TYPE__LINK_TYPE_WLAN',
    4: 'VMETA__LINK_TYPE__LINK_TYPE_CELLULAR',
    2147483647: '_VMETA__LINK_TYPE_IS_INT_SIZE',
}
VMETA__LINK_TYPE__LINK_TYPE_UNKNOWN = 0
VMETA__LINK_TYPE__LINK_TYPE_LO = 1
VMETA__LINK_TYPE__LINK_TYPE_LAN = 2
VMETA__LINK_TYPE__LINK_TYPE_WLAN = 3
VMETA__LINK_TYPE__LINK_TYPE_CELLULAR = 4
_VMETA__LINK_TYPE_IS_INT_SIZE = 2147483647
_Vmeta__LinkType = ctypes.c_uint32 # enum

# values for enumeration '_Vmeta__LinkStatus'
_Vmeta__LinkStatus__enumvalues = {
    0: 'VMETA__LINK_STATUS__LINK_STATUS_DOWN',
    1: 'VMETA__LINK_STATUS__LINK_STATUS_UP',
    2: 'VMETA__LINK_STATUS__LINK_STATUS_RUNNING',
    3: 'VMETA__LINK_STATUS__LINK_STATUS_READY',
    4: 'VMETA__LINK_STATUS__LINK_STATUS_CONNECTING',
    5: 'VMETA__LINK_STATUS__LINK_STATUS_ERROR',
    2147483647: '_VMETA__LINK_STATUS_IS_INT_SIZE',
}
VMETA__LINK_STATUS__LINK_STATUS_DOWN = 0
VMETA__LINK_STATUS__LINK_STATUS_UP = 1
VMETA__LINK_STATUS__LINK_STATUS_RUNNING = 2
VMETA__LINK_STATUS__LINK_STATUS_READY = 3
VMETA__LINK_STATUS__LINK_STATUS_CONNECTING = 4
VMETA__LINK_STATUS__LINK_STATUS_ERROR = 5
_VMETA__LINK_STATUS_IS_INT_SIZE = 2147483647
_Vmeta__LinkStatus = ctypes.c_uint32 # enum
class struct__Vmeta__StarfishLinkInfo(Structure):
    pass

struct__Vmeta__StarfishLinkInfo._pack_ = True # source:False
struct__Vmeta__StarfishLinkInfo._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('type', _Vmeta__LinkType),
    ('status', _Vmeta__LinkStatus),
    ('quality', ctypes.c_int32),
    ('active', ctypes.c_int32),
]

class struct__Vmeta__StarfishLinkMetadata(Structure):
    pass

struct__Vmeta__StarfishLinkMetadata._pack_ = True # source:False
struct__Vmeta__StarfishLinkMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('n_links', ctypes.c_uint64),
    ('links', POINTER_T(POINTER_T(struct__Vmeta__StarfishLinkInfo))),
    ('quality', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class union__Vmeta__LinkMetadata_0(Union):
    pass

union__Vmeta__LinkMetadata_0._pack_ = True # source:False
union__Vmeta__LinkMetadata_0._fields_ = [
    ('wifi', POINTER_T(struct__Vmeta__WifiLinkMetadata)),
    ('starfish', POINTER_T(struct__Vmeta__StarfishLinkMetadata)),
]

class struct__Vmeta__LinkMetadata(Structure):
    pass

struct__Vmeta__LinkMetadata._pack_ = True # source:False
struct__Vmeta__LinkMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('protocol_case', c__EA_Vmeta__LinkMetadata__ProtocolCase),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('_Vmeta__LinkMetadata_0', union__Vmeta__LinkMetadata_0),
]


# values for enumeration '_Vmeta__TrackingClass'
_Vmeta__TrackingClass__enumvalues = {
    0: 'VMETA__TRACKING_CLASS__TC_PERSON',
    1: 'VMETA__TRACKING_CLASS__TC_ANIMAL',
    2: 'VMETA__TRACKING_CLASS__TC_BICYCLE',
    3: 'VMETA__TRACKING_CLASS__TC_BOAT',
    4: 'VMETA__TRACKING_CLASS__TC_CAR',
    5: 'VMETA__TRACKING_CLASS__TC_HORSE',
    6: 'VMETA__TRACKING_CLASS__TC_MOTORBIKE',
    127: 'VMETA__TRACKING_CLASS__TC_UNDEFINED',
    2147483647: '_VMETA__TRACKING_CLASS_IS_INT_SIZE',
}
VMETA__TRACKING_CLASS__TC_PERSON = 0
VMETA__TRACKING_CLASS__TC_ANIMAL = 1
VMETA__TRACKING_CLASS__TC_BICYCLE = 2
VMETA__TRACKING_CLASS__TC_BOAT = 3
VMETA__TRACKING_CLASS__TC_CAR = 4
VMETA__TRACKING_CLASS__TC_HORSE = 5
VMETA__TRACKING_CLASS__TC_MOTORBIKE = 6
VMETA__TRACKING_CLASS__TC_UNDEFINED = 127
_VMETA__TRACKING_CLASS_IS_INT_SIZE = 2147483647
_Vmeta__TrackingClass = ctypes.c_uint32 # enum
class struct__Vmeta__BoundingBox(Structure):
    pass

struct__Vmeta__BoundingBox._pack_ = True # source:False
struct__Vmeta__BoundingBox._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('width', ctypes.c_float),
    ('height', ctypes.c_float),
    ('object_class', _Vmeta__TrackingClass),
    ('confidence', ctypes.c_float),
    ('uid', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]


# values for enumeration '_Vmeta__TrackingState'
_Vmeta__TrackingState__enumvalues = {
    0: 'VMETA__TRACKING_STATE__TS_TRACKING',
    1: 'VMETA__TRACKING_STATE__TS_SEARCHING',
    2147483647: '_VMETA__TRACKING_STATE_IS_INT_SIZE',
}
VMETA__TRACKING_STATE__TS_TRACKING = 0
VMETA__TRACKING_STATE__TS_SEARCHING = 1
_VMETA__TRACKING_STATE_IS_INT_SIZE = 2147483647
_Vmeta__TrackingState = ctypes.c_uint32 # enum
class struct__Vmeta__TrackingMetadata(Structure):
    pass

struct__Vmeta__TrackingMetadata._pack_ = True # source:False
struct__Vmeta__TrackingMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('target', POINTER_T(struct__Vmeta__BoundingBox)),
    ('timestamp', ctypes.c_uint64),
    ('quality', ctypes.c_uint32),
    ('state', _Vmeta__TrackingState),
    ('cookie', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct__Vmeta__TrackingProposalMetadata(Structure):
    pass

struct__Vmeta__TrackingProposalMetadata._pack_ = True # source:False
struct__Vmeta__TrackingProposalMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('n_proposals', ctypes.c_uint64),
    ('proposals', POINTER_T(POINTER_T(struct__Vmeta__BoundingBox))),
    ('timestamp', ctypes.c_uint64),
]

class struct__Vmeta__TimedMetadata(Structure):
    pass

struct__Vmeta__TimedMetadata._pack_ = True # source:False
struct__Vmeta__TimedMetadata._fields_ = [
    ('base', struct_ProtobufCMessage),
    ('drone', POINTER_T(struct__Vmeta__DroneMetadata)),
    ('camera', POINTER_T(struct__Vmeta__CameraMetadata)),
    ('n_links', ctypes.c_uint64),
    ('links', POINTER_T(POINTER_T(struct__Vmeta__LinkMetadata))),
    ('tracking', POINTER_T(struct__Vmeta__TrackingMetadata)),
    ('proposal', POINTER_T(struct__Vmeta__TrackingProposalMetadata)),
]

class struct_vmeta_frame(Structure):
    pass

vmeta_frame_proto_get_unpacked = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_unpacked
vmeta_frame_proto_get_unpacked.restype = ctypes.c_int32
vmeta_frame_proto_get_unpacked.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(POINTER_T(struct__Vmeta__TimedMetadata))]
vmeta_frame_proto_release_unpacked = _libraries['libvideo-metadata.so'].vmeta_frame_proto_release_unpacked
vmeta_frame_proto_release_unpacked.restype = ctypes.c_int32
vmeta_frame_proto_release_unpacked.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_unpacked_rw = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_unpacked_rw
vmeta_frame_proto_get_unpacked_rw.restype = ctypes.c_int32
vmeta_frame_proto_get_unpacked_rw.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(POINTER_T(struct__Vmeta__TimedMetadata))]
vmeta_frame_proto_release_unpacked_rw = _libraries['libvideo-metadata.so'].vmeta_frame_proto_release_unpacked_rw
vmeta_frame_proto_release_unpacked_rw.restype = ctypes.c_int32
vmeta_frame_proto_release_unpacked_rw.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_buffer = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_buffer
vmeta_frame_proto_get_buffer.restype = ctypes.c_int32
vmeta_frame_proto_get_buffer.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(POINTER_T(ctypes.c_ubyte)), POINTER_T(ctypes.c_uint64)]
vmeta_frame_proto_release_buffer = _libraries['libvideo-metadata.so'].vmeta_frame_proto_release_buffer
vmeta_frame_proto_release_buffer.restype = ctypes.c_int32
vmeta_frame_proto_release_buffer.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_ubyte)]
vmeta_frame_proto_get_packed_size = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_packed_size
vmeta_frame_proto_get_packed_size.restype = ssize_t
vmeta_frame_proto_get_packed_size.argtypes = [POINTER_T(struct_vmeta_frame)]
vmeta_frame_proto_get_camera = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_camera
vmeta_frame_proto_get_camera.restype = POINTER_T(struct__Vmeta__CameraMetadata)
vmeta_frame_proto_get_camera.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_camera_base_quat = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_camera_base_quat
vmeta_frame_proto_get_camera_base_quat.restype = POINTER_T(struct__Vmeta__Quaternion)
vmeta_frame_proto_get_camera_base_quat.argtypes = [POINTER_T(struct__Vmeta__CameraMetadata)]
vmeta_frame_proto_get_camera_quat = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_camera_quat
vmeta_frame_proto_get_camera_quat.restype = POINTER_T(struct__Vmeta__Quaternion)
vmeta_frame_proto_get_camera_quat.argtypes = [POINTER_T(struct__Vmeta__CameraMetadata)]
vmeta_frame_proto_get_drone = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone
vmeta_frame_proto_get_drone.restype = POINTER_T(struct__Vmeta__DroneMetadata)
vmeta_frame_proto_get_drone.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_drone_location = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone_location
vmeta_frame_proto_get_drone_location.restype = POINTER_T(struct__Vmeta__Location)
vmeta_frame_proto_get_drone_location.argtypes = [POINTER_T(struct__Vmeta__DroneMetadata)]
vmeta_frame_proto_get_drone_quat = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone_quat
vmeta_frame_proto_get_drone_quat.restype = POINTER_T(struct__Vmeta__Quaternion)
vmeta_frame_proto_get_drone_quat.argtypes = [POINTER_T(struct__Vmeta__DroneMetadata)]
vmeta_frame_proto_get_drone_speed = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone_speed
vmeta_frame_proto_get_drone_speed.restype = POINTER_T(struct__Vmeta__NED)
vmeta_frame_proto_get_drone_speed.argtypes = [POINTER_T(struct__Vmeta__DroneMetadata)]
vmeta_frame_proto_get_drone_position = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone_position
vmeta_frame_proto_get_drone_position.restype = POINTER_T(struct__Vmeta__NED)
vmeta_frame_proto_get_drone_position.argtypes = [POINTER_T(struct__Vmeta__DroneMetadata)]
vmeta_frame_proto_get_drone_local_position = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_drone_local_position
vmeta_frame_proto_get_drone_local_position.restype = POINTER_T(struct__Vmeta__Vector3)
vmeta_frame_proto_get_drone_local_position.argtypes = [POINTER_T(struct__Vmeta__DroneMetadata)]
vmeta_frame_proto_add_wifi_link = _libraries['libvideo-metadata.so'].vmeta_frame_proto_add_wifi_link
vmeta_frame_proto_add_wifi_link.restype = POINTER_T(struct__Vmeta__WifiLinkMetadata)
vmeta_frame_proto_add_wifi_link.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_add_starfish_link_info = _libraries['libvideo-metadata.so'].vmeta_frame_proto_add_starfish_link_info
vmeta_frame_proto_add_starfish_link_info.restype = POINTER_T(struct__Vmeta__StarfishLinkInfo)
vmeta_frame_proto_add_starfish_link_info.argtypes = [POINTER_T(struct__Vmeta__StarfishLinkMetadata)]
vmeta_frame_proto_add_starfish_link = _libraries['libvideo-metadata.so'].vmeta_frame_proto_add_starfish_link
vmeta_frame_proto_add_starfish_link.restype = POINTER_T(struct__Vmeta__StarfishLinkMetadata)
vmeta_frame_proto_add_starfish_link.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_tracking = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_tracking
vmeta_frame_proto_get_tracking.restype = POINTER_T(struct__Vmeta__TrackingMetadata)
vmeta_frame_proto_get_tracking.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_get_tracking_target = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_tracking_target
vmeta_frame_proto_get_tracking_target.restype = POINTER_T(struct__Vmeta__BoundingBox)
vmeta_frame_proto_get_tracking_target.argtypes = [POINTER_T(struct__Vmeta__TrackingMetadata)]
vmeta_frame_proto_get_proposal = _libraries['libvideo-metadata.so'].vmeta_frame_proto_get_proposal
vmeta_frame_proto_get_proposal.restype = POINTER_T(struct__Vmeta__TrackingProposalMetadata)
vmeta_frame_proto_get_proposal.argtypes = [POINTER_T(struct__Vmeta__TimedMetadata)]
vmeta_frame_proto_proposal_add_box = _libraries['libvideo-metadata.so'].vmeta_frame_proto_proposal_add_box
vmeta_frame_proto_proposal_add_box.restype = POINTER_T(struct__Vmeta__BoundingBox)
vmeta_frame_proto_proposal_add_box.argtypes = [POINTER_T(struct__Vmeta__TrackingProposalMetadata)]
Vmeta__FlyingState = _Vmeta__FlyingState
Vmeta__FlyingState__enumvalues = _Vmeta__FlyingState__enumvalues
vmeta_frame_flying_state_proto_to_vmeta = _libraries['libvideo-metadata.so'].vmeta_frame_flying_state_proto_to_vmeta
vmeta_frame_flying_state_proto_to_vmeta.restype = vmeta_flying_state
vmeta_frame_flying_state_proto_to_vmeta.argtypes = [Vmeta__FlyingState]
class struct_vmeta_frame_v1_streaming_basic(Structure):
    pass

struct_vmeta_frame_v1_streaming_basic._pack_ = True # source:False
struct_vmeta_frame_v1_streaming_basic._fields_ = [
    ('drone_attitude', struct_vmeta_euler),
    ('frame_quat', struct_vmeta_quaternion),
    ('camera_pan', ctypes.c_float),
    ('camera_tilt', ctypes.c_float),
    ('exposure_time', ctypes.c_float),
    ('gain', ctypes.c_uint16),
    ('wifi_rssi', ctypes.c_byte),
    ('battery_percentage', ctypes.c_ubyte),
]

class struct_vmeta_frame_v1_streaming_extended(Structure):
    pass

struct_vmeta_frame_v1_streaming_extended._pack_ = True # source:False
struct_vmeta_frame_v1_streaming_extended._fields_ = [
    ('drone_attitude', struct_vmeta_euler),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('location', struct_vmeta_location),
    ('altitude', ctypes.c_double),
    ('distance_from_home', ctypes.c_double),
    ('speed', struct_vmeta_xyz),
    ('frame_quat', struct_vmeta_quaternion),
    ('camera_pan', ctypes.c_float),
    ('camera_tilt', ctypes.c_float),
    ('exposure_time', ctypes.c_float),
    ('gain', ctypes.c_uint16),
    ('wifi_rssi', ctypes.c_byte),
    ('battery_percentage', ctypes.c_ubyte),
    ('binning', ctypes.c_uint32, 1),
    ('animation', ctypes.c_uint32, 1),
    ('PADDING_1', ctypes.c_uint32, 30),
    ('state', vmeta_flying_state),
    ('mode', vmeta_piloting_mode),
]

class struct_vmeta_frame_v1_recording(Structure):
    pass

struct_vmeta_frame_v1_recording._pack_ = True # source:False
struct_vmeta_frame_v1_recording._fields_ = [
    ('drone_attitude', struct_vmeta_euler),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('location', struct_vmeta_location),
    ('altitude', ctypes.c_double),
    ('distance_from_home', ctypes.c_double),
    ('speed', struct_vmeta_xyz),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('frame_timestamp', ctypes.c_uint64),
    ('frame_quat', struct_vmeta_quaternion),
    ('camera_pan', ctypes.c_float),
    ('camera_tilt', ctypes.c_float),
    ('exposure_time', ctypes.c_float),
    ('gain', ctypes.c_uint16),
    ('wifi_rssi', ctypes.c_byte),
    ('battery_percentage', ctypes.c_ubyte),
    ('binning', ctypes.c_uint32, 1),
    ('animation', ctypes.c_uint32, 1),
    ('PADDING_2', ctypes.c_uint32, 30),
    ('state', vmeta_flying_state),
    ('mode', vmeta_piloting_mode),
    ('PADDING_3', ctypes.c_ubyte * 4),
]

vmeta_frame_v1_streaming_basic_write = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_basic_write
vmeta_frame_v1_streaming_basic_write.restype = ctypes.c_int32
vmeta_frame_v1_streaming_basic_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_streaming_basic)]
vmeta_frame_v1_streaming_basic_read = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_basic_read
vmeta_frame_v1_streaming_basic_read.restype = ctypes.c_int32
vmeta_frame_v1_streaming_basic_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_streaming_basic)]
vmeta_frame_v1_streaming_basic_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_basic_to_json
vmeta_frame_v1_streaming_basic_to_json.restype = ctypes.c_int32
vmeta_frame_v1_streaming_basic_to_json.argtypes = [POINTER_T(struct_vmeta_frame_v1_streaming_basic), POINTER_T(struct_json_object)]
vmeta_frame_v1_streaming_basic_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_basic_to_csv
vmeta_frame_v1_streaming_basic_to_csv.restype = size_t
vmeta_frame_v1_streaming_basic_to_csv.argtypes = [POINTER_T(struct_vmeta_frame_v1_streaming_basic), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v1_streaming_basic_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_basic_csv_header
vmeta_frame_v1_streaming_basic_csv_header.restype = size_t
vmeta_frame_v1_streaming_basic_csv_header.argtypes = [POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v1_streaming_extended_write = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_extended_write
vmeta_frame_v1_streaming_extended_write.restype = ctypes.c_int32
vmeta_frame_v1_streaming_extended_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_streaming_extended)]
vmeta_frame_v1_streaming_extended_read = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_extended_read
vmeta_frame_v1_streaming_extended_read.restype = ctypes.c_int32
vmeta_frame_v1_streaming_extended_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_streaming_extended)]
vmeta_frame_v1_streaming_extended_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_extended_to_json
vmeta_frame_v1_streaming_extended_to_json.restype = ctypes.c_int32
vmeta_frame_v1_streaming_extended_to_json.argtypes = [POINTER_T(struct_vmeta_frame_v1_streaming_extended), POINTER_T(struct_json_object)]
vmeta_frame_v1_streaming_extended_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_extended_to_csv
vmeta_frame_v1_streaming_extended_to_csv.restype = size_t
vmeta_frame_v1_streaming_extended_to_csv.argtypes = [POINTER_T(struct_vmeta_frame_v1_streaming_extended), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v1_streaming_extended_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_v1_streaming_extended_csv_header
vmeta_frame_v1_streaming_extended_csv_header.restype = size_t
vmeta_frame_v1_streaming_extended_csv_header.argtypes = [POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v1_recording_write = _libraries['libvideo-metadata.so'].vmeta_frame_v1_recording_write
vmeta_frame_v1_recording_write.restype = ctypes.c_int32
vmeta_frame_v1_recording_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_recording)]
vmeta_frame_v1_recording_read = _libraries['libvideo-metadata.so'].vmeta_frame_v1_recording_read
vmeta_frame_v1_recording_read.restype = ctypes.c_int32
vmeta_frame_v1_recording_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v1_recording)]
vmeta_frame_v1_recording_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_v1_recording_to_json
vmeta_frame_v1_recording_to_json.restype = ctypes.c_int32
vmeta_frame_v1_recording_to_json.argtypes = [POINTER_T(struct_vmeta_frame_v1_recording), POINTER_T(struct_json_object)]
vmeta_frame_v1_recording_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_v1_recording_to_csv
vmeta_frame_v1_recording_to_csv.restype = size_t
vmeta_frame_v1_recording_to_csv.argtypes = [POINTER_T(struct_vmeta_frame_v1_recording), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v1_recording_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_v1_recording_csv_header
vmeta_frame_v1_recording_csv_header.restype = size_t
vmeta_frame_v1_recording_csv_header.argtypes = [POINTER_T(ctypes.c_char), size_t]
class struct_vmeta_frame_v2_base(Structure):
    pass

struct_vmeta_frame_v2_base._pack_ = True # source:False
struct_vmeta_frame_v2_base._fields_ = [
    ('drone_quat', struct_vmeta_quaternion),
    ('location', struct_vmeta_location),
    ('ground_distance', ctypes.c_double),
    ('speed', struct_vmeta_ned),
    ('air_speed', ctypes.c_float),
    ('frame_quat', struct_vmeta_quaternion),
    ('camera_pan', ctypes.c_float),
    ('camera_tilt', ctypes.c_float),
    ('exposure_time', ctypes.c_float),
    ('gain', ctypes.c_uint16),
    ('wifi_rssi', ctypes.c_byte),
    ('battery_percentage', ctypes.c_ubyte),
    ('binning', ctypes.c_uint32, 1),
    ('animation', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint32, 30),
    ('state', vmeta_flying_state),
    ('mode', vmeta_piloting_mode),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

class struct_vmeta_frame_v2(Structure):
    pass

struct_vmeta_frame_v2._pack_ = True # source:False
struct_vmeta_frame_v2._fields_ = [
    ('base', struct_vmeta_frame_v2_base),
    ('has_timestamp', ctypes.c_uint32, 1),
    ('has_followme', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint64, 62),
    ('timestamp', struct_vmeta_frame_ext_timestamp),
    ('followme', struct_vmeta_frame_ext_followme),
]

vmeta_frame_v2_write = _libraries['libvideo-metadata.so'].vmeta_frame_v2_write
vmeta_frame_v2_write.restype = ctypes.c_int32
vmeta_frame_v2_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v2)]
vmeta_frame_v2_read = _libraries['libvideo-metadata.so'].vmeta_frame_v2_read
vmeta_frame_v2_read.restype = ctypes.c_int32
vmeta_frame_v2_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v2)]
vmeta_frame_v2_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_v2_to_json
vmeta_frame_v2_to_json.restype = ctypes.c_int32
vmeta_frame_v2_to_json.argtypes = [POINTER_T(struct_vmeta_frame_v2), POINTER_T(struct_json_object)]
vmeta_frame_v2_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_v2_to_csv
vmeta_frame_v2_to_csv.restype = size_t
vmeta_frame_v2_to_csv.argtypes = [POINTER_T(struct_vmeta_frame_v2), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v2_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_v2_csv_header
vmeta_frame_v2_csv_header.restype = size_t
vmeta_frame_v2_csv_header.argtypes = [POINTER_T(ctypes.c_char), size_t]
class struct_vmeta_frame_v3_base(Structure):
    pass

struct_vmeta_frame_v3_base._pack_ = True # source:False
struct_vmeta_frame_v3_base._fields_ = [
    ('drone_quat', struct_vmeta_quaternion),
    ('location', struct_vmeta_location),
    ('ground_distance', ctypes.c_double),
    ('speed', struct_vmeta_ned),
    ('air_speed', ctypes.c_float),
    ('frame_base_quat', struct_vmeta_quaternion),
    ('frame_quat', struct_vmeta_quaternion),
    ('exposure_time', ctypes.c_float),
    ('gain', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('awb_r_gain', ctypes.c_float),
    ('awb_b_gain', ctypes.c_float),
    ('picture_hfov', ctypes.c_float),
    ('picture_vfov', ctypes.c_float),
    ('link_goodput', ctypes.c_uint32),
    ('link_quality', ctypes.c_byte),
    ('wifi_rssi', ctypes.c_byte),
    ('battery_percentage', ctypes.c_ubyte),
    ('animation', ctypes.c_uint32, 1),
    ('PADDING_1', ctypes.c_uint8, 7),
    ('state', vmeta_flying_state),
    ('mode', vmeta_piloting_mode),
]

class struct_vmeta_frame_v3(Structure):
    pass

struct_vmeta_frame_v3._pack_ = True # source:False
struct_vmeta_frame_v3._fields_ = [
    ('base', struct_vmeta_frame_v3_base),
    ('has_timestamp', ctypes.c_uint32, 1),
    ('has_automation', ctypes.c_uint32, 1),
    ('has_thermal', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint64, 61),
    ('timestamp', struct_vmeta_frame_ext_timestamp),
    ('automation', struct_vmeta_frame_ext_automation),
    ('thermal', struct_vmeta_frame_ext_thermal),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

vmeta_frame_v3_write = _libraries['libvideo-metadata.so'].vmeta_frame_v3_write
vmeta_frame_v3_write.restype = ctypes.c_int32
vmeta_frame_v3_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v3)]
vmeta_frame_v3_read = _libraries['libvideo-metadata.so'].vmeta_frame_v3_read
vmeta_frame_v3_read.restype = ctypes.c_int32
vmeta_frame_v3_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame_v3)]
vmeta_frame_v3_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_v3_to_json
vmeta_frame_v3_to_json.restype = ctypes.c_int32
vmeta_frame_v3_to_json.argtypes = [POINTER_T(struct_vmeta_frame_v3), POINTER_T(struct_json_object)]
vmeta_frame_v3_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_v3_to_csv
vmeta_frame_v3_to_csv.restype = size_t
vmeta_frame_v3_to_csv.argtypes = [POINTER_T(struct_vmeta_frame_v3), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_v3_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_v3_csv_header
vmeta_frame_v3_csv_header.restype = size_t
vmeta_frame_v3_csv_header.argtypes = [POINTER_T(ctypes.c_char), size_t]
class union_vmeta_frame_0(Union):
    pass

union_vmeta_frame_0._pack_ = True # source:False
union_vmeta_frame_0._fields_ = [
    ('v1_rec', struct_vmeta_frame_v1_recording),
    ('v1_strm_basic', struct_vmeta_frame_v1_streaming_basic),
    ('v1_strm_ext', struct_vmeta_frame_v1_streaming_extended),
    ('v2', struct_vmeta_frame_v2),
    ('v3', struct_vmeta_frame_v3),
    ('proto', POINTER_T(struct_vmeta_frame_proto)),
    ('PADDING_0', ctypes.c_ubyte * 304),
]

struct_vmeta_frame._pack_ = True # source:False
struct_vmeta_frame._fields_ = [
    ('type', vmeta_frame_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('vmeta_frame_0', union_vmeta_frame_0),
    ('ref_count', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

vmeta_frame_write = _libraries['libvideo-metadata.so'].vmeta_frame_write
vmeta_frame_write.restype = ctypes.c_int32
vmeta_frame_write.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(struct_vmeta_frame)]
vmeta_frame_read = _libraries['libvideo-metadata.so'].vmeta_frame_read
vmeta_frame_read.restype = ctypes.c_int32
vmeta_frame_read.argtypes = [POINTER_T(struct_vmeta_buffer), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_vmeta_frame))]
vmeta_frame_new = _libraries['libvideo-metadata.so'].vmeta_frame_new
vmeta_frame_new.restype = ctypes.c_int32
vmeta_frame_new.argtypes = [vmeta_frame_type, POINTER_T(POINTER_T(struct_vmeta_frame))]
vmeta_frame_ref = _libraries['libvideo-metadata.so'].vmeta_frame_ref
vmeta_frame_ref.restype = ctypes.c_int32
vmeta_frame_ref.argtypes = [POINTER_T(struct_vmeta_frame)]
vmeta_frame_unref = _libraries['libvideo-metadata.so'].vmeta_frame_unref
vmeta_frame_unref.restype = ctypes.c_int32
vmeta_frame_unref.argtypes = [POINTER_T(struct_vmeta_frame)]
vmeta_frame_get_ref_count = _libraries['libvideo-metadata.so'].vmeta_frame_get_ref_count
vmeta_frame_get_ref_count.restype = ctypes.c_int32
vmeta_frame_get_ref_count.argtypes = [POINTER_T(struct_vmeta_frame)]
vmeta_frame_to_json = _libraries['libvideo-metadata.so'].vmeta_frame_to_json
vmeta_frame_to_json.restype = ctypes.c_int32
vmeta_frame_to_json.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_json_object)]
vmeta_frame_to_json_str = _libraries['libvideo-metadata.so'].vmeta_frame_to_json_str
vmeta_frame_to_json_str.restype = ctypes.c_int32
vmeta_frame_to_json_str.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_char), ctypes.c_uint32]
vmeta_frame_to_csv = _libraries['libvideo-metadata.so'].vmeta_frame_to_csv
vmeta_frame_to_csv.restype = ssize_t
vmeta_frame_to_csv.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_char), size_t]
vmeta_frame_csv_header = _libraries['libvideo-metadata.so'].vmeta_frame_csv_header
vmeta_frame_csv_header.restype = ssize_t
vmeta_frame_csv_header.argtypes = [vmeta_frame_type, POINTER_T(ctypes.c_char), size_t]
vmeta_frame_get_mime_type = _libraries['libvideo-metadata.so'].vmeta_frame_get_mime_type
vmeta_frame_get_mime_type.restype = POINTER_T(ctypes.c_char)
vmeta_frame_get_mime_type.argtypes = [vmeta_frame_type]
vmeta_frame_get_location = _libraries['libvideo-metadata.so'].vmeta_frame_get_location
vmeta_frame_get_location.restype = ctypes.c_int32
vmeta_frame_get_location.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_location)]
vmeta_frame_get_speed_ned = _libraries['libvideo-metadata.so'].vmeta_frame_get_speed_ned
vmeta_frame_get_speed_ned.restype = ctypes.c_int32
vmeta_frame_get_speed_ned.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_ned)]
vmeta_frame_get_air_speed = _libraries['libvideo-metadata.so'].vmeta_frame_get_air_speed
vmeta_frame_get_air_speed.restype = ctypes.c_int32
vmeta_frame_get_air_speed.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_ground_distance = _libraries['libvideo-metadata.so'].vmeta_frame_get_ground_distance
vmeta_frame_get_ground_distance.restype = ctypes.c_int32
vmeta_frame_get_ground_distance.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_double)]
vmeta_frame_get_drone_euler = _libraries['libvideo-metadata.so'].vmeta_frame_get_drone_euler
vmeta_frame_get_drone_euler.restype = ctypes.c_int32
vmeta_frame_get_drone_euler.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_euler)]
vmeta_frame_get_drone_quat = _libraries['libvideo-metadata.so'].vmeta_frame_get_drone_quat
vmeta_frame_get_drone_quat.restype = ctypes.c_int32
vmeta_frame_get_drone_quat.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_quaternion)]
vmeta_frame_get_frame_euler = _libraries['libvideo-metadata.so'].vmeta_frame_get_frame_euler
vmeta_frame_get_frame_euler.restype = ctypes.c_int32
vmeta_frame_get_frame_euler.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_euler)]
vmeta_frame_get_frame_quat = _libraries['libvideo-metadata.so'].vmeta_frame_get_frame_quat
vmeta_frame_get_frame_quat.restype = ctypes.c_int32
vmeta_frame_get_frame_quat.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_quaternion)]
vmeta_frame_get_frame_base_euler = _libraries['libvideo-metadata.so'].vmeta_frame_get_frame_base_euler
vmeta_frame_get_frame_base_euler.restype = ctypes.c_int32
vmeta_frame_get_frame_base_euler.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_euler)]
vmeta_frame_get_frame_base_quat = _libraries['libvideo-metadata.so'].vmeta_frame_get_frame_base_quat
vmeta_frame_get_frame_base_quat.restype = ctypes.c_int32
vmeta_frame_get_frame_base_quat.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(struct_vmeta_quaternion)]
vmeta_frame_get_frame_timestamp = _libraries['libvideo-metadata.so'].vmeta_frame_get_frame_timestamp
vmeta_frame_get_frame_timestamp.restype = ctypes.c_int32
vmeta_frame_get_frame_timestamp.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_uint64)]
vmeta_frame_get_camera_pan = _libraries['libvideo-metadata.so'].vmeta_frame_get_camera_pan
vmeta_frame_get_camera_pan.restype = ctypes.c_int32
vmeta_frame_get_camera_pan.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_camera_tilt = _libraries['libvideo-metadata.so'].vmeta_frame_get_camera_tilt
vmeta_frame_get_camera_tilt.restype = ctypes.c_int32
vmeta_frame_get_camera_tilt.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_exposure_time = _libraries['libvideo-metadata.so'].vmeta_frame_get_exposure_time
vmeta_frame_get_exposure_time.restype = ctypes.c_int32
vmeta_frame_get_exposure_time.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_gain = _libraries['libvideo-metadata.so'].vmeta_frame_get_gain
vmeta_frame_get_gain.restype = ctypes.c_int32
vmeta_frame_get_gain.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_uint16)]
vmeta_frame_get_awb_r_gain = _libraries['libvideo-metadata.so'].vmeta_frame_get_awb_r_gain
vmeta_frame_get_awb_r_gain.restype = ctypes.c_int32
vmeta_frame_get_awb_r_gain.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_awb_b_gain = _libraries['libvideo-metadata.so'].vmeta_frame_get_awb_b_gain
vmeta_frame_get_awb_b_gain.restype = ctypes.c_int32
vmeta_frame_get_awb_b_gain.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_picture_h_fov = _libraries['libvideo-metadata.so'].vmeta_frame_get_picture_h_fov
vmeta_frame_get_picture_h_fov.restype = ctypes.c_int32
vmeta_frame_get_picture_h_fov.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_picture_v_fov = _libraries['libvideo-metadata.so'].vmeta_frame_get_picture_v_fov
vmeta_frame_get_picture_v_fov.restype = ctypes.c_int32
vmeta_frame_get_picture_v_fov.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_float)]
vmeta_frame_get_link_goodput = _libraries['libvideo-metadata.so'].vmeta_frame_get_link_goodput
vmeta_frame_get_link_goodput.restype = ctypes.c_int32
vmeta_frame_get_link_goodput.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_uint32)]
vmeta_frame_get_link_quality = _libraries['libvideo-metadata.so'].vmeta_frame_get_link_quality
vmeta_frame_get_link_quality.restype = ctypes.c_int32
vmeta_frame_get_link_quality.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_ubyte)]
vmeta_frame_get_wifi_rssi = _libraries['libvideo-metadata.so'].vmeta_frame_get_wifi_rssi
vmeta_frame_get_wifi_rssi.restype = ctypes.c_int32
vmeta_frame_get_wifi_rssi.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_byte)]
vmeta_frame_get_battery_percentage = _libraries['libvideo-metadata.so'].vmeta_frame_get_battery_percentage
vmeta_frame_get_battery_percentage.restype = ctypes.c_int32
vmeta_frame_get_battery_percentage.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_ubyte)]
vmeta_frame_get_flying_state = _libraries['libvideo-metadata.so'].vmeta_frame_get_flying_state
vmeta_frame_get_flying_state.restype = ctypes.c_int32
vmeta_frame_get_flying_state.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(vmeta_flying_state)]
vmeta_frame_get_piloting_mode = _libraries['libvideo-metadata.so'].vmeta_frame_get_piloting_mode
vmeta_frame_get_piloting_mode.restype = ctypes.c_int32
vmeta_frame_get_piloting_mode.argtypes = [POINTER_T(struct_vmeta_frame), POINTER_T(vmeta_piloting_mode)]

# values for enumeration 'vmeta_session_location_format'
vmeta_session_location_format__enumvalues = {
    0: 'VMETA_SESSION_LOCATION_CSV',
    1: 'VMETA_SESSION_LOCATION_ISO6709',
    2: 'VMETA_SESSION_LOCATION_XYZ',
}
VMETA_SESSION_LOCATION_CSV = 0
VMETA_SESSION_LOCATION_ISO6709 = 1
VMETA_SESSION_LOCATION_XYZ = 2
vmeta_session_location_format = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_stream_sdes_type'
vmeta_stream_sdes_type__enumvalues = {
    0: 'VMETA_STRM_SDES_TYPE_END',
    1: 'VMETA_STRM_SDES_TYPE_CNAME',
    2: 'VMETA_STRM_SDES_TYPE_NAME',
    3: 'VMETA_STRM_SDES_TYPE_EMAIL',
    4: 'VMETA_STRM_SDES_TYPE_PHONE',
    5: 'VMETA_STRM_SDES_TYPE_LOC',
    6: 'VMETA_STRM_SDES_TYPE_TOOL',
    7: 'VMETA_STRM_SDES_TYPE_NOTE',
    8: 'VMETA_STRM_SDES_TYPE_PRIV',
}
VMETA_STRM_SDES_TYPE_END = 0
VMETA_STRM_SDES_TYPE_CNAME = 1
VMETA_STRM_SDES_TYPE_NAME = 2
VMETA_STRM_SDES_TYPE_EMAIL = 3
VMETA_STRM_SDES_TYPE_PHONE = 4
VMETA_STRM_SDES_TYPE_LOC = 5
VMETA_STRM_SDES_TYPE_TOOL = 6
VMETA_STRM_SDES_TYPE_NOTE = 7
VMETA_STRM_SDES_TYPE_PRIV = 8
vmeta_stream_sdes_type = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_stream_sdp_type'
vmeta_stream_sdp_type__enumvalues = {
    0: 'VMETA_STRM_SDP_TYPE_SESSION_INFO',
    1: 'VMETA_STRM_SDP_TYPE_SESSION_NAME',
    2: 'VMETA_STRM_SDP_TYPE_SESSION_TOOL',
    3: 'VMETA_STRM_SDP_TYPE_SESSION_ATTR',
    4: 'VMETA_STRM_SDP_TYPE_MEDIA_INFO',
    5: 'VMETA_STRM_SDP_TYPE_MEDIA_ATTR',
}
VMETA_STRM_SDP_TYPE_SESSION_INFO = 0
VMETA_STRM_SDP_TYPE_SESSION_NAME = 1
VMETA_STRM_SDP_TYPE_SESSION_TOOL = 2
VMETA_STRM_SDP_TYPE_SESSION_ATTR = 3
VMETA_STRM_SDP_TYPE_MEDIA_INFO = 4
VMETA_STRM_SDP_TYPE_MEDIA_ATTR = 5
vmeta_stream_sdp_type = ctypes.c_uint32 # enum

# values for enumeration 'vmeta_record_type'
vmeta_record_type__enumvalues = {
    0: 'VMETA_REC_META',
    1: 'VMETA_REC_UDTA',
    2: 'VMETA_REC_XYZ',
}
VMETA_REC_META = 0
VMETA_REC_UDTA = 1
VMETA_REC_XYZ = 2
vmeta_record_type = ctypes.c_uint32 # enum
class struct_vmeta_thermal_alignment(Structure):
    pass

struct_vmeta_thermal_alignment._pack_ = True # source:False
struct_vmeta_thermal_alignment._fields_ = [
    ('rotation', struct_vmeta_euler),
    ('valid', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_vmeta_thermal_conversion(Structure):
    pass

struct_vmeta_thermal_conversion._pack_ = True # source:False
struct_vmeta_thermal_conversion._fields_ = [
    ('r', ctypes.c_float),
    ('b', ctypes.c_float),
    ('f', ctypes.c_float),
    ('o', ctypes.c_float),
    ('tau_win', ctypes.c_float),
    ('t_win', ctypes.c_float),
    ('t_bg', ctypes.c_float),
    ('emissivity', ctypes.c_float),
    ('valid', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_vmeta_thermal(Structure):
    pass

struct_vmeta_thermal._pack_ = True # source:False
struct_vmeta_thermal._fields_ = [
    ('metaversion', ctypes.c_int32),
    ('camserial', ctypes.c_char * 50),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('alignment', struct_vmeta_thermal_alignment),
    ('conv_low', struct_vmeta_thermal_conversion),
    ('conv_high', struct_vmeta_thermal_conversion),
    ('scale_factor', ctypes.c_double),
]

class struct_vmeta_session(Structure):
    pass

struct_vmeta_session._pack_ = True # source:False
struct_vmeta_session._fields_ = [
    ('friendly_name', ctypes.c_char * 40),
    ('maker', ctypes.c_char * 40),
    ('model', ctypes.c_char * 40),
    ('model_id', ctypes.c_char * 5),
    ('serial_number', ctypes.c_char * 32),
    ('software_version', ctypes.c_char * 20),
    ('build_id', ctypes.c_char * 48),
    ('title', ctypes.c_char * 80),
    ('comment', ctypes.c_char * 100),
    ('copyright', ctypes.c_char * 80),
    ('PADDING_0', ctypes.c_ubyte * 3),
    ('media_date', ctypes.c_int64),
    ('media_date_gmtoff', ctypes.c_int64),
    ('run_date', ctypes.c_int64),
    ('run_date_gmtoff', ctypes.c_int64),
    ('run_id', ctypes.c_char * 33),
    ('boot_id', ctypes.c_char * 33),
    ('flight_id', ctypes.c_char * 33),
    ('custom_id', ctypes.c_char * 80),
    ('PADDING_1', ctypes.c_ubyte * 5),
    ('takeoff_loc', struct_vmeta_location),
    ('picture_fov', struct_vmeta_fov),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('thermal', struct_vmeta_thermal),
    ('has_thermal', ctypes.c_uint32, 1),
    ('PADDING_3', ctypes.c_uint32, 31),
    ('camera_type', vmeta_camera_type),
    ('video_mode', vmeta_video_mode),
    ('video_stop_reason', vmeta_video_stop_reason),
    ('dynamic_range', vmeta_dynamic_range),
    ('tone_mapping', vmeta_tone_mapping),
]

time_t = ctypes.c_int64
vmeta_session_date_write = _libraries['libvideo-metadata.so'].vmeta_session_date_write
vmeta_session_date_write.restype = ssize_t
vmeta_session_date_write.argtypes = [POINTER_T(ctypes.c_char), size_t, time_t, ctypes.c_int64]
vmeta_session_date_read = _libraries['libvideo-metadata.so'].vmeta_session_date_read
vmeta_session_date_read.restype = ctypes.c_int32
vmeta_session_date_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_int64), POINTER_T(ctypes.c_int64)]
vmeta_session_location_write = _libraries['libvideo-metadata.so'].vmeta_session_location_write
vmeta_session_location_write.restype = ssize_t
vmeta_session_location_write.argtypes = [POINTER_T(ctypes.c_char), size_t, vmeta_session_location_format, POINTER_T(struct_vmeta_location)]
vmeta_session_location_read = _libraries['libvideo-metadata.so'].vmeta_session_location_read
vmeta_session_location_read.restype = ctypes.c_int32
vmeta_session_location_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_location)]
vmeta_session_fov_write = _libraries['libvideo-metadata.so'].vmeta_session_fov_write
vmeta_session_fov_write.restype = ssize_t
vmeta_session_fov_write.argtypes = [POINTER_T(ctypes.c_char), size_t, POINTER_T(struct_vmeta_fov)]
vmeta_session_fov_read = _libraries['libvideo-metadata.so'].vmeta_session_fov_read
vmeta_session_fov_read.restype = ctypes.c_int32
vmeta_session_fov_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_fov)]
vmeta_session_thermal_alignment_write = _libraries['libvideo-metadata.so'].vmeta_session_thermal_alignment_write
vmeta_session_thermal_alignment_write.restype = ssize_t
vmeta_session_thermal_alignment_write.argtypes = [POINTER_T(ctypes.c_char), size_t, POINTER_T(struct_vmeta_thermal_alignment)]
vmeta_session_thermal_alignment_read = _libraries['libvideo-metadata.so'].vmeta_session_thermal_alignment_read
vmeta_session_thermal_alignment_read.restype = ctypes.c_int32
vmeta_session_thermal_alignment_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_thermal_alignment)]
vmeta_session_thermal_conversion_write = _libraries['libvideo-metadata.so'].vmeta_session_thermal_conversion_write
vmeta_session_thermal_conversion_write.restype = ssize_t
vmeta_session_thermal_conversion_write.argtypes = [POINTER_T(ctypes.c_char), size_t, POINTER_T(struct_vmeta_thermal_conversion)]
vmeta_session_thermal_conversion_read = _libraries['libvideo-metadata.so'].vmeta_session_thermal_conversion_read
vmeta_session_thermal_conversion_read.restype = ctypes.c_int32
vmeta_session_thermal_conversion_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_thermal_conversion)]
vmeta_session_thermal_scale_factor_write = _libraries['libvideo-metadata.so'].vmeta_session_thermal_scale_factor_write
vmeta_session_thermal_scale_factor_write.restype = ssize_t
vmeta_session_thermal_scale_factor_write.argtypes = [POINTER_T(ctypes.c_char), size_t, ctypes.c_double]
vmeta_session_thermal_scale_factor_read = _libraries['libvideo-metadata.so'].vmeta_session_thermal_scale_factor_read
vmeta_session_thermal_scale_factor_read.restype = ctypes.c_int32
vmeta_session_thermal_scale_factor_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_double)]
vmeta_session_streaming_sdes_write_cb_t = ctypes.CFUNCTYPE(None, vmeta_stream_sdes_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(None))
vmeta_session_streaming_sdes_write = _libraries['libvideo-metadata.so'].vmeta_session_streaming_sdes_write
vmeta_session_streaming_sdes_write.restype = ctypes.c_int32
vmeta_session_streaming_sdes_write.argtypes = [POINTER_T(struct_vmeta_session), vmeta_session_streaming_sdes_write_cb_t, POINTER_T(None)]
vmeta_session_streaming_sdes_read = _libraries['libvideo-metadata.so'].vmeta_session_streaming_sdes_read
vmeta_session_streaming_sdes_read.restype = ctypes.c_int32
vmeta_session_streaming_sdes_read.argtypes = [vmeta_stream_sdes_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_session)]
vmeta_session_streaming_sdp_write_cb_t = ctypes.CFUNCTYPE(None, vmeta_stream_sdp_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(None))
vmeta_session_streaming_sdp_write = _libraries['libvideo-metadata.so'].vmeta_session_streaming_sdp_write
vmeta_session_streaming_sdp_write.restype = ctypes.c_int32
vmeta_session_streaming_sdp_write.argtypes = [POINTER_T(struct_vmeta_session), ctypes.c_int32, vmeta_session_streaming_sdp_write_cb_t, POINTER_T(None)]
vmeta_session_streaming_sdp_read = _libraries['libvideo-metadata.so'].vmeta_session_streaming_sdp_read
vmeta_session_streaming_sdp_read.restype = ctypes.c_int32
vmeta_session_streaming_sdp_read.argtypes = [vmeta_stream_sdp_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_session)]
vmeta_session_recording_write_cb_t = ctypes.CFUNCTYPE(None, vmeta_record_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(None))
vmeta_session_recording_write = _libraries['libvideo-metadata.so'].vmeta_session_recording_write
vmeta_session_recording_write.restype = ctypes.c_int32
vmeta_session_recording_write.argtypes = [POINTER_T(struct_vmeta_session), vmeta_session_recording_write_cb_t, POINTER_T(None)]
vmeta_session_recording_read = _libraries['libvideo-metadata.so'].vmeta_session_recording_read
vmeta_session_recording_read.restype = ctypes.c_int32
vmeta_session_recording_read.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(struct_vmeta_session)]
vmeta_session_to_json = _libraries['libvideo-metadata.so'].vmeta_session_to_json
vmeta_session_to_json.restype = ctypes.c_int32
vmeta_session_to_json.argtypes = [POINTER_T(struct_vmeta_session), POINTER_T(struct_json_object)]
vmeta_session_to_str = _libraries['libvideo-metadata.so'].vmeta_session_to_str
vmeta_session_to_str.restype = ctypes.c_int32
vmeta_session_to_str.argtypes = [POINTER_T(struct_vmeta_session), POINTER_T(ctypes.c_char), size_t]
class struct_mbuf_coded_video_frame(Structure):
    pass

class struct_mbuf_coded_video_frame_queue(Structure):
    pass

mbuf_coded_video_frame_pre_release_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None))
mbuf_coded_video_frame_queue_filter_t = ctypes.CFUNCTYPE(ctypes.c_bool, POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None))
class struct_mbuf_coded_video_frame_cbs(Structure):
    pass

struct_mbuf_coded_video_frame_cbs._pack_ = True # source:False
struct_mbuf_coded_video_frame_cbs._fields_ = [
    ('pre_release', ctypes.CFUNCTYPE(None, POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None))),
    ('pre_release_userdata', POINTER_T(None)),
]

class struct_mbuf_coded_video_frame_queue_args(Structure):
    pass

struct_mbuf_coded_video_frame_queue_args._pack_ = True # source:False
struct_mbuf_coded_video_frame_queue_args._fields_ = [
    ('filter', ctypes.CFUNCTYPE(ctypes.c_bool, POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None))),
    ('filter_userdata', POINTER_T(None)),
    ('max_frames', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

mbuf_coded_video_frame_new = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_new
mbuf_coded_video_frame_new.restype = ctypes.c_int32
mbuf_coded_video_frame_new.argtypes = [POINTER_T(struct_vdef_coded_frame), POINTER_T(POINTER_T(struct_mbuf_coded_video_frame))]
mbuf_coded_video_frame_set_callbacks = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_set_callbacks
mbuf_coded_video_frame_set_callbacks.restype = ctypes.c_int32
mbuf_coded_video_frame_set_callbacks.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_coded_video_frame_cbs)]
mbuf_coded_video_frame_ref = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_ref
mbuf_coded_video_frame_ref.restype = ctypes.c_int32
mbuf_coded_video_frame_ref.argtypes = [POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_unref = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_unref
mbuf_coded_video_frame_unref.restype = ctypes.c_int32
mbuf_coded_video_frame_unref.argtypes = [POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_set_frame_info = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_set_frame_info
mbuf_coded_video_frame_set_frame_info.restype = ctypes.c_int32
mbuf_coded_video_frame_set_frame_info.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_vdef_coded_frame)]
mbuf_coded_video_frame_set_metadata = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_set_metadata
mbuf_coded_video_frame_set_metadata.restype = ctypes.c_int32
mbuf_coded_video_frame_set_metadata.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_vmeta_frame)]
mbuf_coded_video_frame_add_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_add_nalu
mbuf_coded_video_frame_add_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_add_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_mem), size_t, POINTER_T(struct_vdef_nalu)]
mbuf_coded_video_frame_insert_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_insert_nalu
mbuf_coded_video_frame_insert_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_insert_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_mem), size_t, POINTER_T(struct_vdef_nalu), ctypes.c_uint32]
mbuf_coded_video_frame_finalize = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_finalize
mbuf_coded_video_frame_finalize.restype = ctypes.c_int32
mbuf_coded_video_frame_finalize.argtypes = [POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_uses_mem_from_pool = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_uses_mem_from_pool
mbuf_coded_video_frame_uses_mem_from_pool.restype = ctypes.c_int32
mbuf_coded_video_frame_uses_mem_from_pool.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_pool), POINTER_T(ctypes.c_bool), POINTER_T(ctypes.c_bool)]
mbuf_coded_video_frame_get_metadata = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_metadata
mbuf_coded_video_frame_get_metadata.restype = ctypes.c_int32
mbuf_coded_video_frame_get_metadata.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(POINTER_T(struct_vmeta_frame))]
mbuf_coded_video_frame_get_nalu_count = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_nalu_count
mbuf_coded_video_frame_get_nalu_count.restype = ctypes.c_int32
mbuf_coded_video_frame_get_nalu_count.argtypes = [POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_get_nalu_mem_info = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_nalu_mem_info
mbuf_coded_video_frame_get_nalu_mem_info.restype = ctypes.c_int32
mbuf_coded_video_frame_get_nalu_mem_info.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), ctypes.c_uint32, POINTER_T(struct_mbuf_mem_info)]
mbuf_coded_video_frame_get_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_nalu
mbuf_coded_video_frame_get_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_get_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), ctypes.c_uint32, POINTER_T(POINTER_T(None)), POINTER_T(struct_vdef_nalu)]
mbuf_coded_video_frame_release_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_release_nalu
mbuf_coded_video_frame_release_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_release_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), ctypes.c_uint32, POINTER_T(None)]
mbuf_coded_video_frame_get_rw_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_rw_nalu
mbuf_coded_video_frame_get_rw_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_get_rw_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), ctypes.c_uint32, POINTER_T(POINTER_T(None)), POINTER_T(struct_vdef_nalu)]
mbuf_coded_video_frame_release_rw_nalu = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_release_rw_nalu
mbuf_coded_video_frame_release_rw_nalu.restype = ctypes.c_int32
mbuf_coded_video_frame_release_rw_nalu.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), ctypes.c_uint32, POINTER_T(None)]
mbuf_coded_video_frame_get_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_packed_buffer
mbuf_coded_video_frame_get_packed_buffer.restype = ctypes.c_int32
mbuf_coded_video_frame_get_packed_buffer.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_coded_video_frame_release_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_release_packed_buffer
mbuf_coded_video_frame_release_packed_buffer.restype = ctypes.c_int32
mbuf_coded_video_frame_release_packed_buffer.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None)]
mbuf_coded_video_frame_get_rw_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_rw_packed_buffer
mbuf_coded_video_frame_get_rw_packed_buffer.restype = ctypes.c_int32
mbuf_coded_video_frame_get_rw_packed_buffer.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_coded_video_frame_release_rw_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_release_rw_packed_buffer
mbuf_coded_video_frame_release_rw_packed_buffer.restype = ctypes.c_int32
mbuf_coded_video_frame_release_rw_packed_buffer.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(None)]
mbuf_coded_video_frame_get_packed_size = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_packed_size
mbuf_coded_video_frame_get_packed_size.restype = ssize_t
mbuf_coded_video_frame_get_packed_size.argtypes = [POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_copy = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_copy
mbuf_coded_video_frame_copy.restype = ctypes.c_int32
mbuf_coded_video_frame_copy.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_mem), POINTER_T(POINTER_T(struct_mbuf_coded_video_frame))]
mbuf_coded_video_frame_get_frame_info = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_frame_info
mbuf_coded_video_frame_get_frame_info.restype = ctypes.c_int32
mbuf_coded_video_frame_get_frame_info.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_vdef_coded_frame)]
mbuf_coded_video_frame_add_ancillary_string = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_add_ancillary_string
mbuf_coded_video_frame_add_ancillary_string.restype = ctypes.c_int32
mbuf_coded_video_frame_add_ancillary_string.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char)]
mbuf_coded_video_frame_add_ancillary_buffer = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_add_ancillary_buffer
mbuf_coded_video_frame_add_ancillary_buffer.restype = ctypes.c_int32
mbuf_coded_video_frame_add_ancillary_buffer.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(ctypes.c_char), POINTER_T(None), size_t]
mbuf_coded_video_frame_add_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_add_ancillary_data
mbuf_coded_video_frame_add_ancillary_data.restype = ctypes.c_int32
mbuf_coded_video_frame_add_ancillary_data.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(struct_mbuf_ancillary_data)]
mbuf_coded_video_frame_get_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_get_ancillary_data
mbuf_coded_video_frame_get_ancillary_data.restype = ctypes.c_int32
mbuf_coded_video_frame_get_ancillary_data.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_mbuf_ancillary_data))]
mbuf_coded_video_frame_remove_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_remove_ancillary_data
mbuf_coded_video_frame_remove_ancillary_data.restype = ctypes.c_int32
mbuf_coded_video_frame_remove_ancillary_data.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), POINTER_T(ctypes.c_char)]
mbuf_coded_video_frame_foreach_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_foreach_ancillary_data
mbuf_coded_video_frame_foreach_ancillary_data.restype = ctypes.c_int32
mbuf_coded_video_frame_foreach_ancillary_data.argtypes = [POINTER_T(struct_mbuf_coded_video_frame), mbuf_ancillary_data_cb_t, POINTER_T(None)]
mbuf_coded_video_frame_ancillary_data_copier = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_ancillary_data_copier
mbuf_coded_video_frame_ancillary_data_copier.restype = ctypes.c_bool
mbuf_coded_video_frame_ancillary_data_copier.argtypes = [POINTER_T(struct_mbuf_ancillary_data), POINTER_T(None)]
mbuf_coded_video_frame_queue_new = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_new
mbuf_coded_video_frame_queue_new.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_new.argtypes = [POINTER_T(POINTER_T(struct_mbuf_coded_video_frame_queue))]
mbuf_coded_video_frame_queue_new_with_args = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_new_with_args
mbuf_coded_video_frame_queue_new_with_args.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_new_with_args.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue_args), POINTER_T(POINTER_T(struct_mbuf_coded_video_frame_queue))]
mbuf_coded_video_frame_queue_push = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_push
mbuf_coded_video_frame_queue_push.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_push.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue), POINTER_T(struct_mbuf_coded_video_frame)]
mbuf_coded_video_frame_queue_peek = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_peek
mbuf_coded_video_frame_queue_peek.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_peek.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue), POINTER_T(POINTER_T(struct_mbuf_coded_video_frame))]
mbuf_coded_video_frame_queue_pop = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_pop
mbuf_coded_video_frame_queue_pop.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_pop.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue), POINTER_T(POINTER_T(struct_mbuf_coded_video_frame))]
mbuf_coded_video_frame_queue_flush = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_flush
mbuf_coded_video_frame_queue_flush.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_flush.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue)]
mbuf_coded_video_frame_queue_get_event = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_get_event
mbuf_coded_video_frame_queue_get_event.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_get_event.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue), POINTER_T(POINTER_T(struct_pomp_evt))]
mbuf_coded_video_frame_queue_destroy = _libraries['libmedia-buffers.so'].mbuf_coded_video_frame_queue_destroy
mbuf_coded_video_frame_queue_destroy.restype = ctypes.c_int32
mbuf_coded_video_frame_queue_destroy.argtypes = [POINTER_T(struct_mbuf_coded_video_frame_queue)]
class struct_mbuf_raw_video_frame(Structure):
    pass

class struct_mbuf_raw_video_frame_queue(Structure):
    pass

mbuf_raw_video_frame_pre_release_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None))
mbuf_raw_video_frame_queue_filter_t = ctypes.CFUNCTYPE(ctypes.c_bool, POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None))
class struct_mbuf_raw_video_frame_cbs(Structure):
    pass

struct_mbuf_raw_video_frame_cbs._pack_ = True # source:False
struct_mbuf_raw_video_frame_cbs._fields_ = [
    ('pre_release', ctypes.CFUNCTYPE(None, POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None))),
    ('pre_release_userdata', POINTER_T(None)),
]

class struct_mbuf_raw_video_frame_queue_args(Structure):
    pass

struct_mbuf_raw_video_frame_queue_args._pack_ = True # source:False
struct_mbuf_raw_video_frame_queue_args._fields_ = [
    ('filter', ctypes.CFUNCTYPE(ctypes.c_bool, POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None))),
    ('filter_userdata', POINTER_T(None)),
    ('max_frames', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

mbuf_raw_video_frame_new = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_new
mbuf_raw_video_frame_new.restype = ctypes.c_int32
mbuf_raw_video_frame_new.argtypes = [POINTER_T(struct_vdef_raw_frame), POINTER_T(POINTER_T(struct_mbuf_raw_video_frame))]
mbuf_raw_video_frame_set_callbacks = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_set_callbacks
mbuf_raw_video_frame_set_callbacks.restype = ctypes.c_int32
mbuf_raw_video_frame_set_callbacks.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_mbuf_raw_video_frame_cbs)]
mbuf_raw_video_frame_ref = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_ref
mbuf_raw_video_frame_ref.restype = ctypes.c_int32
mbuf_raw_video_frame_ref.argtypes = [POINTER_T(struct_mbuf_raw_video_frame)]
mbuf_raw_video_frame_unref = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_unref
mbuf_raw_video_frame_unref.restype = ctypes.c_int32
mbuf_raw_video_frame_unref.argtypes = [POINTER_T(struct_mbuf_raw_video_frame)]
mbuf_raw_video_frame_set_frame_info = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_set_frame_info
mbuf_raw_video_frame_set_frame_info.restype = ctypes.c_int32
mbuf_raw_video_frame_set_frame_info.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_vdef_raw_frame)]
mbuf_raw_video_frame_set_metadata = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_set_metadata
mbuf_raw_video_frame_set_metadata.restype = ctypes.c_int32
mbuf_raw_video_frame_set_metadata.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_vmeta_frame)]
mbuf_raw_video_frame_set_plane = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_set_plane
mbuf_raw_video_frame_set_plane.restype = ctypes.c_int32
mbuf_raw_video_frame_set_plane.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(struct_mbuf_mem), size_t, size_t]
mbuf_raw_video_frame_finalize = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_finalize
mbuf_raw_video_frame_finalize.restype = ctypes.c_int32
mbuf_raw_video_frame_finalize.argtypes = [POINTER_T(struct_mbuf_raw_video_frame)]
mbuf_raw_video_frame_uses_mem_from_pool = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_uses_mem_from_pool
mbuf_raw_video_frame_uses_mem_from_pool.restype = ctypes.c_int32
mbuf_raw_video_frame_uses_mem_from_pool.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_mbuf_pool), POINTER_T(ctypes.c_bool), POINTER_T(ctypes.c_bool)]
mbuf_raw_video_frame_get_metadata = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_metadata
mbuf_raw_video_frame_get_metadata.restype = ctypes.c_int32
mbuf_raw_video_frame_get_metadata.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(POINTER_T(struct_vmeta_frame))]
mbuf_raw_video_frame_get_plane_mem_info = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_plane_mem_info
mbuf_raw_video_frame_get_plane_mem_info.restype = ctypes.c_int32
mbuf_raw_video_frame_get_plane_mem_info.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(struct_mbuf_mem_info)]
mbuf_raw_video_frame_get_plane = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_plane
mbuf_raw_video_frame_get_plane.restype = ctypes.c_int32
mbuf_raw_video_frame_get_plane.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_raw_video_frame_release_plane = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_release_plane
mbuf_raw_video_frame_release_plane.restype = ctypes.c_int32
mbuf_raw_video_frame_release_plane.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(None)]
mbuf_raw_video_frame_get_rw_plane = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_rw_plane
mbuf_raw_video_frame_get_rw_plane.restype = ctypes.c_int32
mbuf_raw_video_frame_get_rw_plane.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_raw_video_frame_release_rw_plane = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_release_rw_plane
mbuf_raw_video_frame_release_rw_plane.restype = ctypes.c_int32
mbuf_raw_video_frame_release_rw_plane.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_uint32, POINTER_T(None)]
mbuf_raw_video_frame_get_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_packed_buffer
mbuf_raw_video_frame_get_packed_buffer.restype = ctypes.c_int32
mbuf_raw_video_frame_get_packed_buffer.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_raw_video_frame_release_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_release_packed_buffer
mbuf_raw_video_frame_release_packed_buffer.restype = ctypes.c_int32
mbuf_raw_video_frame_release_packed_buffer.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None)]
mbuf_raw_video_frame_get_rw_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_rw_packed_buffer
mbuf_raw_video_frame_get_rw_packed_buffer.restype = ctypes.c_int32
mbuf_raw_video_frame_get_rw_packed_buffer.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(POINTER_T(None)), POINTER_T(ctypes.c_uint64)]
mbuf_raw_video_frame_release_rw_packed_buffer = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_release_rw_packed_buffer
mbuf_raw_video_frame_release_rw_packed_buffer.restype = ctypes.c_int32
mbuf_raw_video_frame_release_rw_packed_buffer.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None)]
mbuf_raw_video_frame_get_packed_size = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_packed_size
mbuf_raw_video_frame_get_packed_size.restype = ssize_t
mbuf_raw_video_frame_get_packed_size.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), ctypes.c_bool]
mbuf_raw_video_frame_copy = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_copy
mbuf_raw_video_frame_copy.restype = ctypes.c_int32
mbuf_raw_video_frame_copy.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_mbuf_mem), ctypes.c_bool, POINTER_T(POINTER_T(struct_mbuf_raw_video_frame))]
mbuf_raw_video_frame_get_frame_info = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_frame_info
mbuf_raw_video_frame_get_frame_info.restype = ctypes.c_int32
mbuf_raw_video_frame_get_frame_info.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_vdef_raw_frame)]
mbuf_raw_video_frame_add_ancillary_string = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_add_ancillary_string
mbuf_raw_video_frame_add_ancillary_string.restype = ctypes.c_int32
mbuf_raw_video_frame_add_ancillary_string.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char)]
mbuf_raw_video_frame_add_ancillary_buffer = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_add_ancillary_buffer
mbuf_raw_video_frame_add_ancillary_buffer.restype = ctypes.c_int32
mbuf_raw_video_frame_add_ancillary_buffer.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(ctypes.c_char), POINTER_T(None), size_t]
mbuf_raw_video_frame_add_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_add_ancillary_data
mbuf_raw_video_frame_add_ancillary_data.restype = ctypes.c_int32
mbuf_raw_video_frame_add_ancillary_data.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(struct_mbuf_ancillary_data)]
mbuf_raw_video_frame_get_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_get_ancillary_data
mbuf_raw_video_frame_get_ancillary_data.restype = ctypes.c_int32
mbuf_raw_video_frame_get_ancillary_data.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_mbuf_ancillary_data))]
mbuf_raw_video_frame_remove_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_remove_ancillary_data
mbuf_raw_video_frame_remove_ancillary_data.restype = ctypes.c_int32
mbuf_raw_video_frame_remove_ancillary_data.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(ctypes.c_char)]
mbuf_raw_video_frame_foreach_ancillary_data = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_foreach_ancillary_data
mbuf_raw_video_frame_foreach_ancillary_data.restype = ctypes.c_int32
mbuf_raw_video_frame_foreach_ancillary_data.argtypes = [POINTER_T(struct_mbuf_raw_video_frame), mbuf_ancillary_data_cb_t, POINTER_T(None)]
mbuf_raw_video_frame_ancillary_data_copier = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_ancillary_data_copier
mbuf_raw_video_frame_ancillary_data_copier.restype = ctypes.c_bool
mbuf_raw_video_frame_ancillary_data_copier.argtypes = [POINTER_T(struct_mbuf_ancillary_data), POINTER_T(None)]
mbuf_raw_video_frame_queue_new = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_new
mbuf_raw_video_frame_queue_new.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_new.argtypes = [POINTER_T(POINTER_T(struct_mbuf_raw_video_frame_queue))]
mbuf_raw_video_frame_queue_new_with_args = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_new_with_args
mbuf_raw_video_frame_queue_new_with_args.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_new_with_args.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue_args), POINTER_T(POINTER_T(struct_mbuf_raw_video_frame_queue))]
mbuf_raw_video_frame_queue_push = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_push
mbuf_raw_video_frame_queue_push.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_push.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue), POINTER_T(struct_mbuf_raw_video_frame)]
mbuf_raw_video_frame_queue_peek = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_peek
mbuf_raw_video_frame_queue_peek.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_peek.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue), POINTER_T(POINTER_T(struct_mbuf_raw_video_frame))]
mbuf_raw_video_frame_queue_pop = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_pop
mbuf_raw_video_frame_queue_pop.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_pop.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue), POINTER_T(POINTER_T(struct_mbuf_raw_video_frame))]
mbuf_raw_video_frame_queue_flush = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_flush
mbuf_raw_video_frame_queue_flush.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_flush.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue)]
mbuf_raw_video_frame_queue_get_event = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_get_event
mbuf_raw_video_frame_queue_get_event.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_get_event.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue), POINTER_T(POINTER_T(struct_pomp_evt))]
mbuf_raw_video_frame_queue_destroy = _libraries['libmedia-buffers.so'].mbuf_raw_video_frame_queue_destroy
mbuf_raw_video_frame_queue_destroy.restype = ctypes.c_int32
mbuf_raw_video_frame_queue_destroy.argtypes = [POINTER_T(struct_mbuf_raw_video_frame_queue)]
class struct_egl_display(Structure):
    pass

class struct_mux_ctx(Structure):
    pass

PDRAW_ANCILLARY_DATA_KEY_VIDEOFRAME = (POINTER_T(ctypes.c_char)).in_dll(_libraries['libpdraw.so'], 'PDRAW_ANCILLARY_DATA_KEY_VIDEOFRAME')

# values for enumeration 'pdraw_hmd_model'
pdraw_hmd_model__enumvalues = {
    0: 'PDRAW_HMD_MODEL_UNKNOWN',
    0: 'PDRAW_HMD_MODEL_COCKPITGLASSES',
    1: 'PDRAW_HMD_MODEL_COCKPITGLASSES_2',
}
PDRAW_HMD_MODEL_UNKNOWN = 0
PDRAW_HMD_MODEL_COCKPITGLASSES = 0
PDRAW_HMD_MODEL_COCKPITGLASSES_2 = 1
pdraw_hmd_model = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_pipeline_mode'
pdraw_pipeline_mode__enumvalues = {
    0: 'PDRAW_PIPELINE_MODE_DECODE_ALL',
    1: 'PDRAW_PIPELINE_MODE_DECODE_NONE',
}
PDRAW_PIPELINE_MODE_DECODE_ALL = 0
PDRAW_PIPELINE_MODE_DECODE_NONE = 1
pdraw_pipeline_mode = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_playback_type'
pdraw_playback_type__enumvalues = {
    0: 'PDRAW_PLAYBACK_TYPE_UNKNOWN',
    1: 'PDRAW_PLAYBACK_TYPE_LIVE',
    2: 'PDRAW_PLAYBACK_TYPE_REPLAY',
}
PDRAW_PLAYBACK_TYPE_UNKNOWN = 0
PDRAW_PLAYBACK_TYPE_LIVE = 1
PDRAW_PLAYBACK_TYPE_REPLAY = 2
pdraw_playback_type = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_media_type'
pdraw_media_type__enumvalues = {
    0: 'PDRAW_MEDIA_TYPE_UNKNOWN',
    1: 'PDRAW_MEDIA_TYPE_VIDEO',
}
PDRAW_MEDIA_TYPE_UNKNOWN = 0
PDRAW_MEDIA_TYPE_VIDEO = 1
pdraw_media_type = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_video_type'
pdraw_video_type__enumvalues = {
    0: 'PDRAW_VIDEO_TYPE_DEFAULT_CAMERA',
    0: 'PDRAW_VIDEO_TYPE_FRONT_CAMERA',
}
PDRAW_VIDEO_TYPE_DEFAULT_CAMERA = 0
PDRAW_VIDEO_TYPE_FRONT_CAMERA = 0
pdraw_video_type = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_histogram_channel'
pdraw_histogram_channel__enumvalues = {
    0: 'PDRAW_HISTOGRAM_CHANNEL_RED',
    1: 'PDRAW_HISTOGRAM_CHANNEL_GREEN',
    2: 'PDRAW_HISTOGRAM_CHANNEL_BLUE',
    3: 'PDRAW_HISTOGRAM_CHANNEL_LUMA',
    4: 'PDRAW_HISTOGRAM_CHANNEL_MAX',
}
PDRAW_HISTOGRAM_CHANNEL_RED = 0
PDRAW_HISTOGRAM_CHANNEL_GREEN = 1
PDRAW_HISTOGRAM_CHANNEL_BLUE = 2
PDRAW_HISTOGRAM_CHANNEL_LUMA = 3
PDRAW_HISTOGRAM_CHANNEL_MAX = 4
pdraw_histogram_channel = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_video_renderer_fill_mode'
pdraw_video_renderer_fill_mode__enumvalues = {
    0: 'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT',
    1: 'PDRAW_VIDEO_RENDERER_FILL_MODE_CROP',
    2: 'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_CROP',
    3: 'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_EXTEND',
    4: 'PDRAW_VIDEO_RENDERER_FILL_MODE_MAX',
}
PDRAW_VIDEO_RENDERER_FILL_MODE_FIT = 0
PDRAW_VIDEO_RENDERER_FILL_MODE_CROP = 1
PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_CROP = 2
PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_EXTEND = 3
PDRAW_VIDEO_RENDERER_FILL_MODE_MAX = 4
pdraw_video_renderer_fill_mode = ctypes.c_uint32 # enum

# values for enumeration 'pdraw_video_renderer_transition_flag'
pdraw_video_renderer_transition_flag__enumvalues = {
    1: 'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_SOS',
    2: 'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_EOS',
    4: 'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_RECONFIGURE',
    8: 'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_TIMEOUT',
    16: 'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_PHOTO_TRIGGER',
}
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_SOS = 1
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_EOS = 2
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_RECONFIGURE = 4
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_TIMEOUT = 8
PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_PHOTO_TRIGGER = 16
pdraw_video_renderer_transition_flag = ctypes.c_uint32 # enum
class struct_pdraw_raw_video_info(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('format', struct_vdef_raw_format),
        ('info', struct_vdef_format_info),
    ]

class struct_pdraw_coded_video_info_0_0(Structure):
    pass

struct_pdraw_coded_video_info_0_0._pack_ = True # source:False
struct_pdraw_coded_video_info_0_0._fields_ = [
    ('sps', ctypes.c_ubyte * 64),
    ('spslen', ctypes.c_uint64),
    ('pps', ctypes.c_ubyte * 64),
    ('ppslen', ctypes.c_uint64),
]

class struct_pdraw_coded_video_info_0_1(Structure):
    pass

struct_pdraw_coded_video_info_0_1._pack_ = True # source:False
struct_pdraw_coded_video_info_0_1._fields_ = [
    ('vps', ctypes.c_ubyte * 64),
    ('vpslen', ctypes.c_uint64),
    ('sps', ctypes.c_ubyte * 64),
    ('spslen', ctypes.c_uint64),
    ('pps', ctypes.c_ubyte * 64),
    ('ppslen', ctypes.c_uint64),
]

class union_pdraw_coded_video_info_0(Union):
    _pack_ = True # source:False
    _fields_ = [
        ('h264', struct_pdraw_coded_video_info_0_0),
        ('h265', struct_pdraw_coded_video_info_0_1),
    ]

class struct_pdraw_coded_video_info(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('format', struct_vdef_coded_format),
        ('info', struct_vdef_format_info),
        ('pdraw_coded_video_info_0', union_pdraw_coded_video_info_0),
    ]

class union_pdraw_video_info_0(Union):
    _pack_ = True # source:False
    _fields_ = [
        ('raw', struct_pdraw_raw_video_info),
        ('coded', struct_pdraw_coded_video_info),
    ]

class struct_pdraw_video_info(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('format', vdef_frame_type),
        ('type', pdraw_video_type),
        ('pdraw_video_info_0', union_pdraw_video_info_0),
    ]

class union_pdraw_media_info_0(Union):
    _pack_ = True # source:False
    _fields_ = [
        ('video', struct_pdraw_video_info),
    ]

class struct_pdraw_media_info(Structure):
    pass

struct_pdraw_media_info._pack_ = True # source:False
struct_pdraw_media_info._fields_ = [
    ('type', pdraw_media_type),
    ('id', ctypes.c_uint32),
    ('name', POINTER_T(ctypes.c_char)),
    ('path', POINTER_T(ctypes.c_char)),
    ('playback_type', pdraw_playback_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('duration', ctypes.c_uint64),
    ('session_meta', POINTER_T(struct_vmeta_session)),
    ('pdraw_media_info_0', union_pdraw_media_info_0),
]

class union_pdraw_video_frame_0(Union):
    pass

union_pdraw_video_frame_0._pack_ = True # source:False
union_pdraw_video_frame_0._fields_ = [
    ('raw', struct_vdef_raw_frame),
    ('coded', struct_vdef_coded_frame),
    ('PADDING_0', ctypes.c_ubyte * 48),
]

class struct_pdraw_video_frame(Structure):
    pass

struct_pdraw_video_frame._pack_ = True # source:False
struct_pdraw_video_frame._fields_ = [
    ('format', vdef_frame_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pdraw_video_frame_0', union_pdraw_video_frame_0),
    ('is_sync', ctypes.c_int32),
    ('is_ref', ctypes.c_int32),
    ('ntp_timestamp', ctypes.c_uint64),
    ('ntp_unskewed_timestamp', ctypes.c_uint64),
    ('ntp_raw_timestamp', ctypes.c_uint64),
    ('ntp_raw_unskewed_timestamp', ctypes.c_uint64),
    ('play_timestamp', ctypes.c_uint64),
    ('capture_timestamp', ctypes.c_uint64),
    ('local_timestamp', ctypes.c_uint64),
]

class struct_pdraw_video_frame_extra(Structure):
    pass

struct_pdraw_video_frame_extra._pack_ = True # source:False
struct_pdraw_video_frame_extra._fields_ = [
    ('play_timestamp', ctypes.c_uint64),
    ('histogram', POINTER_T(ctypes.c_float) * 4),
    ('histogram_len', ctypes.c_uint64 * 4),
]

class struct_pdraw_rect(Structure):
    pass

struct_pdraw_rect._pack_ = True # source:False
struct_pdraw_rect._fields_ = [
    ('x', ctypes.c_int32),
    ('y', ctypes.c_int32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
]

class struct_pdraw_video_renderer_params(Structure):
    pass

struct_pdraw_video_renderer_params._pack_ = True # source:False
struct_pdraw_video_renderer_params._fields_ = [
    ('fill_mode', pdraw_video_renderer_fill_mode),
    ('enable_transition_flags', ctypes.c_uint32),
    ('enable_hmd_distortion_correction', ctypes.c_int32),
    ('hmd_ipd_offset', ctypes.c_float),
    ('hmd_x_offset', ctypes.c_float),
    ('hmd_y_offset', ctypes.c_float),
    ('video_scale_factor', ctypes.c_float),
    ('enable_overexposure_zebras', ctypes.c_int32),
    ('overexposure_zebras_threshold', ctypes.c_float),
    ('enable_histograms', ctypes.c_int32),
    ('video_texture_width', ctypes.c_uint32),
    ('video_texture_dar_width', ctypes.c_uint32),
    ('video_texture_dar_height', ctypes.c_uint32),
]

class union_pdraw_video_sink_params_0(Union):
    pass

union_pdraw_video_sink_params_0._pack_ = True # source:False
union_pdraw_video_sink_params_0._fields_ = [
    ('required_raw_format', struct_vdef_raw_format),
    ('required_coded_format', struct_vdef_coded_format),
    ('PADDING_0', ctypes.c_ubyte * 20),
]

class struct_pdraw_video_sink_params(Structure):
    pass

struct_pdraw_video_sink_params._pack_ = True # source:False
struct_pdraw_video_sink_params._fields_ = [
    ('queue_max_count', ctypes.c_uint32),
    ('pdraw_video_sink_params_0', union_pdraw_video_sink_params_0),
    ('fake_frame_num', ctypes.c_int32),
]

class struct_pdraw_muxer_video_media_params(Structure):
    pass

struct_pdraw_muxer_video_media_params._pack_ = True # source:False
struct_pdraw_muxer_video_media_params._fields_ = [
    ('resolution', struct_vdef_dim),
    ('encoding', vdef_encoding),
    ('target_bitrate', ctypes.c_uint32),
    ('gop_length_sec', ctypes.c_float),
]

class struct_pdraw_demuxer_media(Structure):
    pass

struct_pdraw_demuxer_media._pack_ = True # source:False
struct_pdraw_demuxer_media._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('media_id', ctypes.c_int32),
    ('is_default', ctypes.c_int32),
    ('session_meta', struct_vmeta_session),
    ('idx', ctypes.c_int32),
    ('stream_port', ctypes.c_uint32),
    ('control_port', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('uri', POINTER_T(ctypes.c_char)),
]

class struct_pdraw(Structure):
    pass

class struct_pdraw_demuxer(Structure):
    pass

class struct_pdraw_muxer(Structure):
    pass

class struct_pdraw_video_renderer(Structure):
    pass

class struct_pdraw_coded_video_sink(Structure):
    pass

class struct_pdraw_raw_video_sink(Structure):
    pass

class struct_pdraw_cbs(Structure):
    pass

struct_pdraw_cbs._pack_ = True # source:False
struct_pdraw_cbs._fields_ = [
    ('stop_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), ctypes.c_int32, POINTER_T(None))),
    ('media_added', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_media_info), POINTER_T(None))),
    ('media_removed', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_media_info), POINTER_T(None))),
    ('socket_created', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), ctypes.c_int32, POINTER_T(None))),
]

class struct_pdraw_demuxer_cbs(Structure):
    pass

struct_pdraw_demuxer_cbs._pack_ = True # source:False
struct_pdraw_demuxer_cbs._fields_ = [
    ('open_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, POINTER_T(None))),
    ('close_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, POINTER_T(None))),
    ('unrecoverable_error', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), POINTER_T(None))),
    ('select_media', ctypes.CFUNCTYPE(ctypes.c_int32, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), POINTER_T(struct_pdraw_demuxer_media), ctypes.c_uint64, POINTER_T(None))),
    ('ready_to_play', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, POINTER_T(None))),
    ('end_of_range', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_uint64, POINTER_T(None))),
    ('play_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, ctypes.c_uint64, ctypes.c_float, POINTER_T(None))),
    ('pause_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, ctypes.c_uint64, POINTER_T(None))),
    ('seek_resp', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_int32, ctypes.c_uint64, ctypes.c_float, POINTER_T(None))),
]

class struct_pdraw_video_renderer_cbs(Structure):
    pass

struct_pdraw_video_renderer_cbs._pack_ = True # source:False
struct_pdraw_video_renderer_cbs._fields_ = [
    ('media_added', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_media_info), POINTER_T(None))),
    ('media_removed', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_media_info), POINTER_T(None))),
    ('render_ready', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(None))),
    ('load_texture', ctypes.CFUNCTYPE(ctypes.c_int32, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), ctypes.c_uint32, ctypes.c_uint32, POINTER_T(struct_pdraw_media_info), POINTER_T(struct_mbuf_raw_video_frame), POINTER_T(None), ctypes.c_uint64, POINTER_T(None))),
    ('render_overlay', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_rect), POINTER_T(struct_pdraw_rect), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float), POINTER_T(struct_pdraw_media_info), POINTER_T(struct_vmeta_frame), POINTER_T(struct_pdraw_video_frame_extra), POINTER_T(None))),
]

class struct_pdraw_coded_video_sink_cbs(Structure):
    pass

struct_pdraw_coded_video_sink_cbs._pack_ = True # source:False
struct_pdraw_coded_video_sink_cbs._fields_ = [
    ('flush', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_coded_video_sink), POINTER_T(None))),
]

class struct_pdraw_raw_video_sink_cbs(Structure):
    pass

struct_pdraw_raw_video_sink_cbs._pack_ = True # source:False
struct_pdraw_raw_video_sink_cbs._fields_ = [
    ('flush', ctypes.CFUNCTYPE(None, POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_raw_video_sink), POINTER_T(None))),
]

pdraw_new = _libraries['libpdraw.so'].pdraw_new
pdraw_new.restype = ctypes.c_int32
pdraw_new.argtypes = [POINTER_T(struct_pomp_loop), POINTER_T(struct_pdraw_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw))]
pdraw_destroy = _libraries['libpdraw.so'].pdraw_destroy
pdraw_destroy.restype = ctypes.c_int32
pdraw_destroy.argtypes = [POINTER_T(struct_pdraw)]
pdraw_stop = _libraries['libpdraw.so'].pdraw_stop
pdraw_stop.restype = ctypes.c_int32
pdraw_stop.argtypes = [POINTER_T(struct_pdraw)]
pdraw_demuxer_new_from_url = _libraries['libpdraw.so'].pdraw_demuxer_new_from_url
pdraw_demuxer_new_from_url.restype = ctypes.c_int32
pdraw_demuxer_new_from_url.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), POINTER_T(struct_pdraw_demuxer_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_demuxer))]
pdraw_demuxer_new_single_stream = _libraries['libpdraw.so'].pdraw_demuxer_new_single_stream
pdraw_demuxer_new_single_stream.restype = ctypes.c_int32
pdraw_demuxer_new_single_stream.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), uint16_t, uint16_t, POINTER_T(ctypes.c_char), uint16_t, uint16_t, POINTER_T(struct_pdraw_demuxer_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_demuxer))]
pdraw_demuxer_new_from_url_on_mux = _libraries['libpdraw.so'].pdraw_demuxer_new_from_url_on_mux
pdraw_demuxer_new_from_url_on_mux.restype = ctypes.c_int32
pdraw_demuxer_new_from_url_on_mux.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), POINTER_T(struct_mux_ctx), POINTER_T(struct_pdraw_demuxer_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_demuxer))]
pdraw_demuxer_destroy = _libraries['libpdraw.so'].pdraw_demuxer_destroy
pdraw_demuxer_destroy.restype = ctypes.c_int32
pdraw_demuxer_destroy.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_close = _libraries['libpdraw.so'].pdraw_demuxer_close
pdraw_demuxer_close.restype = ctypes.c_int32
pdraw_demuxer_close.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_get_single_stream_local_stream_port = _libraries['libpdraw.so'].pdraw_demuxer_get_single_stream_local_stream_port
pdraw_demuxer_get_single_stream_local_stream_port.restype = uint16_t
pdraw_demuxer_get_single_stream_local_stream_port.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_get_single_stream_local_control_port = _libraries['libpdraw.so'].pdraw_demuxer_get_single_stream_local_control_port
pdraw_demuxer_get_single_stream_local_control_port.restype = uint16_t
pdraw_demuxer_get_single_stream_local_control_port.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_is_ready_to_play = _libraries['libpdraw.so'].pdraw_demuxer_is_ready_to_play
pdraw_demuxer_is_ready_to_play.restype = ctypes.c_int32
pdraw_demuxer_is_ready_to_play.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_is_paused = _libraries['libpdraw.so'].pdraw_demuxer_is_paused
pdraw_demuxer_is_paused.restype = ctypes.c_int32
pdraw_demuxer_is_paused.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_play = _libraries['libpdraw.so'].pdraw_demuxer_play
pdraw_demuxer_play.restype = ctypes.c_int32
pdraw_demuxer_play.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_play_with_speed = _libraries['libpdraw.so'].pdraw_demuxer_play_with_speed
pdraw_demuxer_play_with_speed.restype = ctypes.c_int32
pdraw_demuxer_play_with_speed.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), ctypes.c_float]
pdraw_demuxer_pause = _libraries['libpdraw.so'].pdraw_demuxer_pause
pdraw_demuxer_pause.restype = ctypes.c_int32
pdraw_demuxer_pause.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_previous_frame = _libraries['libpdraw.so'].pdraw_demuxer_previous_frame
pdraw_demuxer_previous_frame.restype = ctypes.c_int32
pdraw_demuxer_previous_frame.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_next_frame = _libraries['libpdraw.so'].pdraw_demuxer_next_frame
pdraw_demuxer_next_frame.restype = ctypes.c_int32
pdraw_demuxer_next_frame.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_seek = _libraries['libpdraw.so'].pdraw_demuxer_seek
pdraw_demuxer_seek.restype = ctypes.c_int32
pdraw_demuxer_seek.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), int64_t, ctypes.c_int32]
pdraw_demuxer_seek_forward = _libraries['libpdraw.so'].pdraw_demuxer_seek_forward
pdraw_demuxer_seek_forward.restype = ctypes.c_int32
pdraw_demuxer_seek_forward.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), uint64_t, ctypes.c_int32]
pdraw_demuxer_seek_back = _libraries['libpdraw.so'].pdraw_demuxer_seek_back
pdraw_demuxer_seek_back.restype = ctypes.c_int32
pdraw_demuxer_seek_back.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), uint64_t, ctypes.c_int32]
pdraw_demuxer_seek_to = _libraries['libpdraw.so'].pdraw_demuxer_seek_to
pdraw_demuxer_seek_to.restype = ctypes.c_int32
pdraw_demuxer_seek_to.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer), uint64_t, ctypes.c_int32]
pdraw_demuxer_get_duration = _libraries['libpdraw.so'].pdraw_demuxer_get_duration
pdraw_demuxer_get_duration.restype = uint64_t
pdraw_demuxer_get_duration.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_demuxer_get_current_time = _libraries['libpdraw.so'].pdraw_demuxer_get_current_time
pdraw_demuxer_get_current_time.restype = uint64_t
pdraw_demuxer_get_current_time.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_demuxer)]
pdraw_muxer_new = _libraries['libpdraw.so'].pdraw_muxer_new
pdraw_muxer_new.restype = ctypes.c_int32
pdraw_muxer_new.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_pdraw_muxer))]
pdraw_muxer_destroy = _libraries['libpdraw.so'].pdraw_muxer_destroy
pdraw_muxer_destroy.restype = ctypes.c_int32
pdraw_muxer_destroy.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_muxer)]
pdraw_muxer_add_media = _libraries['libpdraw.so'].pdraw_muxer_add_media
pdraw_muxer_add_media.restype = ctypes.c_int32
pdraw_muxer_add_media.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_muxer), ctypes.c_uint32, POINTER_T(struct_pdraw_muxer_video_media_params)]
pdraw_video_renderer_new = _libraries['libpdraw.so'].pdraw_video_renderer_new
pdraw_video_renderer_new.restype = ctypes.c_int32
pdraw_video_renderer_new.argtypes = [POINTER_T(struct_pdraw), ctypes.c_uint32, POINTER_T(struct_pdraw_rect), POINTER_T(struct_pdraw_video_renderer_params), POINTER_T(struct_pdraw_video_renderer_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_video_renderer))]
pdraw_video_renderer_new_egl = _libraries['libpdraw.so'].pdraw_video_renderer_new_egl
pdraw_video_renderer_new_egl.restype = ctypes.c_int32
pdraw_video_renderer_new_egl.argtypes = [POINTER_T(struct_pdraw), ctypes.c_uint32, POINTER_T(struct_pdraw_rect), POINTER_T(struct_pdraw_video_renderer_params), POINTER_T(struct_pdraw_video_renderer_cbs), POINTER_T(None), POINTER_T(struct_egl_display), POINTER_T(POINTER_T(struct_pdraw_video_renderer))]
pdraw_video_renderer_destroy = _libraries['libpdraw.so'].pdraw_video_renderer_destroy
pdraw_video_renderer_destroy.restype = ctypes.c_int32
pdraw_video_renderer_destroy.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer)]
pdraw_video_renderer_resize = _libraries['libpdraw.so'].pdraw_video_renderer_resize
pdraw_video_renderer_resize.restype = ctypes.c_int32
pdraw_video_renderer_resize.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_rect)]
pdraw_video_renderer_set_media_id = _libraries['libpdraw.so'].pdraw_video_renderer_set_media_id
pdraw_video_renderer_set_media_id.restype = ctypes.c_int32
pdraw_video_renderer_set_media_id.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), ctypes.c_uint32]
pdraw_video_renderer_get_media_id = _libraries['libpdraw.so'].pdraw_video_renderer_get_media_id
pdraw_video_renderer_get_media_id.restype = ctypes.c_uint32
pdraw_video_renderer_get_media_id.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer)]
pdraw_video_renderer_set_params = _libraries['libpdraw.so'].pdraw_video_renderer_set_params
pdraw_video_renderer_set_params.restype = ctypes.c_int32
pdraw_video_renderer_set_params.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_video_renderer_params)]
pdraw_video_renderer_get_params = _libraries['libpdraw.so'].pdraw_video_renderer_get_params
pdraw_video_renderer_get_params.restype = ctypes.c_int32
pdraw_video_renderer_get_params.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_video_renderer_params)]
pdraw_video_renderer_render = _libraries['libpdraw.so'].pdraw_video_renderer_render
pdraw_video_renderer_render.restype = ctypes.c_int32
pdraw_video_renderer_render.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_rect)]
pdraw_video_renderer_render_mat = _libraries['libpdraw.so'].pdraw_video_renderer_render_mat
pdraw_video_renderer_render_mat.restype = ctypes.c_int32
pdraw_video_renderer_render_mat.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_video_renderer), POINTER_T(struct_pdraw_rect), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float)]
pdraw_coded_video_sink_new = _libraries['libpdraw.so'].pdraw_coded_video_sink_new
pdraw_coded_video_sink_new.restype = ctypes.c_int32
pdraw_coded_video_sink_new.argtypes = [POINTER_T(struct_pdraw), ctypes.c_uint32, POINTER_T(struct_pdraw_video_sink_params), POINTER_T(struct_pdraw_coded_video_sink_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_coded_video_sink))]
pdraw_coded_video_sink_destroy = _libraries['libpdraw.so'].pdraw_coded_video_sink_destroy
pdraw_coded_video_sink_destroy.restype = ctypes.c_int32
pdraw_coded_video_sink_destroy.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_coded_video_sink)]
pdraw_coded_video_sink_resync = _libraries['libpdraw.so'].pdraw_coded_video_sink_resync
pdraw_coded_video_sink_resync.restype = ctypes.c_int32
pdraw_coded_video_sink_resync.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_coded_video_sink)]
pdraw_coded_video_sink_get_queue = _libraries['libpdraw.so'].pdraw_coded_video_sink_get_queue
pdraw_coded_video_sink_get_queue.restype = POINTER_T(struct_mbuf_coded_video_frame_queue)
pdraw_coded_video_sink_get_queue.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_coded_video_sink)]
pdraw_coded_video_sink_queue_flushed = _libraries['libpdraw.so'].pdraw_coded_video_sink_queue_flushed
pdraw_coded_video_sink_queue_flushed.restype = ctypes.c_int32
pdraw_coded_video_sink_queue_flushed.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_coded_video_sink)]
pdraw_raw_video_sink_new = _libraries['libpdraw.so'].pdraw_raw_video_sink_new
pdraw_raw_video_sink_new.restype = ctypes.c_int32
pdraw_raw_video_sink_new.argtypes = [POINTER_T(struct_pdraw), ctypes.c_uint32, POINTER_T(struct_pdraw_video_sink_params), POINTER_T(struct_pdraw_raw_video_sink_cbs), POINTER_T(None), POINTER_T(POINTER_T(struct_pdraw_raw_video_sink))]
pdraw_raw_video_sink_destroy = _libraries['libpdraw.so'].pdraw_raw_video_sink_destroy
pdraw_raw_video_sink_destroy.restype = ctypes.c_int32
pdraw_raw_video_sink_destroy.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_raw_video_sink)]
pdraw_raw_video_sink_get_queue = _libraries['libpdraw.so'].pdraw_raw_video_sink_get_queue
pdraw_raw_video_sink_get_queue.restype = POINTER_T(struct_mbuf_raw_video_frame_queue)
pdraw_raw_video_sink_get_queue.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_raw_video_sink)]
pdraw_raw_video_sink_queue_flushed = _libraries['libpdraw.so'].pdraw_raw_video_sink_queue_flushed
pdraw_raw_video_sink_queue_flushed.restype = ctypes.c_int32
pdraw_raw_video_sink_queue_flushed.argtypes = [POINTER_T(struct_pdraw), POINTER_T(struct_pdraw_raw_video_sink)]
pdraw_get_friendly_name_setting = _libraries['libpdraw.so'].pdraw_get_friendly_name_setting
pdraw_get_friendly_name_setting.restype = ctypes.c_int32
pdraw_get_friendly_name_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), size_t]
pdraw_set_friendly_name_setting = _libraries['libpdraw.so'].pdraw_set_friendly_name_setting
pdraw_set_friendly_name_setting.restype = ctypes.c_int32
pdraw_set_friendly_name_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char)]
pdraw_get_serial_number_setting = _libraries['libpdraw.so'].pdraw_get_serial_number_setting
pdraw_get_serial_number_setting.restype = ctypes.c_int32
pdraw_get_serial_number_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), size_t]
pdraw_set_serial_number_setting = _libraries['libpdraw.so'].pdraw_set_serial_number_setting
pdraw_set_serial_number_setting.restype = ctypes.c_int32
pdraw_set_serial_number_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char)]
pdraw_get_software_version_setting = _libraries['libpdraw.so'].pdraw_get_software_version_setting
pdraw_get_software_version_setting.restype = ctypes.c_int32
pdraw_get_software_version_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char), size_t]
pdraw_set_software_version_setting = _libraries['libpdraw.so'].pdraw_set_software_version_setting
pdraw_set_software_version_setting.restype = ctypes.c_int32
pdraw_set_software_version_setting.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char)]
pdraw_get_pipeline_mode_setting = _libraries['libpdraw.so'].pdraw_get_pipeline_mode_setting
pdraw_get_pipeline_mode_setting.restype = pdraw_pipeline_mode
pdraw_get_pipeline_mode_setting.argtypes = [POINTER_T(struct_pdraw)]
pdraw_set_pipeline_mode_setting = _libraries['libpdraw.so'].pdraw_set_pipeline_mode_setting
pdraw_set_pipeline_mode_setting.restype = ctypes.c_int32
pdraw_set_pipeline_mode_setting.argtypes = [POINTER_T(struct_pdraw), pdraw_pipeline_mode]
pdraw_get_display_screen_settings = _libraries['libpdraw.so'].pdraw_get_display_screen_settings
pdraw_get_display_screen_settings.restype = ctypes.c_int32
pdraw_get_display_screen_settings.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float), POINTER_T(ctypes.c_float)]
pdraw_set_display_screen_settings = _libraries['libpdraw.so'].pdraw_set_display_screen_settings
pdraw_set_display_screen_settings.restype = ctypes.c_int32
pdraw_set_display_screen_settings.argtypes = [POINTER_T(struct_pdraw), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
pdraw_get_hmd_model_setting = _libraries['libpdraw.so'].pdraw_get_hmd_model_setting
pdraw_get_hmd_model_setting.restype = pdraw_hmd_model
pdraw_get_hmd_model_setting.argtypes = [POINTER_T(struct_pdraw)]
pdraw_set_hmd_model_setting = _libraries['libpdraw.so'].pdraw_set_hmd_model_setting
pdraw_set_hmd_model_setting.restype = ctypes.c_int32
pdraw_set_hmd_model_setting.argtypes = [POINTER_T(struct_pdraw), pdraw_hmd_model]
pdraw_set_android_jvm = _libraries['libpdraw.so'].pdraw_set_android_jvm
pdraw_set_android_jvm.restype = ctypes.c_int32
pdraw_set_android_jvm.argtypes = [POINTER_T(struct_pdraw), POINTER_T(None)]
pdraw_dump_pipeline = _libraries['libpdraw.so'].pdraw_dump_pipeline
pdraw_dump_pipeline.restype = ctypes.c_int32
pdraw_dump_pipeline.argtypes = [POINTER_T(struct_pdraw), POINTER_T(ctypes.c_char)]
pdraw_hmd_model_str = _libraries['libpdraw.so'].pdraw_hmd_model_str
pdraw_hmd_model_str.restype = POINTER_T(ctypes.c_char)
pdraw_hmd_model_str.argtypes = [pdraw_hmd_model]
pdraw_pipeline_mode_str = _libraries['libpdraw.so'].pdraw_pipeline_mode_str
pdraw_pipeline_mode_str.restype = POINTER_T(ctypes.c_char)
pdraw_pipeline_mode_str.argtypes = [pdraw_pipeline_mode]
pdraw_playback_type_str = _libraries['libpdraw.so'].pdraw_playback_type_str
pdraw_playback_type_str.restype = POINTER_T(ctypes.c_char)
pdraw_playback_type_str.argtypes = [pdraw_playback_type]
pdraw_media_type_str = _libraries['libpdraw.so'].pdraw_media_type_str
pdraw_media_type_str.restype = POINTER_T(ctypes.c_char)
pdraw_media_type_str.argtypes = [pdraw_media_type]
pdraw_video_type_str = _libraries['libpdraw.so'].pdraw_video_type_str
pdraw_video_type_str.restype = POINTER_T(ctypes.c_char)
pdraw_video_type_str.argtypes = [pdraw_video_type]
pdraw_histogram_channel_str = _libraries['libpdraw.so'].pdraw_histogram_channel_str
pdraw_histogram_channel_str.restype = POINTER_T(ctypes.c_char)
pdraw_histogram_channel_str.argtypes = [pdraw_histogram_channel]
pdraw_video_renderer_fill_mode_str = _libraries['libpdraw.so'].pdraw_video_renderer_fill_mode_str
pdraw_video_renderer_fill_mode_str.restype = POINTER_T(ctypes.c_char)
pdraw_video_renderer_fill_mode_str.argtypes = [pdraw_video_renderer_fill_mode]
pdraw_video_renderer_transition_flag_str = _libraries['libpdraw.so'].pdraw_video_renderer_transition_flag_str
pdraw_video_renderer_transition_flag_str.restype = POINTER_T(ctypes.c_char)
pdraw_video_renderer_transition_flag_str.argtypes = [pdraw_video_renderer_transition_flag]
pdraw_video_frame_to_json = _libraries['libpdraw.so'].pdraw_video_frame_to_json
pdraw_video_frame_to_json.restype = ctypes.c_int32
pdraw_video_frame_to_json.argtypes = [POINTER_T(struct_pdraw_video_frame), POINTER_T(struct_vmeta_frame), POINTER_T(struct_json_object)]
pdraw_video_frame_to_json_str = _libraries['libpdraw.so'].pdraw_video_frame_to_json_str
pdraw_video_frame_to_json_str.restype = ctypes.c_int32
pdraw_video_frame_to_json_str.argtypes = [POINTER_T(struct_pdraw_video_frame), POINTER_T(struct_vmeta_frame), POINTER_T(ctypes.c_char), ctypes.c_uint32]
pdraw_media_info_dup = _libraries['libpdraw.so'].pdraw_media_info_dup
pdraw_media_info_dup.restype = POINTER_T(struct_pdraw_media_info)
pdraw_media_info_dup.argtypes = [POINTER_T(struct_pdraw_media_info)]
pdraw_media_info_free = _libraries['libpdraw.so'].pdraw_media_info_free
pdraw_media_info_free.restype = None
pdraw_media_info_free.argtypes = [POINTER_T(struct_pdraw_media_info)]
_ARSDK_H_ = True # macro
# ARSDK_API = (None) # macro
ARSDK_PROTOCOL_VERSION_1 = (1) # macro
ARSDK_PROTOCOL_VERSION_2 = (2) # macro
ARSDK_PROTOCOL_VERSION_3 = (3) # macro
_ARSDK_DESC_H_ = True # macro
_ARSDK_CMD_ITF_H_ = True # macro

# macro function ARSDK_CMD_FULL_ID
_ARSDK_MNGR_H_ = True # macro
ARSDK_INVALID_HANDLE = (0) # macro
_ARSDK_BACKEND_H_ = True # macro
_ARSDK_BACKEND_NET_H_ = True # macro
ARSDK_BACKEND_NET_PROTO_MIN = (1) # macro
ARSDK_BACKEND_NET_PROTO_MAX = (3) # macro
_ARSDK_BACKEND_MUX_H_ = True # macro
ARSDK_BACKEND_MUX_PROTO_MIN = (1) # macro
ARSDK_BACKEND_MUX_PROTO_MAX = (3) # macro
_ARSDK_PUBLISHER_AVAHI_H_ = True # macro
_ARSDK_PUBLISHER_NET_H_ = True # macro
_ARSDK_PUBLISHER_MUX_H_ = True # macro
_ARSDK_PEER_H_ = True # macro
class struct_arsdk_mngr(Structure):
    pass

class struct_arsdk_backend(Structure):
    pass

class struct_arsdk_cmd_itf(Structure):
    pass

class struct_arsdk_peer(Structure):
    pass


# values for enumeration 'arsdk_cmd_list_type'
arsdk_cmd_list_type__enumvalues = {
    0: 'ARSDK_CMD_LIST_TYPE_NONE',
    1: 'ARSDK_CMD_LIST_TYPE_LIST_ITEM',
    2: 'ARSDK_CMD_LIST_TYPE_MAP_ITEM',
}
ARSDK_CMD_LIST_TYPE_NONE = 0
ARSDK_CMD_LIST_TYPE_LIST_ITEM = 1
ARSDK_CMD_LIST_TYPE_MAP_ITEM = 2
arsdk_cmd_list_type = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_cmd_buffer_type'
arsdk_cmd_buffer_type__enumvalues = {
    0: 'ARSDK_CMD_BUFFER_TYPE_INVALID',
    1: 'ARSDK_CMD_BUFFER_TYPE_NON_ACK',
    2: 'ARSDK_CMD_BUFFER_TYPE_ACK',
    3: 'ARSDK_CMD_BUFFER_TYPE_HIGH_PRIO',
}
ARSDK_CMD_BUFFER_TYPE_INVALID = 0
ARSDK_CMD_BUFFER_TYPE_NON_ACK = 1
ARSDK_CMD_BUFFER_TYPE_ACK = 2
ARSDK_CMD_BUFFER_TYPE_HIGH_PRIO = 3
arsdk_cmd_buffer_type = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_cmd_timeout_policy'
arsdk_cmd_timeout_policy__enumvalues = {
    0: 'ARSDK_CMD_TIMEOUT_POLICY_POP',
    1: 'ARSDK_CMD_TIMEOUT_POLICY_RETRY',
    2: 'ARSDK_CMD_TIMEOUT_POLICY_FLUSH',
}
ARSDK_CMD_TIMEOUT_POLICY_POP = 0
ARSDK_CMD_TIMEOUT_POLICY_RETRY = 1
ARSDK_CMD_TIMEOUT_POLICY_FLUSH = 2
arsdk_cmd_timeout_policy = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_arg_type'
arsdk_arg_type__enumvalues = {
    0: 'ARSDK_ARG_TYPE_I8',
    1: 'ARSDK_ARG_TYPE_U8',
    2: 'ARSDK_ARG_TYPE_I16',
    3: 'ARSDK_ARG_TYPE_U16',
    4: 'ARSDK_ARG_TYPE_I32',
    5: 'ARSDK_ARG_TYPE_U32',
    6: 'ARSDK_ARG_TYPE_I64',
    7: 'ARSDK_ARG_TYPE_U64',
    8: 'ARSDK_ARG_TYPE_FLOAT',
    9: 'ARSDK_ARG_TYPE_DOUBLE',
    10: 'ARSDK_ARG_TYPE_STRING',
    11: 'ARSDK_ARG_TYPE_ENUM',
    12: 'ARSDK_ARG_TYPE_BINARY',
}
ARSDK_ARG_TYPE_I8 = 0
ARSDK_ARG_TYPE_U8 = 1
ARSDK_ARG_TYPE_I16 = 2
ARSDK_ARG_TYPE_U16 = 3
ARSDK_ARG_TYPE_I32 = 4
ARSDK_ARG_TYPE_U32 = 5
ARSDK_ARG_TYPE_I64 = 6
ARSDK_ARG_TYPE_U64 = 7
ARSDK_ARG_TYPE_FLOAT = 8
ARSDK_ARG_TYPE_DOUBLE = 9
ARSDK_ARG_TYPE_STRING = 10
ARSDK_ARG_TYPE_ENUM = 11
ARSDK_ARG_TYPE_BINARY = 12
arsdk_arg_type = ctypes.c_uint32 # enum
class struct_arsdk_enum_desc(Structure):
    pass

struct_arsdk_enum_desc._pack_ = True # source:False
struct_arsdk_enum_desc._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('value', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_arsdk_arg_desc(Structure):
    pass

struct_arsdk_arg_desc._pack_ = True # source:False
struct_arsdk_arg_desc._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('type', arsdk_arg_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('enum_desc_table', POINTER_T(struct_arsdk_enum_desc)),
    ('enum_desc_count', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

class struct_arsdk_cmd_desc(Structure):
    pass

struct_arsdk_cmd_desc._pack_ = True # source:False
struct_arsdk_cmd_desc._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('prj_id', ctypes.c_ubyte),
    ('cls_id', ctypes.c_ubyte),
    ('cmd_id', ctypes.c_uint16),
    ('list_type', arsdk_cmd_list_type),
    ('buffer_type', arsdk_cmd_buffer_type),
    ('timeout_policy', arsdk_cmd_timeout_policy),
    ('arg_desc_table', POINTER_T(struct_arsdk_arg_desc)),
    ('arg_desc_count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_arsdk_binary(Structure):
    pass

struct_arsdk_binary._pack_ = True # source:False
struct_arsdk_binary._fields_ = [
    ('cdata', POINTER_T(None)),
    ('len', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class union_arsdk_value_0(Union):
    pass

union_arsdk_value_0._pack_ = True # source:False
union_arsdk_value_0._fields_ = [
    ('i8', ctypes.c_byte),
    ('u8', ctypes.c_ubyte),
    ('i16', ctypes.c_int16),
    ('u16', ctypes.c_uint16),
    ('i32', ctypes.c_int32),
    ('u32', ctypes.c_uint32),
    ('u64', ctypes.c_uint64),
    ('i64', ctypes.c_int64),
    ('f32', ctypes.c_float),
    ('f64', ctypes.c_double),
    ('str', POINTER_T(ctypes.c_char)),
    ('cstr', POINTER_T(ctypes.c_char)),
    ('binary', struct_arsdk_binary),
]

class struct_arsdk_value(Structure):
    pass

struct_arsdk_value._pack_ = True # source:False
struct_arsdk_value._fields_ = [
    ('type', arsdk_arg_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('data', union_arsdk_value_0),
]

class struct_arsdk_cmd(Structure):
    pass

struct_arsdk_cmd._pack_ = True # source:False
struct_arsdk_cmd._fields_ = [
    ('prj_id', ctypes.c_ubyte),
    ('cls_id', ctypes.c_ubyte),
    ('cmd_id', ctypes.c_uint16),
    ('id', ctypes.c_uint32),
    ('buf', POINTER_T(struct_pomp_buffer)),
    ('userdata', POINTER_T(None)),
    ('buffer_type', arsdk_cmd_buffer_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
]


# values for enumeration 'arsdk_cmd_dir'
arsdk_cmd_dir__enumvalues = {
    0: 'ARSDK_CMD_DIR_RX',
    1: 'ARSDK_CMD_DIR_TX',
}
ARSDK_CMD_DIR_RX = 0
ARSDK_CMD_DIR_TX = 1
arsdk_cmd_dir = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_cmd_itf_send_status'
arsdk_cmd_itf_send_status__enumvalues = {
    0: 'ARSDK_CMD_ITF_SEND_STATUS_SENT',
    1: 'ARSDK_CMD_ITF_SEND_STATUS_ACK_RECEIVED',
    2: 'ARSDK_CMD_ITF_SEND_STATUS_TIMEOUT',
    3: 'ARSDK_CMD_ITF_SEND_STATUS_CANCELED',
}
ARSDK_CMD_ITF_SEND_STATUS_SENT = 0
ARSDK_CMD_ITF_SEND_STATUS_ACK_RECEIVED = 1
ARSDK_CMD_ITF_SEND_STATUS_TIMEOUT = 2
ARSDK_CMD_ITF_SEND_STATUS_CANCELED = 3
arsdk_cmd_itf_send_status = ctypes.c_uint32 # enum
arsdk_cmd_itf_send_status_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), POINTER_T(struct_arsdk_cmd), arsdk_cmd_itf_send_status, ctypes.c_int32, POINTER_T(None))
class struct_arsdk_cmd_itf_cbs(Structure):
    pass

struct_arsdk_cmd_itf_cbs._pack_ = True # source:False
struct_arsdk_cmd_itf_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('dispose', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), POINTER_T(None))),
    ('recv_cmd', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), POINTER_T(struct_arsdk_cmd), POINTER_T(None))),
    ('cmd_log', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), arsdk_cmd_dir, POINTER_T(struct_arsdk_cmd), POINTER_T(None))),
    ('transport_log', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), arsdk_cmd_dir, POINTER_T(None), ctypes.c_uint64, POINTER_T(None), ctypes.c_uint64, POINTER_T(None))),
    ('send_status', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), POINTER_T(struct_arsdk_cmd), arsdk_cmd_itf_send_status, ctypes.c_int32, POINTER_T(None))),
    ('link_quality', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_cmd_itf), ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, POINTER_T(None))),
]

arsdk_cmd_itf_send_status_str = _libraries['libarsdk.so'].arsdk_cmd_itf_send_status_str
arsdk_cmd_itf_send_status_str.restype = POINTER_T(ctypes.c_char)
arsdk_cmd_itf_send_status_str.argtypes = [arsdk_cmd_itf_send_status]
arsdk_cmd_itf_set_osdata = _libraries['libarsdk.so'].arsdk_cmd_itf_set_osdata
arsdk_cmd_itf_set_osdata.restype = ctypes.c_int32
arsdk_cmd_itf_set_osdata.argtypes = [POINTER_T(struct_arsdk_cmd_itf), POINTER_T(None)]
arsdk_cmd_itf_get_osdata = _libraries['libarsdk.so'].arsdk_cmd_itf_get_osdata
arsdk_cmd_itf_get_osdata.restype = POINTER_T(None)
arsdk_cmd_itf_get_osdata.argtypes = [POINTER_T(struct_arsdk_cmd_itf)]
arsdk_cmd_itf_send = _libraries['libarsdk.so'].arsdk_cmd_itf_send
arsdk_cmd_itf_send.restype = ctypes.c_int32
arsdk_cmd_itf_send.argtypes = [POINTER_T(struct_arsdk_cmd_itf), POINTER_T(struct_arsdk_cmd), arsdk_cmd_itf_send_status_cb_t, POINTER_T(None)]
arsdk_cmd_enc = _libraries['libarsdk.so'].arsdk_cmd_enc
arsdk_cmd_enc.restype = ctypes.c_int32
arsdk_cmd_enc.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_arsdk_cmd_desc)]
arsdk_cmd_enc_argv = _libraries['libarsdk.so'].arsdk_cmd_enc_argv
arsdk_cmd_enc_argv.restype = ctypes.c_int32
arsdk_cmd_enc_argv.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_arsdk_cmd_desc), size_t, POINTER_T(struct_arsdk_value)]
arsdk_cmd_dec = _libraries['libarsdk.so'].arsdk_cmd_dec
arsdk_cmd_dec.restype = ctypes.c_int32
arsdk_cmd_dec.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_arsdk_cmd_desc)]
arsdk_cmd_dec_header = _libraries['libarsdk.so'].arsdk_cmd_dec_header
arsdk_cmd_dec_header.restype = ctypes.c_int32
arsdk_cmd_dec_header.argtypes = [POINTER_T(struct_arsdk_cmd)]
arsdk_cmd_find_desc = _libraries['libarsdk.so'].arsdk_cmd_find_desc
arsdk_cmd_find_desc.restype = POINTER_T(struct_arsdk_cmd_desc)
arsdk_cmd_find_desc.argtypes = [POINTER_T(struct_arsdk_cmd)]
arsdk_cmd_fmt = _libraries['libarsdk.so'].arsdk_cmd_fmt
arsdk_cmd_fmt.restype = ctypes.c_int32
arsdk_cmd_fmt.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(ctypes.c_char), size_t]
arsdk_cmd_get_values = _libraries['libarsdk.so'].arsdk_cmd_get_values
arsdk_cmd_get_values.restype = ctypes.c_int32
arsdk_cmd_get_values.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_arsdk_value), size_t, POINTER_T(ctypes.c_uint64)]
arsdk_arg_type_str = _libraries['libarsdk.so'].arsdk_arg_type_str
arsdk_arg_type_str.restype = POINTER_T(ctypes.c_char)
arsdk_arg_type_str.argtypes = [arsdk_arg_type]
arsdk_cmd_get_name = _libraries['FIXME_STUB'].arsdk_cmd_get_name
arsdk_cmd_get_name.restype = POINTER_T(ctypes.c_char)
arsdk_cmd_get_name.argtypes = [POINTER_T(struct_arsdk_cmd)]
arsdk_cmd_init = _libraries['FIXME_STUB'].arsdk_cmd_init
arsdk_cmd_init.restype = None
arsdk_cmd_init.argtypes = [POINTER_T(struct_arsdk_cmd)]
arsdk_cmd_init_with_buf = _libraries['FIXME_STUB'].arsdk_cmd_init_with_buf
arsdk_cmd_init_with_buf.restype = None
arsdk_cmd_init_with_buf.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_pomp_buffer)]
arsdk_cmd_clear = _libraries['FIXME_STUB'].arsdk_cmd_clear
arsdk_cmd_clear.restype = None
arsdk_cmd_clear.argtypes = [POINTER_T(struct_arsdk_cmd)]
arsdk_cmd_copy = _libraries['FIXME_STUB'].arsdk_cmd_copy
arsdk_cmd_copy.restype = None
arsdk_cmd_copy.argtypes = [POINTER_T(struct_arsdk_cmd), POINTER_T(struct_arsdk_cmd)]
class struct_arsdk_mngr_peer_cbs(Structure):
    pass

struct_arsdk_mngr_peer_cbs._pack_ = True # source:False
struct_arsdk_mngr_peer_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('added', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(None))),
    ('removed', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(None))),
]

arsdk_mngr_new = _libraries['libarsdk.so'].arsdk_mngr_new
arsdk_mngr_new.restype = ctypes.c_int32
arsdk_mngr_new.argtypes = [POINTER_T(struct_pomp_loop), POINTER_T(POINTER_T(struct_arsdk_mngr))]
arsdk_mngr_set_peer_cbs = _libraries['libarsdk.so'].arsdk_mngr_set_peer_cbs
arsdk_mngr_set_peer_cbs.restype = ctypes.c_int32
arsdk_mngr_set_peer_cbs.argtypes = [POINTER_T(struct_arsdk_mngr), POINTER_T(struct_arsdk_mngr_peer_cbs)]
arsdk_mngr_get_loop = _libraries['libarsdk.so'].arsdk_mngr_get_loop
arsdk_mngr_get_loop.restype = POINTER_T(struct_pomp_loop)
arsdk_mngr_get_loop.argtypes = [POINTER_T(struct_arsdk_mngr)]
arsdk_mngr_destroy = _libraries['libarsdk.so'].arsdk_mngr_destroy
arsdk_mngr_destroy.restype = ctypes.c_int32
arsdk_mngr_destroy.argtypes = [POINTER_T(struct_arsdk_mngr)]
arsdk_mngr_next_peer = _libraries['libarsdk.so'].arsdk_mngr_next_peer
arsdk_mngr_next_peer.restype = POINTER_T(struct_arsdk_peer)
arsdk_mngr_next_peer.argtypes = [POINTER_T(struct_arsdk_mngr), POINTER_T(struct_arsdk_peer)]
arsdk_mngr_get_peer = _libraries['libarsdk.so'].arsdk_mngr_get_peer
arsdk_mngr_get_peer.restype = POINTER_T(struct_arsdk_peer)
arsdk_mngr_get_peer.argtypes = [POINTER_T(struct_arsdk_mngr), uint16_t]

# values for enumeration 'arsdk_socket_kind'
arsdk_socket_kind__enumvalues = {
    0: 'ARSDK_SOCKET_KIND_DISCOVERY',
    1: 'ARSDK_SOCKET_KIND_CONNECTION',
    2: 'ARSDK_SOCKET_KIND_COMMAND',
    3: 'ARSDK_SOCKET_KIND_FTP',
    4: 'ARSDK_SOCKET_KIND_VIDEO',
}
ARSDK_SOCKET_KIND_DISCOVERY = 0
ARSDK_SOCKET_KIND_CONNECTION = 1
ARSDK_SOCKET_KIND_COMMAND = 2
ARSDK_SOCKET_KIND_FTP = 3
ARSDK_SOCKET_KIND_VIDEO = 4
arsdk_socket_kind = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_device_type'
arsdk_device_type__enumvalues = {
    -1: 'ARSDK_DEVICE_TYPE_UNKNOWN',
    2305: 'ARSDK_DEVICE_TYPE_BEBOP',
    2316: 'ARSDK_DEVICE_TYPE_BEBOP_2',
    2321: 'ARSDK_DEVICE_TYPE_PAROS',
    2324: 'ARSDK_DEVICE_TYPE_ANAFI4K',
    2329: 'ARSDK_DEVICE_TYPE_ANAFI_THERMAL',
    2326: 'ARSDK_DEVICE_TYPE_CHIMERA',
    2330: 'ARSDK_DEVICE_TYPE_ANAFI_2',
    2331: 'ARSDK_DEVICE_TYPE_ANAFI_UA',
    2334: 'ARSDK_DEVICE_TYPE_ANAFI_USA',
    2307: 'ARSDK_DEVICE_TYPE_SKYCTRL',
    2323: 'ARSDK_DEVICE_TYPE_SKYCTRL_NG',
    2319: 'ARSDK_DEVICE_TYPE_SKYCTRL_2',
    2325: 'ARSDK_DEVICE_TYPE_SKYCTRL_2P',
    2328: 'ARSDK_DEVICE_TYPE_SKYCTRL_3',
    2332: 'ARSDK_DEVICE_TYPE_SKYCTRL_UA',
    2333: 'ARSDK_DEVICE_TYPE_SKYCTRL_4',
    2306: 'ARSDK_DEVICE_TYPE_JS',
    2309: 'ARSDK_DEVICE_TYPE_JS_EVO_LIGHT',
    2310: 'ARSDK_DEVICE_TYPE_JS_EVO_RACE',
    2304: 'ARSDK_DEVICE_TYPE_RS',
    2311: 'ARSDK_DEVICE_TYPE_RS_EVO_LIGHT',
    2313: 'ARSDK_DEVICE_TYPE_RS_EVO_BRICK',
    2314: 'ARSDK_DEVICE_TYPE_RS_EVO_HYDROFOIL',
    2315: 'ARSDK_DEVICE_TYPE_RS3',
    2317: 'ARSDK_DEVICE_TYPE_POWERUP',
    2318: 'ARSDK_DEVICE_TYPE_EVINRUDE',
    2320: 'ARSDK_DEVICE_TYPE_WINGX',
}
ARSDK_DEVICE_TYPE_UNKNOWN = -1
ARSDK_DEVICE_TYPE_BEBOP = 2305
ARSDK_DEVICE_TYPE_BEBOP_2 = 2316
ARSDK_DEVICE_TYPE_PAROS = 2321
ARSDK_DEVICE_TYPE_ANAFI4K = 2324
ARSDK_DEVICE_TYPE_ANAFI_THERMAL = 2329
ARSDK_DEVICE_TYPE_CHIMERA = 2326
ARSDK_DEVICE_TYPE_ANAFI_2 = 2330
ARSDK_DEVICE_TYPE_ANAFI_UA = 2331
ARSDK_DEVICE_TYPE_ANAFI_USA = 2334
ARSDK_DEVICE_TYPE_SKYCTRL = 2307
ARSDK_DEVICE_TYPE_SKYCTRL_NG = 2323
ARSDK_DEVICE_TYPE_SKYCTRL_2 = 2319
ARSDK_DEVICE_TYPE_SKYCTRL_2P = 2325
ARSDK_DEVICE_TYPE_SKYCTRL_3 = 2328
ARSDK_DEVICE_TYPE_SKYCTRL_UA = 2332
ARSDK_DEVICE_TYPE_SKYCTRL_4 = 2333
ARSDK_DEVICE_TYPE_JS = 2306
ARSDK_DEVICE_TYPE_JS_EVO_LIGHT = 2309
ARSDK_DEVICE_TYPE_JS_EVO_RACE = 2310
ARSDK_DEVICE_TYPE_RS = 2304
ARSDK_DEVICE_TYPE_RS_EVO_LIGHT = 2311
ARSDK_DEVICE_TYPE_RS_EVO_BRICK = 2313
ARSDK_DEVICE_TYPE_RS_EVO_HYDROFOIL = 2314
ARSDK_DEVICE_TYPE_RS3 = 2315
ARSDK_DEVICE_TYPE_POWERUP = 2317
ARSDK_DEVICE_TYPE_EVINRUDE = 2318
ARSDK_DEVICE_TYPE_WINGX = 2320
arsdk_device_type = ctypes.c_int32 # enum

# values for enumeration 'arsdk_conn_cancel_reason'
arsdk_conn_cancel_reason__enumvalues = {
    0: 'ARSDK_CONN_CANCEL_REASON_LOCAL',
    1: 'ARSDK_CONN_CANCEL_REASON_REMOTE',
    2: 'ARSDK_CONN_CANCEL_REASON_REJECTED',
}
ARSDK_CONN_CANCEL_REASON_LOCAL = 0
ARSDK_CONN_CANCEL_REASON_REMOTE = 1
ARSDK_CONN_CANCEL_REASON_REJECTED = 2
arsdk_conn_cancel_reason = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_link_status'
arsdk_link_status__enumvalues = {
    0: 'ARSDK_LINK_STATUS_KO',
    1: 'ARSDK_LINK_STATUS_OK',
}
ARSDK_LINK_STATUS_KO = 0
ARSDK_LINK_STATUS_OK = 1
arsdk_link_status = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_backend_type'
arsdk_backend_type__enumvalues = {
    -1: 'ARSDK_BACKEND_TYPE_UNKNOWN',
    0: 'ARSDK_BACKEND_TYPE_NET',
    1: 'ARSDK_BACKEND_TYPE_BLE',
    2: 'ARSDK_BACKEND_TYPE_MUX',
}
ARSDK_BACKEND_TYPE_UNKNOWN = -1
ARSDK_BACKEND_TYPE_NET = 0
ARSDK_BACKEND_TYPE_BLE = 1
ARSDK_BACKEND_TYPE_MUX = 2
arsdk_backend_type = ctypes.c_int32 # enum
class struct_arsdk_publisher_cfg(Structure):
    pass

struct_arsdk_publisher_cfg._pack_ = True # source:False
struct_arsdk_publisher_cfg._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('type', arsdk_device_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('id', POINTER_T(ctypes.c_char)),
]

class struct_arsdk_backend_listen_cbs(Structure):
    pass

class struct_arsdk_peer_info(Structure):
    pass

struct_arsdk_backend_listen_cbs._pack_ = True # source:False
struct_arsdk_backend_listen_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('conn_req', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_info), POINTER_T(None))),
]

arsdk_socket_kind_str = _libraries['libarsdk.so'].arsdk_socket_kind_str
arsdk_socket_kind_str.restype = POINTER_T(ctypes.c_char)
arsdk_socket_kind_str.argtypes = [arsdk_socket_kind]
arsdk_device_type_str = _libraries['libarsdk.so'].arsdk_device_type_str
arsdk_device_type_str.restype = POINTER_T(ctypes.c_char)
arsdk_device_type_str.argtypes = [arsdk_device_type]
arsdk_conn_cancel_reason_str = _libraries['libarsdk.so'].arsdk_conn_cancel_reason_str
arsdk_conn_cancel_reason_str.restype = POINTER_T(ctypes.c_char)
arsdk_conn_cancel_reason_str.argtypes = [arsdk_conn_cancel_reason]
arsdk_link_status_str = _libraries['libarsdk.so'].arsdk_link_status_str
arsdk_link_status_str.restype = POINTER_T(ctypes.c_char)
arsdk_link_status_str.argtypes = [arsdk_link_status]
arsdk_backend_type_str = _libraries['libarsdk.so'].arsdk_backend_type_str
arsdk_backend_type_str.restype = POINTER_T(ctypes.c_char)
arsdk_backend_type_str.argtypes = [arsdk_backend_type]
class struct_arsdk_backend_net(Structure):
    pass

class struct_arsdk_backend_net_cfg(Structure):
    pass

struct_arsdk_backend_net_cfg._pack_ = True # source:False
struct_arsdk_backend_net_cfg._fields_ = [
    ('iface', POINTER_T(ctypes.c_char)),
    ('qos_mode_supported', ctypes.c_int32),
    ('stream_supported', ctypes.c_int32),
    ('proto_v_min', ctypes.c_uint32),
    ('proto_v_max', ctypes.c_uint32),
]

arsdk_backend_net_socket_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_backend_net), ctypes.c_int32, arsdk_socket_kind, POINTER_T(None))
arsdk_backend_net_new = _libraries['libarsdk.so'].arsdk_backend_net_new
arsdk_backend_net_new.restype = ctypes.c_int32
arsdk_backend_net_new.argtypes = [POINTER_T(struct_arsdk_mngr), POINTER_T(struct_arsdk_backend_net_cfg), POINTER_T(POINTER_T(struct_arsdk_backend_net))]
arsdk_backend_net_destroy = _libraries['libarsdk.so'].arsdk_backend_net_destroy
arsdk_backend_net_destroy.restype = ctypes.c_int32
arsdk_backend_net_destroy.argtypes = [POINTER_T(struct_arsdk_backend_net)]
arsdk_backend_net_get_parent = _libraries['libarsdk.so'].arsdk_backend_net_get_parent
arsdk_backend_net_get_parent.restype = POINTER_T(struct_arsdk_backend)
arsdk_backend_net_get_parent.argtypes = [POINTER_T(struct_arsdk_backend_net)]
arsdk_backend_net_start_listen = _libraries['libarsdk.so'].arsdk_backend_net_start_listen
arsdk_backend_net_start_listen.restype = ctypes.c_int32
arsdk_backend_net_start_listen.argtypes = [POINTER_T(struct_arsdk_backend_net), POINTER_T(struct_arsdk_backend_listen_cbs), uint16_t]
arsdk_backend_net_stop_listen = _libraries['libarsdk.so'].arsdk_backend_net_stop_listen
arsdk_backend_net_stop_listen.restype = ctypes.c_int32
arsdk_backend_net_stop_listen.argtypes = [POINTER_T(struct_arsdk_backend_net)]
arsdk_backend_net_set_socket_cb = _libraries['libarsdk.so'].arsdk_backend_net_set_socket_cb
arsdk_backend_net_set_socket_cb.restype = ctypes.c_int32
arsdk_backend_net_set_socket_cb.argtypes = [POINTER_T(struct_arsdk_backend_net), arsdk_backend_net_socket_cb_t, POINTER_T(None)]
class struct_arsdk_backend_mux(Structure):
    pass

class struct_arsdk_backend_mux_cfg(Structure):
    pass

struct_arsdk_backend_mux_cfg._pack_ = True # source:False
struct_arsdk_backend_mux_cfg._fields_ = [
    ('mux', POINTER_T(struct_mux_ctx)),
    ('stream_supported', ctypes.c_int32),
    ('proto_v_min', ctypes.c_uint32),
    ('proto_v_max', ctypes.c_uint32),
    ('proto_v', ctypes.c_uint32),
]

arsdk_backend_mux_new = _libraries['libarsdk.so'].arsdk_backend_mux_new
arsdk_backend_mux_new.restype = ctypes.c_int32
arsdk_backend_mux_new.argtypes = [POINTER_T(struct_arsdk_mngr), POINTER_T(struct_arsdk_backend_mux_cfg), POINTER_T(POINTER_T(struct_arsdk_backend_mux))]
arsdk_backend_mux_destroy = _libraries['libarsdk.so'].arsdk_backend_mux_destroy
arsdk_backend_mux_destroy.restype = ctypes.c_int32
arsdk_backend_mux_destroy.argtypes = [POINTER_T(struct_arsdk_backend_mux)]
arsdk_backend_mux_get_parent = _libraries['libarsdk.so'].arsdk_backend_mux_get_parent
arsdk_backend_mux_get_parent.restype = POINTER_T(struct_arsdk_backend)
arsdk_backend_mux_get_parent.argtypes = [POINTER_T(struct_arsdk_backend_mux)]
arsdk_backend_mux_get_mux_ctx = _libraries['libarsdk.so'].arsdk_backend_mux_get_mux_ctx
arsdk_backend_mux_get_mux_ctx.restype = POINTER_T(struct_mux_ctx)
arsdk_backend_mux_get_mux_ctx.argtypes = [POINTER_T(struct_arsdk_backend_mux)]
arsdk_backend_mux_start_listen = _libraries['libarsdk.so'].arsdk_backend_mux_start_listen
arsdk_backend_mux_start_listen.restype = ctypes.c_int32
arsdk_backend_mux_start_listen.argtypes = [POINTER_T(struct_arsdk_backend_mux), POINTER_T(struct_arsdk_backend_listen_cbs)]
arsdk_backend_mux_stop_listen = _libraries['libarsdk.so'].arsdk_backend_mux_stop_listen
arsdk_backend_mux_stop_listen.restype = ctypes.c_int32
arsdk_backend_mux_stop_listen.argtypes = [POINTER_T(struct_arsdk_backend_mux)]
class struct_arsdk_publisher_avahi(Structure):
    pass

class struct_arsdk_publisher_avahi_cfg(Structure):
    pass

struct_arsdk_publisher_avahi_cfg._pack_ = True # source:False
struct_arsdk_publisher_avahi_cfg._fields_ = [
    ('base', struct_arsdk_publisher_cfg),
    ('port', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 6),
]

arsdk_publisher_avahi_new = _libraries['libarsdk.so'].arsdk_publisher_avahi_new
arsdk_publisher_avahi_new.restype = ctypes.c_int32
arsdk_publisher_avahi_new.argtypes = [POINTER_T(struct_arsdk_backend_net), POINTER_T(struct_pomp_loop), POINTER_T(POINTER_T(struct_arsdk_publisher_avahi))]
arsdk_publisher_avahi_destroy = _libraries['libarsdk.so'].arsdk_publisher_avahi_destroy
arsdk_publisher_avahi_destroy.restype = ctypes.c_int32
arsdk_publisher_avahi_destroy.argtypes = [POINTER_T(struct_arsdk_publisher_avahi)]
arsdk_publisher_avahi_start = _libraries['libarsdk.so'].arsdk_publisher_avahi_start
arsdk_publisher_avahi_start.restype = ctypes.c_int32
arsdk_publisher_avahi_start.argtypes = [POINTER_T(struct_arsdk_publisher_avahi), POINTER_T(struct_arsdk_publisher_avahi_cfg)]
arsdk_publisher_avahi_stop = _libraries['libarsdk.so'].arsdk_publisher_avahi_stop
arsdk_publisher_avahi_stop.restype = ctypes.c_int32
arsdk_publisher_avahi_stop.argtypes = [POINTER_T(struct_arsdk_publisher_avahi)]
class struct_arsdk_publisher_net(Structure):
    pass

class struct_arsdk_publisher_net_cfg(Structure):
    pass

struct_arsdk_publisher_net_cfg._pack_ = True # source:False
struct_arsdk_publisher_net_cfg._fields_ = [
    ('base', struct_arsdk_publisher_cfg),
    ('port', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 6),
]

arsdk_publisher_net_new = _libraries['libarsdk.so'].arsdk_publisher_net_new
arsdk_publisher_net_new.restype = ctypes.c_int32
arsdk_publisher_net_new.argtypes = [POINTER_T(struct_arsdk_backend_net), POINTER_T(struct_pomp_loop), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_arsdk_publisher_net))]
arsdk_publisher_net_destroy = _libraries['libarsdk.so'].arsdk_publisher_net_destroy
arsdk_publisher_net_destroy.restype = ctypes.c_int32
arsdk_publisher_net_destroy.argtypes = [POINTER_T(struct_arsdk_publisher_net)]
arsdk_publisher_net_start = _libraries['libarsdk.so'].arsdk_publisher_net_start
arsdk_publisher_net_start.restype = ctypes.c_int32
arsdk_publisher_net_start.argtypes = [POINTER_T(struct_arsdk_publisher_net), POINTER_T(struct_arsdk_publisher_net_cfg)]
arsdk_publisher_net_stop = _libraries['libarsdk.so'].arsdk_publisher_net_stop
arsdk_publisher_net_stop.restype = ctypes.c_int32
arsdk_publisher_net_stop.argtypes = [POINTER_T(struct_arsdk_publisher_net)]
class struct_arsdk_publisher_mux(Structure):
    pass

arsdk_publisher_mux_new = _libraries['libarsdk.so'].arsdk_publisher_mux_new
arsdk_publisher_mux_new.restype = ctypes.c_int32
arsdk_publisher_mux_new.argtypes = [POINTER_T(struct_arsdk_backend_mux), POINTER_T(struct_mux_ctx), POINTER_T(POINTER_T(struct_arsdk_publisher_mux))]
arsdk_publisher_mux_destroy = _libraries['libarsdk.so'].arsdk_publisher_mux_destroy
arsdk_publisher_mux_destroy.restype = ctypes.c_int32
arsdk_publisher_mux_destroy.argtypes = [POINTER_T(struct_arsdk_publisher_mux)]
arsdk_publisher_mux_start = _libraries['libarsdk.so'].arsdk_publisher_mux_start
arsdk_publisher_mux_start.restype = ctypes.c_int32
arsdk_publisher_mux_start.argtypes = [POINTER_T(struct_arsdk_publisher_mux), POINTER_T(struct_arsdk_publisher_cfg)]
arsdk_publisher_mux_stop = _libraries['libarsdk.so'].arsdk_publisher_mux_stop
arsdk_publisher_mux_stop.restype = ctypes.c_int32
arsdk_publisher_mux_stop.argtypes = [POINTER_T(struct_arsdk_publisher_mux)]
struct_arsdk_peer_info._pack_ = True # source:False
struct_arsdk_peer_info._fields_ = [
    ('backend_type', arsdk_backend_type),
    ('proto_v', ctypes.c_uint32),
    ('ctrl_name', POINTER_T(ctypes.c_char)),
    ('ctrl_type', POINTER_T(ctypes.c_char)),
    ('ctrl_addr', POINTER_T(ctypes.c_char)),
    ('device_id', POINTER_T(ctypes.c_char)),
    ('json', POINTER_T(ctypes.c_char)),
]

class struct_arsdk_peer_conn_cfg(Structure):
    pass

struct_arsdk_peer_conn_cfg._pack_ = True # source:False
struct_arsdk_peer_conn_cfg._fields_ = [
    ('json', POINTER_T(ctypes.c_char)),
]

class struct_arsdk_peer_conn_cbs(Structure):
    pass

struct_arsdk_peer_conn_cbs._pack_ = True # source:False
struct_arsdk_peer_conn_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('connected', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_info), POINTER_T(None))),
    ('disconnected', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_info), POINTER_T(None))),
    ('canceled', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_info), arsdk_conn_cancel_reason, POINTER_T(None))),
    ('link_status', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_info), arsdk_link_status, POINTER_T(None))),
]

arsdk_peer_get_handle = _libraries['libarsdk.so'].arsdk_peer_get_handle
arsdk_peer_get_handle.restype = uint16_t
arsdk_peer_get_handle.argtypes = [POINTER_T(struct_arsdk_peer)]
arsdk_peer_get_info = _libraries['libarsdk.so'].arsdk_peer_get_info
arsdk_peer_get_info.restype = ctypes.c_int32
arsdk_peer_get_info.argtypes = [POINTER_T(struct_arsdk_peer), POINTER_T(POINTER_T(struct_arsdk_peer_info))]
arsdk_peer_get_backend = _libraries['libarsdk.so'].arsdk_peer_get_backend
arsdk_peer_get_backend.restype = POINTER_T(struct_arsdk_backend)
arsdk_peer_get_backend.argtypes = [POINTER_T(struct_arsdk_peer)]
arsdk_peer_accept = _libraries['libarsdk.so'].arsdk_peer_accept
arsdk_peer_accept.restype = ctypes.c_int32
arsdk_peer_accept.argtypes = [POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_peer_conn_cfg), POINTER_T(struct_arsdk_peer_conn_cbs), POINTER_T(struct_pomp_loop)]
arsdk_peer_reject = _libraries['libarsdk.so'].arsdk_peer_reject
arsdk_peer_reject.restype = ctypes.c_int32
arsdk_peer_reject.argtypes = [POINTER_T(struct_arsdk_peer)]
arsdk_peer_disconnect = _libraries['libarsdk.so'].arsdk_peer_disconnect
arsdk_peer_disconnect.restype = ctypes.c_int32
arsdk_peer_disconnect.argtypes = [POINTER_T(struct_arsdk_peer)]
arsdk_peer_create_cmd_itf = _libraries['libarsdk.so'].arsdk_peer_create_cmd_itf
arsdk_peer_create_cmd_itf.restype = ctypes.c_int32
arsdk_peer_create_cmd_itf.argtypes = [POINTER_T(struct_arsdk_peer), POINTER_T(struct_arsdk_cmd_itf_cbs), POINTER_T(POINTER_T(struct_arsdk_cmd_itf))]
arsdk_peer_get_cmd_itf = _libraries['libarsdk.so'].arsdk_peer_get_cmd_itf
arsdk_peer_get_cmd_itf.restype = POINTER_T(struct_arsdk_cmd_itf)
arsdk_peer_get_cmd_itf.argtypes = [POINTER_T(struct_arsdk_peer)]
arsdk_get_cmd_table = _libraries['libarsdk.so'].arsdk_get_cmd_table
arsdk_get_cmd_table.restype = POINTER_T(POINTER_T(POINTER_T(POINTER_T(struct_arsdk_cmd_desc))))
arsdk_get_cmd_table.argtypes = []
_ARSDKCTRL_H_ = True # macro
_ARSDK_CTRL_H_ = True # macro
_ARSDKCTRL_BACKEND_H_ = True # macro
_ARSDKCTRL_BACKEND_NET_H_ = True # macro
ARSDKCTRL_BACKEND_NET_PROTO_MIN = (1) # macro
ARSDKCTRL_BACKEND_NET_PROTO_MAX = (3) # macro
_ARSDKCTRL_BACKEND_MUX_H_ = True # macro
ARSDKCTRL_BACKEND_MUX_PROTO_MIN = (1) # macro
ARSDKCTRL_BACKEND_MUX_PROTO_MAX = (3) # macro
_ARSDK_DISCOVERY_AVAHI_H_ = True # macro
_ARSDK_DISCOVERY_NET_H_ = True # macro
_ARSDK_DISCOVERY_MUX_H_ = True # macro
_ARSDK_FTP_ITF_H_ = True # macro
_ARSDK_MEDIA_ITF_H_ = True # macro
_ARSDK_UPDATER_ITF_H_ = True # macro
_ARSDK_BLACKBOX_ITF_H_ = True # macro
_ARSDK_CRASHML_ITF_H_ = True # macro
_ARSDK_PUD_ITF_H_ = True # macro
_ARSDK_EPHEMERIS_ITF_H_ = True # macro
_ARSDK_DEVICE_H_ = True # macro
ARSDK_DEVICE_INVALID_HANDLE = (0) # macro
class struct_arsdk_ctrl(Structure):
    pass

class struct_arsdkctrl_backend(Structure):
    pass

class struct_arsdk_ftp_itf(Structure):
    pass

class struct_arsdk_media_itf(Structure):
    pass

class struct_arsdk_updater_itf(Structure):
    pass

class struct_arsdk_blackbox_itf(Structure):
    pass

class struct_arsdk_crashml_itf(Structure):
    pass

class struct_arsdk_flight_log_itf(Structure):
    pass

class struct_arsdk_pud_itf(Structure):
    pass

class struct_arsdk_ephemeris_itf(Structure):
    pass

class struct_arsdk_discovery(Structure):
    pass

class struct_arsdk_device(Structure):
    pass

class struct_arsdk_device_mngr(Structure):
    pass

class struct_arsdk_stream_itf(Structure):
    pass

class struct_arsdk_device_tcp_proxy(Structure):
    pass

class struct_arsdk_ctrl_device_cbs(Structure):
    pass

struct_arsdk_ctrl_device_cbs._pack_ = True # source:False
struct_arsdk_ctrl_device_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('added', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(None))),
    ('removed', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(None))),
]

arsdk_ctrl_new = _libraries['libarsdkctrl.so'].arsdk_ctrl_new
arsdk_ctrl_new.restype = ctypes.c_int32
arsdk_ctrl_new.argtypes = [POINTER_T(struct_pomp_loop), POINTER_T(POINTER_T(struct_arsdk_ctrl))]
arsdk_ctrl_set_device_cbs = _libraries['libarsdkctrl.so'].arsdk_ctrl_set_device_cbs
arsdk_ctrl_set_device_cbs.restype = ctypes.c_int32
arsdk_ctrl_set_device_cbs.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdk_ctrl_device_cbs)]
arsdk_ctrl_get_loop = _libraries['libarsdkctrl.so'].arsdk_ctrl_get_loop
arsdk_ctrl_get_loop.restype = POINTER_T(struct_pomp_loop)
arsdk_ctrl_get_loop.argtypes = [POINTER_T(struct_arsdk_ctrl)]
arsdk_ctrl_destroy = _libraries['libarsdkctrl.so'].arsdk_ctrl_destroy
arsdk_ctrl_destroy.restype = ctypes.c_int32
arsdk_ctrl_destroy.argtypes = [POINTER_T(struct_arsdk_ctrl)]
arsdk_ctrl_next_device = _libraries['libarsdkctrl.so'].arsdk_ctrl_next_device
arsdk_ctrl_next_device.restype = POINTER_T(struct_arsdk_device)
arsdk_ctrl_next_device.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdk_device)]
arsdk_ctrl_get_device = _libraries['libarsdkctrl.so'].arsdk_ctrl_get_device
arsdk_ctrl_get_device.restype = POINTER_T(struct_arsdk_device)
arsdk_ctrl_get_device.argtypes = [POINTER_T(struct_arsdk_ctrl), uint16_t]
class struct_arsdk_discovery_cfg(Structure):
    pass

struct_arsdk_discovery_cfg._pack_ = True # source:False
struct_arsdk_discovery_cfg._fields_ = [
    ('types', POINTER_T(arsdk_device_type)),
    ('count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_arsdkctrl_backend_net(Structure):
    pass

class struct_arsdkctrl_backend_net_cfg(Structure):
    pass

struct_arsdkctrl_backend_net_cfg._pack_ = True # source:False
struct_arsdkctrl_backend_net_cfg._fields_ = [
    ('iface', POINTER_T(ctypes.c_char)),
    ('qos_mode_supported', ctypes.c_int32),
    ('stream_supported', ctypes.c_int32),
    ('proto_v_min', ctypes.c_uint32),
    ('proto_v_max', ctypes.c_uint32),
]

arsdkctrl_backend_net_socket_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdkctrl_backend_net), ctypes.c_int32, arsdk_socket_kind, POINTER_T(None))
arsdkctrl_backend_net_new = _libraries['libarsdkctrl.so'].arsdkctrl_backend_net_new
arsdkctrl_backend_net_new.restype = ctypes.c_int32
arsdkctrl_backend_net_new.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_net_cfg), POINTER_T(POINTER_T(struct_arsdkctrl_backend_net))]
arsdkctrl_backend_net_destroy = _libraries['libarsdkctrl.so'].arsdkctrl_backend_net_destroy
arsdkctrl_backend_net_destroy.restype = ctypes.c_int32
arsdkctrl_backend_net_destroy.argtypes = [POINTER_T(struct_arsdkctrl_backend_net)]
arsdkctrl_backend_net_get_parent = _libraries['libarsdkctrl.so'].arsdkctrl_backend_net_get_parent
arsdkctrl_backend_net_get_parent.restype = POINTER_T(struct_arsdkctrl_backend)
arsdkctrl_backend_net_get_parent.argtypes = [POINTER_T(struct_arsdkctrl_backend_net)]
arsdkctrl_backend_net_set_socket_cb = _libraries['libarsdkctrl.so'].arsdkctrl_backend_net_set_socket_cb
arsdkctrl_backend_net_set_socket_cb.restype = ctypes.c_int32
arsdkctrl_backend_net_set_socket_cb.argtypes = [POINTER_T(struct_arsdkctrl_backend_net), arsdkctrl_backend_net_socket_cb_t, POINTER_T(None)]
class struct_arsdkctrl_backend_mux(Structure):
    pass

class struct_arsdkctrl_backend_mux_cfg(Structure):
    pass

struct_arsdkctrl_backend_mux_cfg._pack_ = True # source:False
struct_arsdkctrl_backend_mux_cfg._fields_ = [
    ('mux', POINTER_T(struct_mux_ctx)),
    ('stream_supported', ctypes.c_int32),
    ('proto_v_min', ctypes.c_uint32),
    ('proto_v_max', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

arsdkctrl_backend_mux_new = _libraries['libarsdkctrl.so'].arsdkctrl_backend_mux_new
arsdkctrl_backend_mux_new.restype = ctypes.c_int32
arsdkctrl_backend_mux_new.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_mux_cfg), POINTER_T(POINTER_T(struct_arsdkctrl_backend_mux))]
arsdkctrl_backend_mux_destroy = _libraries['libarsdkctrl.so'].arsdkctrl_backend_mux_destroy
arsdkctrl_backend_mux_destroy.restype = ctypes.c_int32
arsdkctrl_backend_mux_destroy.argtypes = [POINTER_T(struct_arsdkctrl_backend_mux)]
arsdkctrl_backend_mux_get_parent = _libraries['libarsdkctrl.so'].arsdkctrl_backend_mux_get_parent
arsdkctrl_backend_mux_get_parent.restype = POINTER_T(struct_arsdkctrl_backend)
arsdkctrl_backend_mux_get_parent.argtypes = [POINTER_T(struct_arsdkctrl_backend_mux)]
arsdkctrl_backend_mux_get_mux_ctx = _libraries['libarsdkctrl.so'].arsdkctrl_backend_mux_get_mux_ctx
arsdkctrl_backend_mux_get_mux_ctx.restype = POINTER_T(struct_mux_ctx)
arsdkctrl_backend_mux_get_mux_ctx.argtypes = [POINTER_T(struct_arsdkctrl_backend_mux)]
class struct_arsdk_discovery_avahi(Structure):
    pass

arsdk_discovery_avahi_new = _libraries['libarsdkctrl.so'].arsdk_discovery_avahi_new
arsdk_discovery_avahi_new.restype = ctypes.c_int32
arsdk_discovery_avahi_new.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_net), POINTER_T(struct_arsdk_discovery_cfg), POINTER_T(POINTER_T(struct_arsdk_discovery_avahi))]
arsdk_discovery_avahi_destroy = _libraries['libarsdkctrl.so'].arsdk_discovery_avahi_destroy
arsdk_discovery_avahi_destroy.restype = ctypes.c_int32
arsdk_discovery_avahi_destroy.argtypes = [POINTER_T(struct_arsdk_discovery_avahi)]
arsdk_discovery_avahi_start = _libraries['libarsdkctrl.so'].arsdk_discovery_avahi_start
arsdk_discovery_avahi_start.restype = ctypes.c_int32
arsdk_discovery_avahi_start.argtypes = [POINTER_T(struct_arsdk_discovery_avahi)]
arsdk_discovery_avahi_stop = _libraries['libarsdkctrl.so'].arsdk_discovery_avahi_stop
arsdk_discovery_avahi_stop.restype = ctypes.c_int32
arsdk_discovery_avahi_stop.argtypes = [POINTER_T(struct_arsdk_discovery_avahi)]
class struct_arsdk_discovery_net(Structure):
    pass

arsdk_discovery_net_new = _libraries['libarsdkctrl.so'].arsdk_discovery_net_new
arsdk_discovery_net_new.restype = ctypes.c_int32
arsdk_discovery_net_new.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_net), POINTER_T(struct_arsdk_discovery_cfg), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_arsdk_discovery_net))]
arsdk_discovery_net_new_with_port = _libraries['libarsdkctrl.so'].arsdk_discovery_net_new_with_port
arsdk_discovery_net_new_with_port.restype = ctypes.c_int32
arsdk_discovery_net_new_with_port.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_net), POINTER_T(struct_arsdk_discovery_cfg), POINTER_T(ctypes.c_char), uint16_t, POINTER_T(POINTER_T(struct_arsdk_discovery_net))]
arsdk_discovery_net_destroy = _libraries['libarsdkctrl.so'].arsdk_discovery_net_destroy
arsdk_discovery_net_destroy.restype = ctypes.c_int32
arsdk_discovery_net_destroy.argtypes = [POINTER_T(struct_arsdk_discovery_net)]
arsdk_discovery_net_start = _libraries['libarsdkctrl.so'].arsdk_discovery_net_start
arsdk_discovery_net_start.restype = ctypes.c_int32
arsdk_discovery_net_start.argtypes = [POINTER_T(struct_arsdk_discovery_net)]
arsdk_discovery_net_stop = _libraries['libarsdkctrl.so'].arsdk_discovery_net_stop
arsdk_discovery_net_stop.restype = ctypes.c_int32
arsdk_discovery_net_stop.argtypes = [POINTER_T(struct_arsdk_discovery_net)]
class struct_arsdk_discovery_mux(Structure):
    pass

arsdk_discovery_mux_new = _libraries['libarsdkctrl.so'].arsdk_discovery_mux_new
arsdk_discovery_mux_new.restype = ctypes.c_int32
arsdk_discovery_mux_new.argtypes = [POINTER_T(struct_arsdk_ctrl), POINTER_T(struct_arsdkctrl_backend_mux), POINTER_T(struct_arsdk_discovery_cfg), POINTER_T(struct_mux_ctx), POINTER_T(POINTER_T(struct_arsdk_discovery_mux))]
arsdk_discovery_mux_destroy = _libraries['libarsdkctrl.so'].arsdk_discovery_mux_destroy
arsdk_discovery_mux_destroy.restype = ctypes.c_int32
arsdk_discovery_mux_destroy.argtypes = [POINTER_T(struct_arsdk_discovery_mux)]
arsdk_discovery_mux_start = _libraries['libarsdkctrl.so'].arsdk_discovery_mux_start
arsdk_discovery_mux_start.restype = ctypes.c_int32
arsdk_discovery_mux_start.argtypes = [POINTER_T(struct_arsdk_discovery_mux)]
arsdk_discovery_mux_stop = _libraries['libarsdkctrl.so'].arsdk_discovery_mux_stop
arsdk_discovery_mux_stop.restype = ctypes.c_int32
arsdk_discovery_mux_stop.argtypes = [POINTER_T(struct_arsdk_discovery_mux)]
class struct_arsdk_ftp_file_list(Structure):
    pass

class struct_arsdk_ftp_req_put(Structure):
    pass

class struct_arsdk_ftp_req_get(Structure):
    pass

class struct_arsdk_ftp_req_rename(Structure):
    pass

class struct_arsdk_ftp_req_delete(Structure):
    pass

class struct_arsdk_ftp_req_list(Structure):
    pass

class struct_arsdk_ftp_file(Structure):
    pass


# values for enumeration 'arsdk_ftp_srv_type'
arsdk_ftp_srv_type__enumvalues = {
    -1: 'ARSDK_FTP_SRV_TYPE_UNKNOWN',
    0: 'ARSDK_FTP_SRV_TYPE_MEDIA',
    1: 'ARSDK_FTP_SRV_TYPE_UPDATE',
    2: 'ARSDK_FTP_SRV_TYPE_FLIGHT_PLAN',
}
ARSDK_FTP_SRV_TYPE_UNKNOWN = -1
ARSDK_FTP_SRV_TYPE_MEDIA = 0
ARSDK_FTP_SRV_TYPE_UPDATE = 1
ARSDK_FTP_SRV_TYPE_FLIGHT_PLAN = 2
arsdk_ftp_srv_type = ctypes.c_int32 # enum

# values for enumeration 'arsdk_ftp_req_status'
arsdk_ftp_req_status__enumvalues = {
    0: 'ARSDK_FTP_REQ_STATUS_OK',
    1: 'ARSDK_FTP_REQ_STATUS_CANCELED',
    2: 'ARSDK_FTP_REQ_STATUS_FAILED',
    3: 'ARSDK_FTP_REQ_STATUS_ABORTED',
}
ARSDK_FTP_REQ_STATUS_OK = 0
ARSDK_FTP_REQ_STATUS_CANCELED = 1
ARSDK_FTP_REQ_STATUS_FAILED = 2
ARSDK_FTP_REQ_STATUS_ABORTED = 3
arsdk_ftp_req_status = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_ftp_file_type'
arsdk_ftp_file_type__enumvalues = {
    -1: 'ARSDK_FTP_FILE_TYPE_UNKNOWN',
    0: 'ARSDK_FTP_FILE_TYPE_FILE',
    1: 'ARSDK_FTP_FILE_TYPE_DIR',
    2: 'ARSDK_FTP_FILE_TYPE_LINK',
}
ARSDK_FTP_FILE_TYPE_UNKNOWN = -1
ARSDK_FTP_FILE_TYPE_FILE = 0
ARSDK_FTP_FILE_TYPE_DIR = 1
ARSDK_FTP_FILE_TYPE_LINK = 2
arsdk_ftp_file_type = ctypes.c_int32 # enum
class struct_arsdk_ftp_req_put_cbs(Structure):
    pass

struct_arsdk_ftp_req_put_cbs._pack_ = True # source:False
struct_arsdk_ftp_req_put_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_put), ctypes.c_float, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_put), arsdk_ftp_req_status, ctypes.c_int32, POINTER_T(None))),
]

class struct_arsdk_ftp_req_get_cbs(Structure):
    pass

struct_arsdk_ftp_req_get_cbs._pack_ = True # source:False
struct_arsdk_ftp_req_get_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_get), ctypes.c_float, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_get), arsdk_ftp_req_status, ctypes.c_int32, POINTER_T(None))),
]

class struct_arsdk_ftp_req_rename_cbs(Structure):
    pass

struct_arsdk_ftp_req_rename_cbs._pack_ = True # source:False
struct_arsdk_ftp_req_rename_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_rename), arsdk_ftp_req_status, ctypes.c_int32, POINTER_T(None))),
]

class struct_arsdk_ftp_req_delete_cbs(Structure):
    pass

struct_arsdk_ftp_req_delete_cbs._pack_ = True # source:False
struct_arsdk_ftp_req_delete_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_delete), arsdk_ftp_req_status, ctypes.c_int32, POINTER_T(None))),
]

class struct_arsdk_ftp_req_list_cbs(Structure):
    pass

struct_arsdk_ftp_req_list_cbs._pack_ = True # source:False
struct_arsdk_ftp_req_list_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_list), arsdk_ftp_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_ftp_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_cancel_all
arsdk_ftp_itf_cancel_all.restype = ctypes.c_int32
arsdk_ftp_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_ftp_itf)]
arsdk_ftp_itf_create_req_get = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_get
arsdk_ftp_itf_create_req_get.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_get.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_get_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), uint8_t, POINTER_T(POINTER_T(struct_arsdk_ftp_req_get))]
arsdk_ftp_req_get_cancel = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_cancel
arsdk_ftp_req_get_cancel.restype = ctypes.c_int32
arsdk_ftp_req_get_cancel.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_remote_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_remote_path
arsdk_ftp_req_get_get_remote_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_get_get_remote_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_local_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_local_path
arsdk_ftp_req_get_get_local_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_get_get_local_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_buffer = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_buffer
arsdk_ftp_req_get_get_buffer.restype = POINTER_T(struct_pomp_buffer)
arsdk_ftp_req_get_get_buffer.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_dev_type
arsdk_ftp_req_get_get_dev_type.restype = arsdk_device_type
arsdk_ftp_req_get_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_total_size = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_total_size
arsdk_ftp_req_get_get_total_size.restype = size_t
arsdk_ftp_req_get_get_total_size.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_req_get_get_dlsize = _libraries['libarsdkctrl.so'].arsdk_ftp_req_get_get_dlsize
arsdk_ftp_req_get_get_dlsize.restype = size_t
arsdk_ftp_req_get_get_dlsize.argtypes = [POINTER_T(struct_arsdk_ftp_req_get)]
arsdk_ftp_itf_create_req_put = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_put
arsdk_ftp_itf_create_req_put.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_put.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_put_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), uint8_t, POINTER_T(POINTER_T(struct_arsdk_ftp_req_put))]
arsdk_ftp_itf_create_req_put_buff = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_put_buff
arsdk_ftp_itf_create_req_put_buff.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_put_buff.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_put_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(struct_pomp_buffer), uint8_t, POINTER_T(POINTER_T(struct_arsdk_ftp_req_put))]
arsdk_ftp_req_put_cancel = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_cancel
arsdk_ftp_req_put_cancel.restype = ctypes.c_int32
arsdk_ftp_req_put_cancel.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_req_put_get_remote_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_get_remote_path
arsdk_ftp_req_put_get_remote_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_put_get_remote_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_req_put_get_local_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_get_local_path
arsdk_ftp_req_put_get_local_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_put_get_local_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_req_put_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_get_dev_type
arsdk_ftp_req_put_get_dev_type.restype = arsdk_device_type
arsdk_ftp_req_put_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_req_put_get_total_size = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_get_total_size
arsdk_ftp_req_put_get_total_size.restype = size_t
arsdk_ftp_req_put_get_total_size.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_req_put_get_ulsize = _libraries['libarsdkctrl.so'].arsdk_ftp_req_put_get_ulsize
arsdk_ftp_req_put_get_ulsize.restype = size_t
arsdk_ftp_req_put_get_ulsize.argtypes = [POINTER_T(struct_arsdk_ftp_req_put)]
arsdk_ftp_itf_create_req_rename = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_rename
arsdk_ftp_itf_create_req_rename.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_rename.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_rename_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_arsdk_ftp_req_rename))]
arsdk_ftp_req_rename_cancel = _libraries['libarsdkctrl.so'].arsdk_ftp_req_rename_cancel
arsdk_ftp_req_rename_cancel.restype = ctypes.c_int32
arsdk_ftp_req_rename_cancel.argtypes = [POINTER_T(struct_arsdk_ftp_req_rename)]
arsdk_ftp_req_rename_get_src = _libraries['libarsdkctrl.so'].arsdk_ftp_req_rename_get_src
arsdk_ftp_req_rename_get_src.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_rename_get_src.argtypes = [POINTER_T(struct_arsdk_ftp_req_rename)]
arsdk_ftp_req_rename_get_dst = _libraries['libarsdkctrl.so'].arsdk_ftp_req_rename_get_dst
arsdk_ftp_req_rename_get_dst.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_rename_get_dst.argtypes = [POINTER_T(struct_arsdk_ftp_req_rename)]
arsdk_ftp_req_rename_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ftp_req_rename_get_dev_type
arsdk_ftp_req_rename_get_dev_type.restype = arsdk_device_type
arsdk_ftp_req_rename_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ftp_req_rename)]
arsdk_ftp_itf_create_req_delete = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_delete
arsdk_ftp_itf_create_req_delete.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_delete.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_delete_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_arsdk_ftp_req_delete))]
arsdk_ftp_req_delete_cancel = _libraries['libarsdkctrl.so'].arsdk_ftp_req_delete_cancel
arsdk_ftp_req_delete_cancel.restype = ctypes.c_int32
arsdk_ftp_req_delete_cancel.argtypes = [POINTER_T(struct_arsdk_ftp_req_delete)]
arsdk_ftp_req_delete_get_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_delete_get_path
arsdk_ftp_req_delete_get_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_delete_get_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_delete)]
arsdk_ftp_req_delete_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ftp_req_delete_get_dev_type
arsdk_ftp_req_delete_get_dev_type.restype = arsdk_device_type
arsdk_ftp_req_delete_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ftp_req_delete)]
arsdk_ftp_itf_create_req_list = _libraries['libarsdkctrl.so'].arsdk_ftp_itf_create_req_list
arsdk_ftp_itf_create_req_list.restype = ctypes.c_int32
arsdk_ftp_itf_create_req_list.argtypes = [POINTER_T(struct_arsdk_ftp_itf), POINTER_T(struct_arsdk_ftp_req_list_cbs), arsdk_device_type, arsdk_ftp_srv_type, POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_arsdk_ftp_req_list))]
arsdk_ftp_req_list_cancel = _libraries['libarsdkctrl.so'].arsdk_ftp_req_list_cancel
arsdk_ftp_req_list_cancel.restype = ctypes.c_int32
arsdk_ftp_req_list_cancel.argtypes = [POINTER_T(struct_arsdk_ftp_req_list)]
arsdk_ftp_req_list_get_path = _libraries['libarsdkctrl.so'].arsdk_ftp_req_list_get_path
arsdk_ftp_req_list_get_path.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_req_list_get_path.argtypes = [POINTER_T(struct_arsdk_ftp_req_list)]
arsdk_ftp_req_list_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ftp_req_list_get_dev_type
arsdk_ftp_req_list_get_dev_type.restype = arsdk_device_type
arsdk_ftp_req_list_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ftp_req_list)]
arsdk_ftp_req_list_get_result = _libraries['libarsdkctrl.so'].arsdk_ftp_req_list_get_result
arsdk_ftp_req_list_get_result.restype = POINTER_T(struct_arsdk_ftp_file_list)
arsdk_ftp_req_list_get_result.argtypes = [POINTER_T(struct_arsdk_ftp_req_list)]
arsdk_ftp_file_list_next_file = _libraries['libarsdkctrl.so'].arsdk_ftp_file_list_next_file
arsdk_ftp_file_list_next_file.restype = POINTER_T(struct_arsdk_ftp_file)
arsdk_ftp_file_list_next_file.argtypes = [POINTER_T(struct_arsdk_ftp_file_list), POINTER_T(struct_arsdk_ftp_file)]
arsdk_ftp_file_list_get_count = _libraries['libarsdkctrl.so'].arsdk_ftp_file_list_get_count
arsdk_ftp_file_list_get_count.restype = size_t
arsdk_ftp_file_list_get_count.argtypes = [POINTER_T(struct_arsdk_ftp_file_list)]
arsdk_ftp_file_list_ref = _libraries['libarsdkctrl.so'].arsdk_ftp_file_list_ref
arsdk_ftp_file_list_ref.restype = None
arsdk_ftp_file_list_ref.argtypes = [POINTER_T(struct_arsdk_ftp_file_list)]
arsdk_ftp_file_list_unref = _libraries['libarsdkctrl.so'].arsdk_ftp_file_list_unref
arsdk_ftp_file_list_unref.restype = None
arsdk_ftp_file_list_unref.argtypes = [POINTER_T(struct_arsdk_ftp_file_list)]
arsdk_ftp_file_get_name = _libraries['libarsdkctrl.so'].arsdk_ftp_file_get_name
arsdk_ftp_file_get_name.restype = POINTER_T(ctypes.c_char)
arsdk_ftp_file_get_name.argtypes = [POINTER_T(struct_arsdk_ftp_file)]
arsdk_ftp_file_get_size = _libraries['libarsdkctrl.so'].arsdk_ftp_file_get_size
arsdk_ftp_file_get_size.restype = size_t
arsdk_ftp_file_get_size.argtypes = [POINTER_T(struct_arsdk_ftp_file)]
arsdk_ftp_file_get_type = _libraries['libarsdkctrl.so'].arsdk_ftp_file_get_type
arsdk_ftp_file_get_type.restype = arsdk_ftp_file_type
arsdk_ftp_file_get_type.argtypes = [POINTER_T(struct_arsdk_ftp_file)]
arsdk_ftp_file_ref = _libraries['libarsdkctrl.so'].arsdk_ftp_file_ref
arsdk_ftp_file_ref.restype = None
arsdk_ftp_file_ref.argtypes = [POINTER_T(struct_arsdk_ftp_file)]
arsdk_ftp_file_unref = _libraries['libarsdkctrl.so'].arsdk_ftp_file_unref
arsdk_ftp_file_unref.restype = None
arsdk_ftp_file_unref.argtypes = [POINTER_T(struct_arsdk_ftp_file)]
class struct_arsdk_media(Structure):
    pass

class struct_arsdk_media_res(Structure):
    pass

class struct_arsdk_media_list(Structure):
    pass

class struct_arsdk_media_req_list(Structure):
    pass

class struct_arsdk_media_req_download(Structure):
    pass

class struct_arsdk_media_req_delete(Structure):
    pass


# values for enumeration 'arsdk_media_req_status'
arsdk_media_req_status__enumvalues = {
    0: 'ARSDK_MEDIA_REQ_STATUS_OK',
    1: 'ARSDK_MEDIA_REQ_STATUS_CANCELED',
    2: 'ARSDK_MEDIA_REQ_STATUS_FAILED',
    3: 'ARSDK_MEDIA_REQ_STATUS_ABORTED',
}
ARSDK_MEDIA_REQ_STATUS_OK = 0
ARSDK_MEDIA_REQ_STATUS_CANCELED = 1
ARSDK_MEDIA_REQ_STATUS_FAILED = 2
ARSDK_MEDIA_REQ_STATUS_ABORTED = 3
arsdk_media_req_status = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_media_type'
arsdk_media_type__enumvalues = {
    0: 'ARSDK_MEDIA_TYPE_UNKNOWN',
    1: 'ARSDK_MEDIA_TYPE_PHOTO',
    2: 'ARSDK_MEDIA_TYPE_VIDEO',
    3: 'ARSDK_MEDIA_TYPE_ALL',
}
ARSDK_MEDIA_TYPE_UNKNOWN = 0
ARSDK_MEDIA_TYPE_PHOTO = 1
ARSDK_MEDIA_TYPE_VIDEO = 2
ARSDK_MEDIA_TYPE_ALL = 3
arsdk_media_type = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_media_res_type'
arsdk_media_res_type__enumvalues = {
    -1: 'ARSDK_MEDIA_RES_TYPE_UNKNOWN',
    0: 'ARSDK_MEDIA_RES_TYPE_PHOTO',
    1: 'ARSDK_MEDIA_RES_TYPE_VIDEO',
    2: 'ARSDK_MEDIA_RES_TYPE_THUMBNAIL',
}
ARSDK_MEDIA_RES_TYPE_UNKNOWN = -1
ARSDK_MEDIA_RES_TYPE_PHOTO = 0
ARSDK_MEDIA_RES_TYPE_VIDEO = 1
ARSDK_MEDIA_RES_TYPE_THUMBNAIL = 2
arsdk_media_res_type = ctypes.c_int32 # enum

# values for enumeration 'arsdk_media_res_format'
arsdk_media_res_format__enumvalues = {
    -1: 'ARSDK_MEDIA_RES_FMT_UNKNOWN',
    0: 'ARSDK_MEDIA_RES_FMT_JPG',
    1: 'ARSDK_MEDIA_RES_FMT_DNG',
    2: 'ARSDK_MEDIA_RES_FMT_MP4',
}
ARSDK_MEDIA_RES_FMT_UNKNOWN = -1
ARSDK_MEDIA_RES_FMT_JPG = 0
ARSDK_MEDIA_RES_FMT_DNG = 1
ARSDK_MEDIA_RES_FMT_MP4 = 2
arsdk_media_res_format = ctypes.c_int32 # enum
class struct_arsdk_media_req_list_cbs(Structure):
    pass

struct_arsdk_media_req_list_cbs._pack_ = True # source:False
struct_arsdk_media_req_list_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_list), arsdk_media_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_media_itf_create_req_list = _libraries['libarsdkctrl.so'].arsdk_media_itf_create_req_list
arsdk_media_itf_create_req_list.restype = ctypes.c_int32
arsdk_media_itf_create_req_list.argtypes = [POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_list_cbs), uint32_t, arsdk_device_type, POINTER_T(POINTER_T(struct_arsdk_media_req_list))]
arsdk_media_req_list_cancel = _libraries['libarsdkctrl.so'].arsdk_media_req_list_cancel
arsdk_media_req_list_cancel.restype = ctypes.c_int32
arsdk_media_req_list_cancel.argtypes = [POINTER_T(struct_arsdk_media_req_list)]
arsdk_media_req_list_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_media_req_list_get_dev_type
arsdk_media_req_list_get_dev_type.restype = arsdk_device_type
arsdk_media_req_list_get_dev_type.argtypes = [POINTER_T(struct_arsdk_media_req_list)]
arsdk_media_req_list_get_result = _libraries['libarsdkctrl.so'].arsdk_media_req_list_get_result
arsdk_media_req_list_get_result.restype = POINTER_T(struct_arsdk_media_list)
arsdk_media_req_list_get_result.argtypes = [POINTER_T(struct_arsdk_media_req_list)]
arsdk_media_list_next_media = _libraries['libarsdkctrl.so'].arsdk_media_list_next_media
arsdk_media_list_next_media.restype = POINTER_T(struct_arsdk_media)
arsdk_media_list_next_media.argtypes = [POINTER_T(struct_arsdk_media_list), POINTER_T(struct_arsdk_media)]
arsdk_media_list_get_count = _libraries['libarsdkctrl.so'].arsdk_media_list_get_count
arsdk_media_list_get_count.restype = size_t
arsdk_media_list_get_count.argtypes = [POINTER_T(struct_arsdk_media_list)]
arsdk_media_list_ref = _libraries['libarsdkctrl.so'].arsdk_media_list_ref
arsdk_media_list_ref.restype = None
arsdk_media_list_ref.argtypes = [POINTER_T(struct_arsdk_media_list)]
arsdk_media_list_unref = _libraries['libarsdkctrl.so'].arsdk_media_list_unref
arsdk_media_list_unref.restype = None
arsdk_media_list_unref.argtypes = [POINTER_T(struct_arsdk_media_list)]
class struct_arsdk_media_req_download_cbs(Structure):
    pass

struct_arsdk_media_req_download_cbs._pack_ = True # source:False
struct_arsdk_media_req_download_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_download), ctypes.c_float, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_download), arsdk_media_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_media_itf_create_req_download = _libraries['libarsdkctrl.so'].arsdk_media_itf_create_req_download
arsdk_media_itf_create_req_download.restype = ctypes.c_int32
arsdk_media_itf_create_req_download.argtypes = [POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_download_cbs), POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char), arsdk_device_type, uint8_t, POINTER_T(POINTER_T(struct_arsdk_media_req_download))]
arsdk_media_req_download_cancel = _libraries['libarsdkctrl.so'].arsdk_media_req_download_cancel
arsdk_media_req_download_cancel.restype = ctypes.c_int32
arsdk_media_req_download_cancel.argtypes = [POINTER_T(struct_arsdk_media_req_download)]
arsdk_media_req_download_get_uri = _libraries['libarsdkctrl.so'].arsdk_media_req_download_get_uri
arsdk_media_req_download_get_uri.restype = POINTER_T(ctypes.c_char)
arsdk_media_req_download_get_uri.argtypes = [POINTER_T(struct_arsdk_media_req_download)]
arsdk_media_req_download_get_local_path = _libraries['libarsdkctrl.so'].arsdk_media_req_download_get_local_path
arsdk_media_req_download_get_local_path.restype = POINTER_T(ctypes.c_char)
arsdk_media_req_download_get_local_path.argtypes = [POINTER_T(struct_arsdk_media_req_download)]
arsdk_media_req_download_get_buffer = _libraries['libarsdkctrl.so'].arsdk_media_req_download_get_buffer
arsdk_media_req_download_get_buffer.restype = POINTER_T(struct_pomp_buffer)
arsdk_media_req_download_get_buffer.argtypes = [POINTER_T(struct_arsdk_media_req_download)]
arsdk_media_req_download_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_media_req_download_get_dev_type
arsdk_media_req_download_get_dev_type.restype = arsdk_device_type
arsdk_media_req_download_get_dev_type.argtypes = [POINTER_T(struct_arsdk_media_req_download)]
class struct_arsdk_media_req_delete_cbs(Structure):
    pass

struct_arsdk_media_req_delete_cbs._pack_ = True # source:False
struct_arsdk_media_req_delete_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_delete), arsdk_media_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_media_itf_create_req_delete = _libraries['libarsdkctrl.so'].arsdk_media_itf_create_req_delete
arsdk_media_itf_create_req_delete.restype = ctypes.c_int32
arsdk_media_itf_create_req_delete.argtypes = [POINTER_T(struct_arsdk_media_itf), POINTER_T(struct_arsdk_media_req_delete_cbs), POINTER_T(struct_arsdk_media), arsdk_device_type, POINTER_T(POINTER_T(struct_arsdk_media_req_delete))]
arsdk_media_req_delete_get_media = _libraries['libarsdkctrl.so'].arsdk_media_req_delete_get_media
arsdk_media_req_delete_get_media.restype = POINTER_T(struct_arsdk_media)
arsdk_media_req_delete_get_media.argtypes = [POINTER_T(struct_arsdk_media_req_delete)]
arsdk_media_req_delete_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_media_req_delete_get_dev_type
arsdk_media_req_delete_get_dev_type.restype = arsdk_device_type
arsdk_media_req_delete_get_dev_type.argtypes = [POINTER_T(struct_arsdk_media_req_delete)]
arsdk_media_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_media_itf_cancel_all
arsdk_media_itf_cancel_all.restype = ctypes.c_int32
arsdk_media_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_media_itf)]
arsdk_media_get_name = _libraries['libarsdkctrl.so'].arsdk_media_get_name
arsdk_media_get_name.restype = POINTER_T(ctypes.c_char)
arsdk_media_get_name.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_get_runid = _libraries['libarsdkctrl.so'].arsdk_media_get_runid
arsdk_media_get_runid.restype = POINTER_T(ctypes.c_char)
arsdk_media_get_runid.argtypes = [POINTER_T(struct_arsdk_media)]
class struct_tm(Structure):
    pass

arsdk_media_get_date = _libraries['libarsdkctrl.so'].arsdk_media_get_date
arsdk_media_get_date.restype = POINTER_T(struct_tm)
arsdk_media_get_date.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_get_type = _libraries['libarsdkctrl.so'].arsdk_media_get_type
arsdk_media_get_type.restype = arsdk_media_type
arsdk_media_get_type.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_next_res = _libraries['libarsdkctrl.so'].arsdk_media_next_res
arsdk_media_next_res.restype = POINTER_T(struct_arsdk_media_res)
arsdk_media_next_res.argtypes = [POINTER_T(struct_arsdk_media), POINTER_T(struct_arsdk_media_res)]
arsdk_media_get_res_count = _libraries['libarsdkctrl.so'].arsdk_media_get_res_count
arsdk_media_get_res_count.restype = size_t
arsdk_media_get_res_count.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_ref = _libraries['libarsdkctrl.so'].arsdk_media_ref
arsdk_media_ref.restype = None
arsdk_media_ref.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_unref = _libraries['libarsdkctrl.so'].arsdk_media_unref
arsdk_media_unref.restype = None
arsdk_media_unref.argtypes = [POINTER_T(struct_arsdk_media)]
arsdk_media_res_get_type = _libraries['libarsdkctrl.so'].arsdk_media_res_get_type
arsdk_media_res_get_type.restype = arsdk_media_res_type
arsdk_media_res_get_type.argtypes = [POINTER_T(struct_arsdk_media_res)]
arsdk_media_res_get_fmt = _libraries['libarsdkctrl.so'].arsdk_media_res_get_fmt
arsdk_media_res_get_fmt.restype = arsdk_media_res_format
arsdk_media_res_get_fmt.argtypes = [POINTER_T(struct_arsdk_media_res)]
arsdk_media_res_get_uri = _libraries['libarsdkctrl.so'].arsdk_media_res_get_uri
arsdk_media_res_get_uri.restype = POINTER_T(ctypes.c_char)
arsdk_media_res_get_uri.argtypes = [POINTER_T(struct_arsdk_media_res)]
arsdk_media_res_get_size = _libraries['libarsdkctrl.so'].arsdk_media_res_get_size
arsdk_media_res_get_size.restype = size_t
arsdk_media_res_get_size.argtypes = [POINTER_T(struct_arsdk_media_res)]
arsdk_media_res_get_name = _libraries['libarsdkctrl.so'].arsdk_media_res_get_name
arsdk_media_res_get_name.restype = POINTER_T(ctypes.c_char)
arsdk_media_res_get_name.argtypes = [POINTER_T(struct_arsdk_media_res)]
class struct_arsdk_updater_transport(Structure):
    pass

class struct_arsdk_updater_req_upload(Structure):
    pass


# values for enumeration 'arsdk_updater_req_status'
arsdk_updater_req_status__enumvalues = {
    0: 'ARSDK_UPDATER_REQ_STATUS_OK',
    1: 'ARSDK_UPDATER_REQ_STATUS_CANCELED',
    2: 'ARSDK_UPDATER_REQ_STATUS_FAILED',
    3: 'ARSDK_UPDATER_REQ_STATUS_ABORTED',
}
ARSDK_UPDATER_REQ_STATUS_OK = 0
ARSDK_UPDATER_REQ_STATUS_CANCELED = 1
ARSDK_UPDATER_REQ_STATUS_FAILED = 2
ARSDK_UPDATER_REQ_STATUS_ABORTED = 3
arsdk_updater_req_status = ctypes.c_uint32 # enum
class struct_arsdk_updater_req_upload_cbs(Structure):
    pass

struct_arsdk_updater_req_upload_cbs._pack_ = True # source:False
struct_arsdk_updater_req_upload_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_updater_itf), POINTER_T(struct_arsdk_updater_req_upload), ctypes.c_float, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_updater_itf), POINTER_T(struct_arsdk_updater_req_upload), arsdk_updater_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_updater_itf_create_req_upload = _libraries['libarsdkctrl.so'].arsdk_updater_itf_create_req_upload
arsdk_updater_itf_create_req_upload.restype = ctypes.c_int32
arsdk_updater_itf_create_req_upload.argtypes = [POINTER_T(struct_arsdk_updater_itf), POINTER_T(ctypes.c_char), arsdk_device_type, POINTER_T(struct_arsdk_updater_req_upload_cbs), POINTER_T(POINTER_T(struct_arsdk_updater_req_upload))]
arsdk_updater_req_upload_cancel = _libraries['libarsdkctrl.so'].arsdk_updater_req_upload_cancel
arsdk_updater_req_upload_cancel.restype = ctypes.c_int32
arsdk_updater_req_upload_cancel.argtypes = [POINTER_T(struct_arsdk_updater_req_upload)]
arsdk_updater_req_upload_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_updater_req_upload_get_dev_type
arsdk_updater_req_upload_get_dev_type.restype = arsdk_device_type
arsdk_updater_req_upload_get_dev_type.argtypes = [POINTER_T(struct_arsdk_updater_req_upload)]
arsdk_updater_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_updater_itf_cancel_all
arsdk_updater_itf_cancel_all.restype = ctypes.c_int32
arsdk_updater_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_updater_itf)]
arsdk_updater_appid_to_devtype = _libraries['libarsdkctrl.so'].arsdk_updater_appid_to_devtype
arsdk_updater_appid_to_devtype.restype = arsdk_device_type
arsdk_updater_appid_to_devtype.argtypes = [uint32_t]
class struct_arsdk_blackbox_listener(Structure):
    pass

class struct_arsdk_blackbox_rc_piloting_info(Structure):
    pass

struct_arsdk_blackbox_rc_piloting_info._pack_ = True # source:False
struct_arsdk_blackbox_rc_piloting_info._fields_ = [
    ('pitch', ctypes.c_byte),
    ('roll', ctypes.c_byte),
    ('yaw', ctypes.c_byte),
    ('gaz', ctypes.c_byte),
    ('source', ctypes.c_byte),
]

class struct_arsdk_blackbox_listener_cbs(Structure):
    pass

struct_arsdk_blackbox_listener_cbs._pack_ = True # source:False
struct_arsdk_blackbox_listener_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('rc_button_action', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_blackbox_itf), POINTER_T(struct_arsdk_blackbox_listener), ctypes.c_int32, POINTER_T(None))),
    ('rc_piloting_info', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_blackbox_itf), POINTER_T(struct_arsdk_blackbox_listener), POINTER_T(struct_arsdk_blackbox_rc_piloting_info), POINTER_T(None))),
    ('unregister', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_blackbox_itf), POINTER_T(struct_arsdk_blackbox_listener), POINTER_T(None))),
]

arsdk_blackbox_itf_create_listener = _libraries['libarsdkctrl.so'].arsdk_blackbox_itf_create_listener
arsdk_blackbox_itf_create_listener.restype = ctypes.c_int32
arsdk_blackbox_itf_create_listener.argtypes = [POINTER_T(struct_arsdk_blackbox_itf), POINTER_T(struct_arsdk_blackbox_listener_cbs), POINTER_T(POINTER_T(struct_arsdk_blackbox_listener))]
arsdk_blackbox_listener_unregister = _libraries['libarsdkctrl.so'].arsdk_blackbox_listener_unregister
arsdk_blackbox_listener_unregister.restype = ctypes.c_int32
arsdk_blackbox_listener_unregister.argtypes = [POINTER_T(struct_arsdk_blackbox_listener)]
class struct_arsdk_crashml_req(Structure):
    pass


# values for enumeration 'arsdk_crashml_type'
arsdk_crashml_type__enumvalues = {
    1: 'ARSDK_CRASHML_TYPE_DIR',
    2: 'ARSDK_CRASHML_TYPE_TARGZ',
}
ARSDK_CRASHML_TYPE_DIR = 1
ARSDK_CRASHML_TYPE_TARGZ = 2
arsdk_crashml_type = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_crashml_req_status'
arsdk_crashml_req_status__enumvalues = {
    0: 'ARSDK_CRASHML_REQ_STATUS_OK',
    1: 'ARSDK_CRASHML_REQ_STATUS_CANCELED',
    2: 'ARSDK_CRASHML_REQ_STATUS_FAILED',
    3: 'ARSDK_CRASHML_REQ_STATUS_ABORTED',
}
ARSDK_CRASHML_REQ_STATUS_OK = 0
ARSDK_CRASHML_REQ_STATUS_CANCELED = 1
ARSDK_CRASHML_REQ_STATUS_FAILED = 2
ARSDK_CRASHML_REQ_STATUS_ABORTED = 3
arsdk_crashml_req_status = ctypes.c_uint32 # enum
class struct_arsdk_crashml_req_cbs(Structure):
    pass

struct_arsdk_crashml_req_cbs._pack_ = True # source:False
struct_arsdk_crashml_req_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_crashml_itf), POINTER_T(struct_arsdk_crashml_req), POINTER_T(ctypes.c_char), ctypes.c_int32, ctypes.c_int32, arsdk_crashml_req_status, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_crashml_itf), POINTER_T(struct_arsdk_crashml_req), arsdk_crashml_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_crashml_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_crashml_itf_cancel_all
arsdk_crashml_itf_cancel_all.restype = ctypes.c_int32
arsdk_crashml_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_crashml_itf)]
arsdk_crashml_itf_create_req = _libraries['libarsdkctrl.so'].arsdk_crashml_itf_create_req
arsdk_crashml_itf_create_req.restype = ctypes.c_int32
arsdk_crashml_itf_create_req.argtypes = [POINTER_T(struct_arsdk_crashml_itf), POINTER_T(ctypes.c_char), arsdk_device_type, POINTER_T(struct_arsdk_crashml_req_cbs), uint32_t, POINTER_T(POINTER_T(struct_arsdk_crashml_req))]
arsdk_crashml_req_cancel = _libraries['libarsdkctrl.so'].arsdk_crashml_req_cancel
arsdk_crashml_req_cancel.restype = ctypes.c_int32
arsdk_crashml_req_cancel.argtypes = [POINTER_T(struct_arsdk_crashml_req)]
arsdk_crashml_req_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_crashml_req_get_dev_type
arsdk_crashml_req_get_dev_type.restype = arsdk_device_type
arsdk_crashml_req_get_dev_type.argtypes = [POINTER_T(struct_arsdk_crashml_req)]
class struct_arsdk_pud_req(Structure):
    pass


# values for enumeration 'arsdk_pud_req_status'
arsdk_pud_req_status__enumvalues = {
    0: 'ARSDK_PUD_REQ_STATUS_OK',
    1: 'ARSDK_PUD_REQ_STATUS_CANCELED',
    2: 'ARSDK_PUD_REQ_STATUS_FAILED',
    3: 'ARSDK_PUD_REQ_STATUS_ABORTED',
}
ARSDK_PUD_REQ_STATUS_OK = 0
ARSDK_PUD_REQ_STATUS_CANCELED = 1
ARSDK_PUD_REQ_STATUS_FAILED = 2
ARSDK_PUD_REQ_STATUS_ABORTED = 3
arsdk_pud_req_status = ctypes.c_uint32 # enum
class struct_arsdk_pud_req_cbs(Structure):
    pass

struct_arsdk_pud_req_cbs._pack_ = True # source:False
struct_arsdk_pud_req_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_pud_itf), POINTER_T(struct_arsdk_pud_req), POINTER_T(ctypes.c_char), ctypes.c_int32, ctypes.c_int32, arsdk_pud_req_status, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_pud_itf), POINTER_T(struct_arsdk_pud_req), arsdk_pud_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_pud_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_pud_itf_cancel_all
arsdk_pud_itf_cancel_all.restype = ctypes.c_int32
arsdk_pud_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_pud_itf)]
arsdk_pud_itf_create_req = _libraries['libarsdkctrl.so'].arsdk_pud_itf_create_req
arsdk_pud_itf_create_req.restype = ctypes.c_int32
arsdk_pud_itf_create_req.argtypes = [POINTER_T(struct_arsdk_pud_itf), POINTER_T(ctypes.c_char), arsdk_device_type, POINTER_T(struct_arsdk_pud_req_cbs), POINTER_T(POINTER_T(struct_arsdk_pud_req))]
arsdk_pud_req_cancel = _libraries['libarsdkctrl.so'].arsdk_pud_req_cancel
arsdk_pud_req_cancel.restype = ctypes.c_int32
arsdk_pud_req_cancel.argtypes = [POINTER_T(struct_arsdk_pud_req)]
arsdk_pud_req_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_pud_req_get_dev_type
arsdk_pud_req_get_dev_type.restype = arsdk_device_type
arsdk_pud_req_get_dev_type.argtypes = [POINTER_T(struct_arsdk_pud_req)]
class struct_arsdk_ephemeris_req_upload(Structure):
    pass


# values for enumeration 'arsdk_ephemeris_req_status'
arsdk_ephemeris_req_status__enumvalues = {
    0: 'ARSDK_EPHEMERIS_REQ_STATUS_OK',
    1: 'ARSDK_EPHEMERIS_REQ_STATUS_CANCELED',
    2: 'ARSDK_EPHEMERIS_REQ_STATUS_FAILED',
    3: 'ARSDK_EPHEMERIS_REQ_STATUS_ABORTED',
}
ARSDK_EPHEMERIS_REQ_STATUS_OK = 0
ARSDK_EPHEMERIS_REQ_STATUS_CANCELED = 1
ARSDK_EPHEMERIS_REQ_STATUS_FAILED = 2
ARSDK_EPHEMERIS_REQ_STATUS_ABORTED = 3
arsdk_ephemeris_req_status = ctypes.c_uint32 # enum
class struct_arsdk_ephemeris_req_upload_cbs(Structure):
    pass

struct_arsdk_ephemeris_req_upload_cbs._pack_ = True # source:False
struct_arsdk_ephemeris_req_upload_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('progress', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ephemeris_itf), POINTER_T(struct_arsdk_ephemeris_req_upload), ctypes.c_float, POINTER_T(None))),
    ('complete', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_ephemeris_itf), POINTER_T(struct_arsdk_ephemeris_req_upload), arsdk_ephemeris_req_status, ctypes.c_int32, POINTER_T(None))),
]

arsdk_ephemeris_itf_create_req_upload = _libraries['libarsdkctrl.so'].arsdk_ephemeris_itf_create_req_upload
arsdk_ephemeris_itf_create_req_upload.restype = ctypes.c_int32
arsdk_ephemeris_itf_create_req_upload.argtypes = [POINTER_T(struct_arsdk_ephemeris_itf), POINTER_T(ctypes.c_char), arsdk_device_type, POINTER_T(struct_arsdk_ephemeris_req_upload_cbs), POINTER_T(POINTER_T(struct_arsdk_ephemeris_req_upload))]
arsdk_ephemeris_req_upload_cancel = _libraries['libarsdkctrl.so'].arsdk_ephemeris_req_upload_cancel
arsdk_ephemeris_req_upload_cancel.restype = ctypes.c_int32
arsdk_ephemeris_req_upload_cancel.argtypes = [POINTER_T(struct_arsdk_ephemeris_req_upload)]
arsdk_ephemeris_req_upload_get_dev_type = _libraries['libarsdkctrl.so'].arsdk_ephemeris_req_upload_get_dev_type
arsdk_ephemeris_req_upload_get_dev_type.restype = arsdk_device_type
arsdk_ephemeris_req_upload_get_dev_type.argtypes = [POINTER_T(struct_arsdk_ephemeris_req_upload)]
arsdk_ephemeris_req_upload_get_file_path = _libraries['libarsdkctrl.so'].arsdk_ephemeris_req_upload_get_file_path
arsdk_ephemeris_req_upload_get_file_path.restype = POINTER_T(ctypes.c_char)
arsdk_ephemeris_req_upload_get_file_path.argtypes = [POINTER_T(struct_arsdk_ephemeris_req_upload)]
arsdk_ephemeris_itf_cancel_all = _libraries['libarsdkctrl.so'].arsdk_ephemeris_itf_cancel_all
arsdk_ephemeris_itf_cancel_all.restype = ctypes.c_int32
arsdk_ephemeris_itf_cancel_all.argtypes = [POINTER_T(struct_arsdk_ephemeris_itf)]

# values for enumeration 'arsdk_device_state'
arsdk_device_state__enumvalues = {
    0: 'ARSDK_DEVICE_STATE_IDLE',
    1: 'ARSDK_DEVICE_STATE_CONNECTING',
    2: 'ARSDK_DEVICE_STATE_CONNECTED',
    3: 'ARSDK_DEVICE_STATE_REMOVING',
}
ARSDK_DEVICE_STATE_IDLE = 0
ARSDK_DEVICE_STATE_CONNECTING = 1
ARSDK_DEVICE_STATE_CONNECTED = 2
ARSDK_DEVICE_STATE_REMOVING = 3
arsdk_device_state = ctypes.c_uint32 # enum

# values for enumeration 'arsdk_device_api'
arsdk_device_api__enumvalues = {
    0: 'ARSDK_DEVICE_API_UNKNOWN',
    1: 'ARSDK_DEVICE_API_FULL',
    2: 'ARSDK_DEVICE_API_UPDATE_ONLY',
}
ARSDK_DEVICE_API_UNKNOWN = 0
ARSDK_DEVICE_API_FULL = 1
ARSDK_DEVICE_API_UPDATE_ONLY = 2
arsdk_device_api = ctypes.c_uint32 # enum
class struct_arsdk_device_info(Structure):
    pass

struct_arsdk_device_info._pack_ = True # source:False
struct_arsdk_device_info._fields_ = [
    ('backend_type', arsdk_backend_type),
    ('proto_v', ctypes.c_uint32),
    ('api', arsdk_device_api),
    ('state', arsdk_device_state),
    ('name', POINTER_T(ctypes.c_char)),
    ('type', arsdk_device_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('addr', POINTER_T(ctypes.c_char)),
    ('port', ctypes.c_uint16),
    ('PADDING_1', ctypes.c_ubyte * 6),
    ('id', POINTER_T(ctypes.c_char)),
    ('json', POINTER_T(ctypes.c_char)),
]

class struct_arsdk_device_conn_cfg(Structure):
    pass

struct_arsdk_device_conn_cfg._pack_ = True # source:False
struct_arsdk_device_conn_cfg._fields_ = [
    ('ctrl_name', POINTER_T(ctypes.c_char)),
    ('ctrl_type', POINTER_T(ctypes.c_char)),
    ('device_id', POINTER_T(ctypes.c_char)),
    ('json', POINTER_T(ctypes.c_char)),
]

class struct_arsdk_device_conn_cbs(Structure):
    pass

struct_arsdk_device_conn_cbs._pack_ = True # source:False
struct_arsdk_device_conn_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('connecting', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_info), POINTER_T(None))),
    ('connected', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_info), POINTER_T(None))),
    ('disconnected', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_info), POINTER_T(None))),
    ('canceled', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_info), arsdk_conn_cancel_reason, POINTER_T(None))),
    ('link_status', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_info), arsdk_link_status, POINTER_T(None))),
]

arsdk_device_state_str = _libraries['libarsdkctrl.so'].arsdk_device_state_str
arsdk_device_state_str.restype = POINTER_T(ctypes.c_char)
arsdk_device_state_str.argtypes = [arsdk_device_state]
arsdk_device_get_handle = _libraries['libarsdkctrl.so'].arsdk_device_get_handle
arsdk_device_get_handle.restype = uint16_t
arsdk_device_get_handle.argtypes = [POINTER_T(struct_arsdk_device)]
arsdk_device_get_info = _libraries['libarsdkctrl.so'].arsdk_device_get_info
arsdk_device_get_info.restype = ctypes.c_int32
arsdk_device_get_info.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_device_info))]
arsdk_device_get_backend = _libraries['libarsdkctrl.so'].arsdk_device_get_backend
arsdk_device_get_backend.restype = POINTER_T(struct_arsdkctrl_backend)
arsdk_device_get_backend.argtypes = [POINTER_T(struct_arsdk_device)]
arsdk_device_connect = _libraries['libarsdkctrl.so'].arsdk_device_connect
arsdk_device_connect.restype = ctypes.c_int32
arsdk_device_connect.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_device_conn_cfg), POINTER_T(struct_arsdk_device_conn_cbs), POINTER_T(struct_pomp_loop)]
arsdk_device_disconnect = _libraries['libarsdkctrl.so'].arsdk_device_disconnect
arsdk_device_disconnect.restype = ctypes.c_int32
arsdk_device_disconnect.argtypes = [POINTER_T(struct_arsdk_device)]
arsdk_device_create_cmd_itf = _libraries['libarsdkctrl.so'].arsdk_device_create_cmd_itf
arsdk_device_create_cmd_itf.restype = ctypes.c_int32
arsdk_device_create_cmd_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(struct_arsdk_cmd_itf_cbs), POINTER_T(POINTER_T(struct_arsdk_cmd_itf))]
arsdk_device_get_cmd_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_cmd_itf
arsdk_device_get_cmd_itf.restype = POINTER_T(struct_arsdk_cmd_itf)
arsdk_device_get_cmd_itf.argtypes = [POINTER_T(struct_arsdk_device)]
arsdk_device_get_ftp_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_ftp_itf
arsdk_device_get_ftp_itf.restype = ctypes.c_int32
arsdk_device_get_ftp_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_ftp_itf))]
arsdk_device_get_media_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_media_itf
arsdk_device_get_media_itf.restype = ctypes.c_int32
arsdk_device_get_media_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_media_itf))]
arsdk_device_get_updater_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_updater_itf
arsdk_device_get_updater_itf.restype = ctypes.c_int32
arsdk_device_get_updater_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_updater_itf))]
arsdk_device_get_blackbox_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_blackbox_itf
arsdk_device_get_blackbox_itf.restype = ctypes.c_int32
arsdk_device_get_blackbox_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_blackbox_itf))]
arsdk_device_get_crashml_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_crashml_itf
arsdk_device_get_crashml_itf.restype = ctypes.c_int32
arsdk_device_get_crashml_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_crashml_itf))]
arsdk_device_get_flight_log_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_flight_log_itf
arsdk_device_get_flight_log_itf.restype = ctypes.c_int32
arsdk_device_get_flight_log_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_flight_log_itf))]
arsdk_device_get_pud_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_pud_itf
arsdk_device_get_pud_itf.restype = ctypes.c_int32
arsdk_device_get_pud_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_pud_itf))]
arsdk_device_get_ephemeris_itf = _libraries['libarsdkctrl.so'].arsdk_device_get_ephemeris_itf
arsdk_device_get_ephemeris_itf.restype = ctypes.c_int32
arsdk_device_get_ephemeris_itf.argtypes = [POINTER_T(struct_arsdk_device), POINTER_T(POINTER_T(struct_arsdk_ephemeris_itf))]
class struct_arsdk_device_tcp_proxy_cbs(Structure):
    pass

struct_arsdk_device_tcp_proxy_cbs._pack_ = True # source:False
struct_arsdk_device_tcp_proxy_cbs._fields_ = [
    ('userdata', POINTER_T(None)),
    ('open', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device_tcp_proxy), ctypes.c_uint16, POINTER_T(None))),
    ('close', ctypes.CFUNCTYPE(None, POINTER_T(struct_arsdk_device_tcp_proxy), POINTER_T(None))),
]

arsdk_device_create_tcp_proxy = _libraries['libarsdkctrl.so'].arsdk_device_create_tcp_proxy
arsdk_device_create_tcp_proxy.restype = ctypes.c_int32
arsdk_device_create_tcp_proxy.argtypes = [POINTER_T(struct_arsdk_device), arsdk_device_type, uint16_t, POINTER_T(struct_arsdk_device_tcp_proxy_cbs), POINTER_T(POINTER_T(struct_arsdk_device_tcp_proxy))]
arsdk_device_destroy_tcp_proxy = _libraries['libarsdkctrl.so'].arsdk_device_destroy_tcp_proxy
arsdk_device_destroy_tcp_proxy.restype = ctypes.c_int32
arsdk_device_destroy_tcp_proxy.argtypes = [POINTER_T(struct_arsdk_device_tcp_proxy)]
arsdk_device_tcp_proxy_get_addr = _libraries['libarsdkctrl.so'].arsdk_device_tcp_proxy_get_addr
arsdk_device_tcp_proxy_get_addr.restype = POINTER_T(ctypes.c_char)
arsdk_device_tcp_proxy_get_addr.argtypes = [POINTER_T(struct_arsdk_device_tcp_proxy)]
arsdk_device_tcp_proxy_get_port = _libraries['libarsdkctrl.so'].arsdk_device_tcp_proxy_get_port
arsdk_device_tcp_proxy_get_port.restype = ctypes.c_int32
arsdk_device_tcp_proxy_get_port.argtypes = [POINTER_T(struct_arsdk_device_tcp_proxy)]
_ARSDK_DISCOVERY_INTERNAL_H_ = True # macro
class struct_arsdk_discovery_device_info(Structure):
    pass

struct_arsdk_discovery_device_info._pack_ = True # source:False
struct_arsdk_discovery_device_info._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('type', arsdk_device_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('addr', POINTER_T(ctypes.c_char)),
    ('port', ctypes.c_uint16),
    ('PADDING_1', ctypes.c_ubyte * 6),
    ('id', POINTER_T(ctypes.c_char)),
    ('proto_v', ctypes.c_uint32),
    ('api', arsdk_device_api),
]

arsdk_discovery_new = _libraries['libarsdkctrl.so'].arsdk_discovery_new
arsdk_discovery_new.restype = ctypes.c_int32
arsdk_discovery_new.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(struct_arsdkctrl_backend), POINTER_T(struct_arsdk_ctrl), POINTER_T(POINTER_T(struct_arsdk_discovery))]
arsdk_discovery_destroy = _libraries['libarsdkctrl.so'].arsdk_discovery_destroy
arsdk_discovery_destroy.restype = ctypes.c_int32
arsdk_discovery_destroy.argtypes = [POINTER_T(struct_arsdk_discovery)]
arsdk_discovery_start = _libraries['libarsdkctrl.so'].arsdk_discovery_start
arsdk_discovery_start.restype = ctypes.c_int32
arsdk_discovery_start.argtypes = [POINTER_T(struct_arsdk_discovery)]
arsdk_discovery_stop = _libraries['libarsdkctrl.so'].arsdk_discovery_stop
arsdk_discovery_stop.restype = ctypes.c_int32
arsdk_discovery_stop.argtypes = [POINTER_T(struct_arsdk_discovery)]
arsdk_discovery_add_device = _libraries['libarsdkctrl.so'].arsdk_discovery_add_device
arsdk_discovery_add_device.restype = ctypes.c_int32
arsdk_discovery_add_device.argtypes = [POINTER_T(struct_arsdk_discovery), POINTER_T(struct_arsdk_discovery_device_info)]
arsdk_discovery_remove_device = _libraries['libarsdkctrl.so'].arsdk_discovery_remove_device
arsdk_discovery_remove_device.restype = ctypes.c_int32
arsdk_discovery_remove_device.argtypes = [POINTER_T(struct_arsdk_discovery), POINTER_T(struct_arsdk_discovery_device_info)]
_MBUF_MEM_GENERIC_H_ = True # macro
mbuf_mem_generic_cookie = (ctypes.c_uint64).in_dll(_libraries['libmedia-buffers-memory-generic.so'], 'mbuf_mem_generic_cookie')
mbuf_mem_generic_wrap_cookie = (ctypes.c_uint64).in_dll(_libraries['libmedia-buffers-memory-generic.so'], 'mbuf_mem_generic_wrap_cookie')
mbuf_mem_generic_impl = (POINTER_T(struct_mbuf_mem_implem)).in_dll(_libraries['libmedia-buffers-memory-generic.so'], 'mbuf_mem_generic_impl')
mbuf_mem_generic_wrap_release_t = ctypes.CFUNCTYPE(None, POINTER_T(None), ctypes.c_uint64, POINTER_T(None))
mbuf_mem_generic_new = _libraries['libmedia-buffers-memory-generic.so'].mbuf_mem_generic_new
mbuf_mem_generic_new.restype = ctypes.c_int32
mbuf_mem_generic_new.argtypes = [size_t, POINTER_T(POINTER_T(struct_mbuf_mem))]
mbuf_mem_generic_wrap = _libraries['libmedia-buffers-memory-generic.so'].mbuf_mem_generic_wrap
mbuf_mem_generic_wrap.restype = ctypes.c_int32
mbuf_mem_generic_wrap.argtypes = [POINTER_T(None), size_t, mbuf_mem_generic_wrap_release_t, POINTER_T(None), POINTER_T(POINTER_T(struct_mbuf_mem))]
mbuf_mem_generic_releaser_free = _libraries['libmedia-buffers-memory-generic.so'].mbuf_mem_generic_releaser_free
mbuf_mem_generic_releaser_free.restype = None
mbuf_mem_generic_releaser_free.argtypes = [POINTER_T(None), size_t, POINTER_T(None)]
_LIBMP4_H_ = True # macro
# MP4_API = (None) # macro
MP4_META_KEY_FRIENDLY_NAME = ("com.apple.quicktime.artist") # macro
MP4_UDTA_KEY_FRIENDLY_NAME = ("\251ART") # macro
MP4_META_KEY_TITLE = ("com.apple.quicktime.title") # macro
MP4_UDTA_KEY_TITLE = ("\251nam") # macro
MP4_META_KEY_COMMENT = ("com.apple.quicktime.comment") # macro
MP4_UDTA_KEY_COMMENT = ("\251cmt") # macro
MP4_META_KEY_COPYRIGHT = ("com.apple.quicktime.copyright") # macro
MP4_UDTA_KEY_COPYRIGHT = ("\251cpy") # macro
MP4_META_KEY_MEDIA_DATE = ("com.apple.quicktime.creationdate") # macro
MP4_UDTA_KEY_MEDIA_DATE = ("\251day") # macro
MP4_META_KEY_LOCATION = ("com.apple.quicktime.location.ISO6709") # macro
MP4_UDTA_KEY_LOCATION = ("\251xyz") # macro
MP4_META_KEY_MAKER = ("com.apple.quicktime.make") # macro
MP4_UDTA_KEY_MAKER = ("\251mak") # macro
MP4_META_KEY_MODEL = ("com.apple.quicktime.model") # macro
MP4_UDTA_KEY_MODEL = ("\251mod") # macro
MP4_META_KEY_SOFTWARE_VERSION = ("com.apple.quicktime.software") # macro
MP4_UDTA_KEY_SOFTWARE_VERSION = ("\251swr") # macro

# values for enumeration 'mp4_track_type'
mp4_track_type__enumvalues = {
    0: 'MP4_TRACK_TYPE_UNKNOWN',
    1: 'MP4_TRACK_TYPE_VIDEO',
    2: 'MP4_TRACK_TYPE_AUDIO',
    3: 'MP4_TRACK_TYPE_HINT',
    4: 'MP4_TRACK_TYPE_METADATA',
    5: 'MP4_TRACK_TYPE_TEXT',
    6: 'MP4_TRACK_TYPE_CHAPTERS',
}
MP4_TRACK_TYPE_UNKNOWN = 0
MP4_TRACK_TYPE_VIDEO = 1
MP4_TRACK_TYPE_AUDIO = 2
MP4_TRACK_TYPE_HINT = 3
MP4_TRACK_TYPE_METADATA = 4
MP4_TRACK_TYPE_TEXT = 5
MP4_TRACK_TYPE_CHAPTERS = 6
mp4_track_type = ctypes.c_uint32 # enum

# values for enumeration 'mp4_video_codec'
mp4_video_codec__enumvalues = {
    0: 'MP4_VIDEO_CODEC_UNKNOWN',
    1: 'MP4_VIDEO_CODEC_AVC',
    2: 'MP4_VIDEO_CODEC_HEVC',
}
MP4_VIDEO_CODEC_UNKNOWN = 0
MP4_VIDEO_CODEC_AVC = 1
MP4_VIDEO_CODEC_HEVC = 2
mp4_video_codec = ctypes.c_uint32 # enum

# values for enumeration 'mp4_audio_codec'
mp4_audio_codec__enumvalues = {
    0: 'MP4_AUDIO_CODEC_UNKNOWN',
    1: 'MP4_AUDIO_CODEC_AAC_LC',
}
MP4_AUDIO_CODEC_UNKNOWN = 0
MP4_AUDIO_CODEC_AAC_LC = 1
mp4_audio_codec = ctypes.c_uint32 # enum

# values for enumeration 'mp4_metadata_cover_type'
mp4_metadata_cover_type__enumvalues = {
    0: 'MP4_METADATA_COVER_TYPE_UNKNOWN',
    1: 'MP4_METADATA_COVER_TYPE_JPEG',
    2: 'MP4_METADATA_COVER_TYPE_PNG',
    3: 'MP4_METADATA_COVER_TYPE_BMP',
}
MP4_METADATA_COVER_TYPE_UNKNOWN = 0
MP4_METADATA_COVER_TYPE_JPEG = 1
MP4_METADATA_COVER_TYPE_PNG = 2
MP4_METADATA_COVER_TYPE_BMP = 3
mp4_metadata_cover_type = ctypes.c_uint32 # enum

# values for enumeration 'mp4_seek_method'
mp4_seek_method__enumvalues = {
    0: 'MP4_SEEK_METHOD_PREVIOUS',
    1: 'MP4_SEEK_METHOD_PREVIOUS_SYNC',
    2: 'MP4_SEEK_METHOD_NEXT_SYNC',
    3: 'MP4_SEEK_METHOD_NEAREST_SYNC',
}
MP4_SEEK_METHOD_PREVIOUS = 0
MP4_SEEK_METHOD_PREVIOUS_SYNC = 1
MP4_SEEK_METHOD_NEXT_SYNC = 2
MP4_SEEK_METHOD_NEAREST_SYNC = 3
mp4_seek_method = ctypes.c_uint32 # enum
class struct_mp4_media_info(Structure):
    pass

struct_mp4_media_info._pack_ = True # source:False
struct_mp4_media_info._fields_ = [
    ('duration', ctypes.c_uint64),
    ('creation_time', ctypes.c_uint64),
    ('modification_time', ctypes.c_uint64),
    ('track_count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_mp4_track_info(Structure):
    pass

struct_mp4_track_info._pack_ = True # source:False
struct_mp4_track_info._fields_ = [
    ('id', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('name', POINTER_T(ctypes.c_char)),
    ('enabled', ctypes.c_int32),
    ('in_movie', ctypes.c_int32),
    ('in_preview', ctypes.c_int32),
    ('type', mp4_track_type),
    ('timescale', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('duration', ctypes.c_uint64),
    ('creation_time', ctypes.c_uint64),
    ('modification_time', ctypes.c_uint64),
    ('sample_count', ctypes.c_uint32),
    ('sample_max_size', ctypes.c_uint32),
    ('sample_offsets', POINTER_T(ctypes.c_uint64)),
    ('sample_sizes', POINTER_T(ctypes.c_uint32)),
    ('video_codec', mp4_video_codec),
    ('video_width', ctypes.c_uint32),
    ('video_height', ctypes.c_uint32),
    ('audio_codec', mp4_audio_codec),
    ('audio_channel_count', ctypes.c_uint32),
    ('audio_sample_size', ctypes.c_uint32),
    ('audio_sample_rate', ctypes.c_float),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('content_encoding', POINTER_T(ctypes.c_char)),
    ('mime_format', POINTER_T(ctypes.c_char)),
    ('has_metadata', ctypes.c_int32),
    ('PADDING_3', ctypes.c_ubyte * 4),
    ('metadata_content_encoding', POINTER_T(ctypes.c_char)),
    ('metadata_mime_format', POINTER_T(ctypes.c_char)),
]

class struct_mp4_hvcc_info(Structure):
    pass

struct_mp4_hvcc_info._pack_ = True # source:False
struct_mp4_hvcc_info._fields_ = [
    ('general_profile_space', ctypes.c_ubyte),
    ('general_tier_flag', ctypes.c_ubyte),
    ('general_profile_idc', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
    ('general_profile_compatibility_flags', ctypes.c_uint32),
    ('general_constraints_indicator_flags', ctypes.c_uint64),
    ('general_level_idc', ctypes.c_ubyte),
    ('PADDING_1', ctypes.c_ubyte),
    ('min_spatial_segmentation_idc', ctypes.c_uint16),
    ('parallelism_type', ctypes.c_ubyte),
    ('chroma_format', ctypes.c_ubyte),
    ('bit_depth_luma', ctypes.c_ubyte),
    ('bit_depth_chroma', ctypes.c_ubyte),
    ('avg_framerate', ctypes.c_uint16),
    ('constant_framerate', ctypes.c_ubyte),
    ('num_temporal_layers', ctypes.c_ubyte),
    ('temporal_id_nested', ctypes.c_ubyte),
    ('length_size', ctypes.c_ubyte),
    ('PADDING_2', ctypes.c_ubyte * 2),
]

class union_mp4_video_decoder_config_0_0_0(Union):
    pass

union_mp4_video_decoder_config_0_0_0._pack_ = True # source:False
union_mp4_video_decoder_config_0_0_0._fields_ = [
    ('sps', POINTER_T(ctypes.c_ubyte)),
    ('c_sps', POINTER_T(ctypes.c_ubyte)),
]

class union_mp4_video_decoder_config_0_0_1(Union):
    pass

union_mp4_video_decoder_config_0_0_1._pack_ = True # source:False
union_mp4_video_decoder_config_0_0_1._fields_ = [
    ('pps', POINTER_T(ctypes.c_ubyte)),
    ('c_pps', POINTER_T(ctypes.c_ubyte)),
]

class struct_mp4_video_decoder_config_0_0(Structure):
    pass

struct_mp4_video_decoder_config_0_0._pack_ = True # source:False
struct_mp4_video_decoder_config_0_0._fields_ = [
    ('mp4_video_decoder_config_0_0_0', union_mp4_video_decoder_config_0_0_0),
    ('sps_size', ctypes.c_uint64),
    ('mp4_video_decoder_config_0_0_1', union_mp4_video_decoder_config_0_0_1),
    ('pps_size', ctypes.c_uint64),
]

class union_mp4_video_decoder_config_0_1_0(Union):
    pass

union_mp4_video_decoder_config_0_1_0._pack_ = True # source:False
union_mp4_video_decoder_config_0_1_0._fields_ = [
    ('vps', POINTER_T(ctypes.c_ubyte)),
    ('c_vps', POINTER_T(ctypes.c_ubyte)),
]

class union_mp4_video_decoder_config_0_1_1(Union):
    pass

union_mp4_video_decoder_config_0_1_1._pack_ = True # source:False
union_mp4_video_decoder_config_0_1_1._fields_ = [
    ('sps', POINTER_T(ctypes.c_ubyte)),
    ('c_sps', POINTER_T(ctypes.c_ubyte)),
]

class union_mp4_video_decoder_config_0_1_2(Union):
    pass

union_mp4_video_decoder_config_0_1_2._pack_ = True # source:False
union_mp4_video_decoder_config_0_1_2._fields_ = [
    ('pps', POINTER_T(ctypes.c_ubyte)),
    ('c_pps', POINTER_T(ctypes.c_ubyte)),
]

class struct_mp4_video_decoder_config_0_1(Structure):
    pass

struct_mp4_video_decoder_config_0_1._pack_ = True # source:False
struct_mp4_video_decoder_config_0_1._fields_ = [
    ('hvcc_info', struct_mp4_hvcc_info),
    ('mp4_video_decoder_config_0_1_0', union_mp4_video_decoder_config_0_1_0),
    ('vps_size', ctypes.c_uint64),
    ('mp4_video_decoder_config_0_1_1', union_mp4_video_decoder_config_0_1_1),
    ('sps_size', ctypes.c_uint64),
    ('mp4_video_decoder_config_0_1_2', union_mp4_video_decoder_config_0_1_2),
    ('pps_size', ctypes.c_uint64),
]

class union_mp4_video_decoder_config_0(Union):
    _pack_ = True # source:False
    _fields_ = [
        ('avc', struct_mp4_video_decoder_config_0_0),
        ('hevc', struct_mp4_video_decoder_config_0_1),
    ]

class struct_mp4_video_decoder_config(Structure):
    pass

struct_mp4_video_decoder_config._pack_ = True # source:False
struct_mp4_video_decoder_config._fields_ = [
    ('codec', mp4_video_codec),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('mp4_video_decoder_config_0', union_mp4_video_decoder_config_0),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
]

class struct_mp4_track_sample(Structure):
    pass

struct_mp4_track_sample._pack_ = True # source:False
struct_mp4_track_sample._fields_ = [
    ('size', ctypes.c_uint32),
    ('metadata_size', ctypes.c_uint32),
    ('silent', ctypes.c_int32),
    ('sync', ctypes.c_int32),
    ('dts', ctypes.c_uint64),
    ('next_dts', ctypes.c_uint64),
    ('prev_sync_dts', ctypes.c_uint64),
    ('next_sync_dts', ctypes.c_uint64),
]

class struct_mp4_mux_track_params(Structure):
    pass

struct_mp4_mux_track_params._pack_ = True # source:False
struct_mp4_mux_track_params._fields_ = [
    ('type', mp4_track_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('name', POINTER_T(ctypes.c_char)),
    ('enabled', ctypes.c_int32),
    ('in_movie', ctypes.c_int32),
    ('in_preview', ctypes.c_int32),
    ('timescale', ctypes.c_uint32),
    ('creation_time', ctypes.c_uint64),
    ('modification_time', ctypes.c_uint64),
]

class struct_mp4_mux_sample(Structure):
    pass

struct_mp4_mux_sample._pack_ = True # source:False
struct_mp4_mux_sample._fields_ = [
    ('buffer', POINTER_T(ctypes.c_ubyte)),
    ('len', ctypes.c_uint64),
    ('sync', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('dts', ctypes.c_int64),
]

class struct_mp4_mux_scattered_sample(Structure):
    pass

struct_mp4_mux_scattered_sample._pack_ = True # source:False
struct_mp4_mux_scattered_sample._fields_ = [
    ('buffers', POINTER_T(POINTER_T(ctypes.c_ubyte))),
    ('len', POINTER_T(ctypes.c_uint64)),
    ('nbuffers', ctypes.c_int32),
    ('sync', ctypes.c_int32),
    ('dts', ctypes.c_int64),
]

class struct_mp4_demux(Structure):
    pass

mp4_demux_open = _libraries['libmp4.so'].mp4_demux_open
mp4_demux_open.restype = ctypes.c_int32
mp4_demux_open.argtypes = [POINTER_T(ctypes.c_char), POINTER_T(POINTER_T(struct_mp4_demux))]
mp4_demux_close = _libraries['libmp4.so'].mp4_demux_close
mp4_demux_close.restype = ctypes.c_int32
mp4_demux_close.argtypes = [POINTER_T(struct_mp4_demux)]
mp4_demux_get_media_info = _libraries['libmp4.so'].mp4_demux_get_media_info
mp4_demux_get_media_info.restype = ctypes.c_int32
mp4_demux_get_media_info.argtypes = [POINTER_T(struct_mp4_demux), POINTER_T(struct_mp4_media_info)]
mp4_demux_get_track_count = _libraries['libmp4.so'].mp4_demux_get_track_count
mp4_demux_get_track_count.restype = ctypes.c_int32
mp4_demux_get_track_count.argtypes = [POINTER_T(struct_mp4_demux)]
mp4_demux_get_track_info = _libraries['libmp4.so'].mp4_demux_get_track_info
mp4_demux_get_track_info.restype = ctypes.c_int32
mp4_demux_get_track_info.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(struct_mp4_track_info)]
mp4_demux_get_track_video_decoder_config = _libraries['libmp4.so'].mp4_demux_get_track_video_decoder_config
mp4_demux_get_track_video_decoder_config.restype = ctypes.c_int32
mp4_demux_get_track_video_decoder_config.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(struct_mp4_video_decoder_config)]
mp4_demux_get_track_audio_specific_config = _libraries['libmp4.so'].mp4_demux_get_track_audio_specific_config
mp4_demux_get_track_audio_specific_config.restype = ctypes.c_int32
mp4_demux_get_track_audio_specific_config.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(POINTER_T(ctypes.c_ubyte)), POINTER_T(ctypes.c_uint32)]
mp4_demux_get_track_sample = _libraries['libmp4.so'].mp4_demux_get_track_sample
mp4_demux_get_track_sample.restype = ctypes.c_int32
mp4_demux_get_track_sample.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, ctypes.c_int32, POINTER_T(ctypes.c_ubyte), ctypes.c_uint32, POINTER_T(ctypes.c_ubyte), ctypes.c_uint32, POINTER_T(struct_mp4_track_sample)]
mp4_demux_get_track_prev_sample_time = _libraries['libmp4.so'].mp4_demux_get_track_prev_sample_time
mp4_demux_get_track_prev_sample_time.restype = ctypes.c_int32
mp4_demux_get_track_prev_sample_time.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(ctypes.c_uint64)]
mp4_demux_get_track_next_sample_time = _libraries['libmp4.so'].mp4_demux_get_track_next_sample_time
mp4_demux_get_track_next_sample_time.restype = ctypes.c_int32
mp4_demux_get_track_next_sample_time.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(ctypes.c_uint64)]
mp4_demux_get_track_prev_sample_time_before = _libraries['libmp4.so'].mp4_demux_get_track_prev_sample_time_before
mp4_demux_get_track_prev_sample_time_before.restype = ctypes.c_int32
mp4_demux_get_track_prev_sample_time_before.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, uint64_t, ctypes.c_int32, POINTER_T(ctypes.c_uint64)]
mp4_demux_get_track_next_sample_time_after = _libraries['libmp4.so'].mp4_demux_get_track_next_sample_time_after
mp4_demux_get_track_next_sample_time_after.restype = ctypes.c_int32
mp4_demux_get_track_next_sample_time_after.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, uint64_t, ctypes.c_int32, POINTER_T(ctypes.c_uint64)]
mp4_demux_seek = _libraries['libmp4.so'].mp4_demux_seek
mp4_demux_seek.restype = ctypes.c_int32
mp4_demux_seek.argtypes = [POINTER_T(struct_mp4_demux), uint64_t, mp4_seek_method]
mp4_demux_seek_to_track_prev_sample = _libraries['libmp4.so'].mp4_demux_seek_to_track_prev_sample
mp4_demux_seek_to_track_prev_sample.restype = ctypes.c_int32
mp4_demux_seek_to_track_prev_sample.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32]
mp4_demux_seek_to_track_next_sample = _libraries['libmp4.so'].mp4_demux_seek_to_track_next_sample
mp4_demux_seek_to_track_next_sample.restype = ctypes.c_int32
mp4_demux_seek_to_track_next_sample.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32]
mp4_demux_get_chapters = _libraries['libmp4.so'].mp4_demux_get_chapters
mp4_demux_get_chapters.restype = ctypes.c_int32
mp4_demux_get_chapters.argtypes = [POINTER_T(struct_mp4_demux), POINTER_T(ctypes.c_uint32), POINTER_T(POINTER_T(ctypes.c_uint64)), POINTER_T(POINTER_T(POINTER_T(ctypes.c_char)))]
mp4_demux_get_metadata_strings = _libraries['libmp4.so'].mp4_demux_get_metadata_strings
mp4_demux_get_metadata_strings.restype = ctypes.c_int32
mp4_demux_get_metadata_strings.argtypes = [POINTER_T(struct_mp4_demux), POINTER_T(ctypes.c_uint32), POINTER_T(POINTER_T(POINTER_T(ctypes.c_char))), POINTER_T(POINTER_T(POINTER_T(ctypes.c_char)))]
mp4_demux_get_track_metadata_strings = _libraries['libmp4.so'].mp4_demux_get_track_metadata_strings
mp4_demux_get_track_metadata_strings.restype = ctypes.c_int32
mp4_demux_get_track_metadata_strings.argtypes = [POINTER_T(struct_mp4_demux), ctypes.c_uint32, POINTER_T(ctypes.c_uint32), POINTER_T(POINTER_T(POINTER_T(ctypes.c_char))), POINTER_T(POINTER_T(POINTER_T(ctypes.c_char)))]
mp4_demux_get_metadata_cover = _libraries['libmp4.so'].mp4_demux_get_metadata_cover
mp4_demux_get_metadata_cover.restype = ctypes.c_int32
mp4_demux_get_metadata_cover.argtypes = [POINTER_T(struct_mp4_demux), POINTER_T(ctypes.c_ubyte), ctypes.c_uint32, POINTER_T(ctypes.c_uint32), POINTER_T(mp4_metadata_cover_type)]
class struct_mp4_mux(Structure):
    pass

mp4_mux_open = _libraries['libmp4.so'].mp4_mux_open
mp4_mux_open.restype = ctypes.c_int32
mp4_mux_open.argtypes = [POINTER_T(ctypes.c_char), uint32_t, uint64_t, uint64_t, POINTER_T(POINTER_T(struct_mp4_mux))]
mp4_mux_open2 = _libraries['libmp4.so'].mp4_mux_open2
mp4_mux_open2.restype = ctypes.c_int32
mp4_mux_open2.argtypes = [POINTER_T(ctypes.c_char), uint32_t, uint64_t, uint64_t, uint32_t, POINTER_T(POINTER_T(struct_mp4_mux))]
mp4_mux_sync = _libraries['libmp4.so'].mp4_mux_sync
mp4_mux_sync.restype = ctypes.c_int32
mp4_mux_sync.argtypes = [POINTER_T(struct_mp4_mux)]
mp4_mux_close = _libraries['libmp4.so'].mp4_mux_close
mp4_mux_close.restype = ctypes.c_int32
mp4_mux_close.argtypes = [POINTER_T(struct_mp4_mux)]
mp4_mux_add_track = _libraries['libmp4.so'].mp4_mux_add_track
mp4_mux_add_track.restype = ctypes.c_int32
mp4_mux_add_track.argtypes = [POINTER_T(struct_mp4_mux), POINTER_T(struct_mp4_mux_track_params)]
mp4_mux_add_ref_to_track = _libraries['libmp4.so'].mp4_mux_add_ref_to_track
mp4_mux_add_ref_to_track.restype = ctypes.c_int32
mp4_mux_add_ref_to_track.argtypes = [POINTER_T(struct_mp4_mux), uint32_t, uint32_t]
mp4_mux_track_set_video_decoder_config = _libraries['libmp4.so'].mp4_mux_track_set_video_decoder_config
mp4_mux_track_set_video_decoder_config.restype = ctypes.c_int32
mp4_mux_track_set_video_decoder_config.argtypes = [POINTER_T(struct_mp4_mux), ctypes.c_int32, POINTER_T(struct_mp4_video_decoder_config)]
mp4_mux_track_set_audio_specific_config = _libraries['libmp4.so'].mp4_mux_track_set_audio_specific_config
mp4_mux_track_set_audio_specific_config.restype = ctypes.c_int32
mp4_mux_track_set_audio_specific_config.argtypes = [POINTER_T(struct_mp4_mux), ctypes.c_int32, POINTER_T(ctypes.c_ubyte), size_t, uint32_t, uint32_t, ctypes.c_float]
mp4_mux_track_set_metadata_mime_type = _libraries['libmp4.so'].mp4_mux_track_set_metadata_mime_type
mp4_mux_track_set_metadata_mime_type.restype = ctypes.c_int32
mp4_mux_track_set_metadata_mime_type.argtypes = [POINTER_T(struct_mp4_mux), ctypes.c_int32, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char)]
mp4_mux_add_file_metadata = _libraries['libmp4.so'].mp4_mux_add_file_metadata
mp4_mux_add_file_metadata.restype = ctypes.c_int32
mp4_mux_add_file_metadata.argtypes = [POINTER_T(struct_mp4_mux), POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char)]
mp4_mux_add_track_metadata = _libraries['libmp4.so'].mp4_mux_add_track_metadata
mp4_mux_add_track_metadata.restype = ctypes.c_int32
mp4_mux_add_track_metadata.argtypes = [POINTER_T(struct_mp4_mux), uint32_t, POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_char)]
mp4_mux_set_file_cover = _libraries['libmp4.so'].mp4_mux_set_file_cover
mp4_mux_set_file_cover.restype = ctypes.c_int32
mp4_mux_set_file_cover.argtypes = [POINTER_T(struct_mp4_mux), mp4_metadata_cover_type, POINTER_T(ctypes.c_ubyte), size_t]
mp4_mux_track_add_sample = _libraries['libmp4.so'].mp4_mux_track_add_sample
mp4_mux_track_add_sample.restype = ctypes.c_int32
mp4_mux_track_add_sample.argtypes = [POINTER_T(struct_mp4_mux), ctypes.c_int32, POINTER_T(struct_mp4_mux_sample)]
mp4_mux_track_add_scattered_sample = _libraries['libmp4.so'].mp4_mux_track_add_scattered_sample
mp4_mux_track_add_scattered_sample.restype = ctypes.c_int32
mp4_mux_track_add_scattered_sample.argtypes = [POINTER_T(struct_mp4_mux), ctypes.c_int32, POINTER_T(struct_mp4_mux_scattered_sample)]
mp4_mux_dump = _libraries['libmp4.so'].mp4_mux_dump
mp4_mux_dump.restype = None
mp4_mux_dump.argtypes = [POINTER_T(struct_mp4_mux)]
mp4_generate_avc_decoder_config = _libraries['libmp4.so'].mp4_generate_avc_decoder_config
mp4_generate_avc_decoder_config.restype = ctypes.c_int32
mp4_generate_avc_decoder_config.argtypes = [POINTER_T(ctypes.c_ubyte), ctypes.c_uint32, POINTER_T(ctypes.c_ubyte), ctypes.c_uint32, POINTER_T(ctypes.c_ubyte), POINTER_T(ctypes.c_uint32)]
mp4_track_type_str = _libraries['libmp4.so'].mp4_track_type_str
mp4_track_type_str.restype = POINTER_T(ctypes.c_char)
mp4_track_type_str.argtypes = [mp4_track_type]
mp4_video_codec_str = _libraries['libmp4.so'].mp4_video_codec_str
mp4_video_codec_str.restype = POINTER_T(ctypes.c_char)
mp4_video_codec_str.argtypes = [mp4_video_codec]
mp4_audio_codec_str = _libraries['libmp4.so'].mp4_audio_codec_str
mp4_audio_codec_str.restype = POINTER_T(ctypes.c_char)
mp4_audio_codec_str.argtypes = [mp4_audio_codec]
mp4_metadata_cover_type_str = _libraries['libmp4.so'].mp4_metadata_cover_type_str
mp4_metadata_cover_type_str.restype = POINTER_T(ctypes.c_char)
mp4_metadata_cover_type_str.argtypes = [mp4_metadata_cover_type]
mp4_usec_to_sample_time = _libraries['FIXME_STUB'].mp4_usec_to_sample_time
mp4_usec_to_sample_time.restype = uint64_t
mp4_usec_to_sample_time.argtypes = [uint64_t, uint32_t]
mp4_sample_time_to_usec = _libraries['FIXME_STUB'].mp4_sample_time_to_usec
mp4_sample_time_to_usec.restype = uint64_t
mp4_sample_time_to_usec.argtypes = [uint64_t, uint32_t]
mp4_convert_timescale = _libraries['FIXME_STUB'].mp4_convert_timescale
mp4_convert_timescale.restype = uint64_t
mp4_convert_timescale.argtypes = [uint64_t, uint32_t, uint32_t]
_LIBMUX_H_ = True # macro
# MUX_API = (None) # macro
MUX_PROTOCOL_VERSION = (2) # macro
MUX_FLAG_FD_NOT_POLLABLE = (1 << 0) # macro
class struct_mux_queue(Structure):
    pass

class struct_mux_ip_proxy(Structure):
    pass


# values for enumeration 'mux_channel_event'
mux_channel_event__enumvalues = {
    0: 'MUX_CHANNEL_RESET',
    1: 'MUX_CHANNEL_DATA',
}
MUX_CHANNEL_RESET = 0
MUX_CHANNEL_DATA = 1
mux_channel_event = ctypes.c_uint32 # enum

# values for enumeration 'mux_ip_proxy_transport'
mux_ip_proxy_transport__enumvalues = {
    0: 'MUX_IP_PROXY_TRANSPORT_TCP',
    1: 'MUX_IP_PROXY_TRANSPORT_UDP',
}
MUX_IP_PROXY_TRANSPORT_TCP = 0
MUX_IP_PROXY_TRANSPORT_UDP = 1
mux_ip_proxy_transport = ctypes.c_uint32 # enum

# values for enumeration 'mux_ip_proxy_application'
mux_ip_proxy_application__enumvalues = {
    0: 'MUX_IP_PROXY_APPLICATION_NONE',
    1: 'MUX_IP_PROXY_APPLICATION_FTP',
}
MUX_IP_PROXY_APPLICATION_NONE = 0
MUX_IP_PROXY_APPLICATION_FTP = 1
mux_ip_proxy_application = ctypes.c_uint32 # enum
class struct_mux_ip_proxy_protocol(Structure):
    _pack_ = True # source:False
    _fields_ = [
        ('transport', mux_ip_proxy_transport),
        ('application', mux_ip_proxy_application),
    ]

class struct_mux_ip_proxy_info(Structure):
    pass

struct_mux_ip_proxy_info._pack_ = True # source:False
struct_mux_ip_proxy_info._fields_ = [
    ('protocol', struct_mux_ip_proxy_protocol),
    ('remote_host', POINTER_T(ctypes.c_char)),
    ('remote_port', ctypes.c_uint16),
    ('udp_redirect_port', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

mux_channel_cb_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ctx), ctypes.c_uint32, mux_channel_event, POINTER_T(struct_pomp_buffer), POINTER_T(None))
class struct_mux_ip_proxy_cbs(Structure):
    pass

struct_mux_ip_proxy_cbs._pack_ = True # source:False
struct_mux_ip_proxy_cbs._fields_ = [
    ('open', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ip_proxy), ctypes.c_uint16, POINTER_T(None))),
    ('close', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ip_proxy), POINTER_T(None))),
    ('remote_update', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ip_proxy), POINTER_T(None))),
    ('resolution_failed', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ip_proxy), ctypes.c_int32, POINTER_T(None))),
    ('userdata', POINTER_T(None)),
]

class struct_mux_ops(Structure):
    pass

struct_mux_ops._pack_ = True # source:False
struct_mux_ops._fields_ = [
    ('tx', ctypes.CFUNCTYPE(ctypes.c_int32, POINTER_T(struct_mux_ctx), POINTER_T(struct_pomp_buffer), POINTER_T(None))),
    ('chan_cb', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ctx), ctypes.c_uint32, mux_channel_event, POINTER_T(struct_pomp_buffer), POINTER_T(None))),
    ('fdeof', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ctx), POINTER_T(None))),
    ('release', ctypes.CFUNCTYPE(None, POINTER_T(struct_mux_ctx), POINTER_T(None))),
    ('resolve', ctypes.CFUNCTYPE(ctypes.c_int32, POINTER_T(struct_mux_ctx), POINTER_T(ctypes.c_char), POINTER_T(ctypes.c_uint32), POINTER_T(None))),
    ('userdata', POINTER_T(None)),
]

mux_new = _libraries['libmux.so'].mux_new
mux_new.restype = POINTER_T(struct_mux_ctx)
mux_new.argtypes = [ctypes.c_int32, POINTER_T(struct_pomp_loop), POINTER_T(struct_mux_ops), uint32_t]
mux_ref = _libraries['libmux.so'].mux_ref
mux_ref.restype = None
mux_ref.argtypes = [POINTER_T(struct_mux_ctx)]
mux_unref = _libraries['libmux.so'].mux_unref
mux_unref.restype = None
mux_unref.argtypes = [POINTER_T(struct_mux_ctx)]
mux_get_loop = _libraries['libmux.so'].mux_get_loop
mux_get_loop.restype = POINTER_T(struct_pomp_loop)
mux_get_loop.argtypes = [POINTER_T(struct_mux_ctx)]
mux_get_remote_version = _libraries['libmux.so'].mux_get_remote_version
mux_get_remote_version.restype = uint32_t
mux_get_remote_version.argtypes = [POINTER_T(struct_mux_ctx)]
mux_stop = _libraries['libmux.so'].mux_stop
mux_stop.restype = ctypes.c_int32
mux_stop.argtypes = [POINTER_T(struct_mux_ctx)]
mux_run = _libraries['libmux.so'].mux_run
mux_run.restype = ctypes.c_int32
mux_run.argtypes = [POINTER_T(struct_mux_ctx)]
mux_reset = _libraries['libmux.so'].mux_reset
mux_reset.restype = ctypes.c_int32
mux_reset.argtypes = [POINTER_T(struct_mux_ctx)]
mux_encode = _libraries['libmux.so'].mux_encode
mux_encode.restype = ctypes.c_int32
mux_encode.argtypes = [POINTER_T(struct_mux_ctx), uint32_t, POINTER_T(struct_pomp_buffer)]
mux_decode = _libraries['libmux.so'].mux_decode
mux_decode.restype = ctypes.c_int32
mux_decode.argtypes = [POINTER_T(struct_mux_ctx), POINTER_T(struct_pomp_buffer)]
mux_resolve = _libraries['libmux.so'].mux_resolve
mux_resolve.restype = ctypes.c_int32
mux_resolve.argtypes = [POINTER_T(struct_mux_ctx), POINTER_T(ctypes.c_char), uint32_t]
mux_channel_open = _libraries['libmux.so'].mux_channel_open
mux_channel_open.restype = ctypes.c_int32
mux_channel_open.argtypes = [POINTER_T(struct_mux_ctx), uint32_t, mux_channel_cb_t, POINTER_T(None)]
mux_channel_close = _libraries['libmux.so'].mux_channel_close
mux_channel_close.restype = ctypes.c_int32
mux_channel_close.argtypes = [POINTER_T(struct_mux_ctx), uint32_t]
mux_channel_alloc_queue = _libraries['libmux.so'].mux_channel_alloc_queue
mux_channel_alloc_queue.restype = ctypes.c_int32
mux_channel_alloc_queue.argtypes = [POINTER_T(struct_mux_ctx), uint32_t, uint32_t, POINTER_T(POINTER_T(struct_mux_queue))]
mux_queue_get_buf = _libraries['libmux.so'].mux_queue_get_buf
mux_queue_get_buf.restype = ctypes.c_int32
mux_queue_get_buf.argtypes = [POINTER_T(struct_mux_queue), POINTER_T(POINTER_T(struct_pomp_buffer))]
mux_queue_try_get_buf = _libraries['libmux.so'].mux_queue_try_get_buf
mux_queue_try_get_buf.restype = ctypes.c_int32
mux_queue_try_get_buf.argtypes = [POINTER_T(struct_mux_queue), POINTER_T(POINTER_T(struct_pomp_buffer))]
class struct_timespec(Structure):
    pass

struct_timespec._pack_ = True # source:False
struct_timespec._fields_ = [
    ('tv_sec', ctypes.c_int64),
    ('tv_nsec', ctypes.c_int64),
]

mux_queue_timed_get_buf = _libraries['libmux.so'].mux_queue_timed_get_buf
mux_queue_timed_get_buf.restype = ctypes.c_int32
mux_queue_timed_get_buf.argtypes = [POINTER_T(struct_mux_queue), POINTER_T(POINTER_T(struct_pomp_buffer)), POINTER_T(struct_timespec)]
mux_ip_proxy_new = _libraries['libmux.so'].mux_ip_proxy_new
mux_ip_proxy_new.restype = ctypes.c_int32
mux_ip_proxy_new.argtypes = [POINTER_T(struct_mux_ctx), POINTER_T(struct_mux_ip_proxy_info), POINTER_T(struct_mux_ip_proxy_cbs), ctypes.c_int32, POINTER_T(POINTER_T(struct_mux_ip_proxy))]
mux_ip_proxy_destroy = _libraries['libmux.so'].mux_ip_proxy_destroy
mux_ip_proxy_destroy.restype = ctypes.c_int32
mux_ip_proxy_destroy.argtypes = [POINTER_T(struct_mux_ip_proxy)]
mux_ip_proxy_get_local_info = _libraries['libmux.so'].mux_ip_proxy_get_local_info
mux_ip_proxy_get_local_info.restype = ctypes.c_int32
mux_ip_proxy_get_local_info.argtypes = [POINTER_T(struct_mux_ip_proxy), POINTER_T(struct_mux_ip_proxy_protocol), POINTER_T(ctypes.c_uint16)]
mux_ip_proxy_get_peerport = _libraries['libmux.so'].mux_ip_proxy_get_peerport
mux_ip_proxy_get_peerport.restype = uint16_t
mux_ip_proxy_get_peerport.argtypes = [POINTER_T(struct_mux_ip_proxy)]
mux_ip_proxy_set_udp_remote = _libraries['libmux.so'].mux_ip_proxy_set_udp_remote
mux_ip_proxy_set_udp_remote.restype = ctypes.c_int32
mux_ip_proxy_set_udp_remote.argtypes = [POINTER_T(struct_mux_ip_proxy), POINTER_T(ctypes.c_char), uint16_t, ctypes.c_int32]
mux_ip_proxy_set_udp_redirect_port = _libraries['libmux.so'].mux_ip_proxy_set_udp_redirect_port
mux_ip_proxy_set_udp_redirect_port.restype = ctypes.c_int32
mux_ip_proxy_set_udp_redirect_port.argtypes = [POINTER_T(struct_mux_ip_proxy), uint16_t]
mux_ip_proxy_get_remote_host = _libraries['libmux.so'].mux_ip_proxy_get_remote_host
mux_ip_proxy_get_remote_host.restype = POINTER_T(ctypes.c_char)
mux_ip_proxy_get_remote_host.argtypes = [POINTER_T(struct_mux_ip_proxy)]
mux_ip_proxy_get_remote_port = _libraries['libmux.so'].mux_ip_proxy_get_remote_port
mux_ip_proxy_get_remote_port.restype = uint16_t
mux_ip_proxy_get_remote_port.argtypes = [POINTER_T(struct_mux_ip_proxy)]
mux_ip_proxy_get_remote_addr = _libraries['libmux.so'].mux_ip_proxy_get_remote_addr
mux_ip_proxy_get_remote_addr.restype = uint32_t
mux_ip_proxy_get_remote_addr.argtypes = [POINTER_T(struct_mux_ip_proxy)]
_LIBMUX_ARSDK_H_ = True # macro
MUX_ARSDK_CHANNEL_ID_TRANSPORT = (1) # macro
MUX_ARSDK_CHANNEL_ID_DISCOVERY = (2) # macro
MUX_ARSDK_CHANNEL_ID_BACKEND = (3) # macro
MUX_ARSDK_CHANNEL_ID_STREAM_DATA = (4) # macro
MUX_ARSDK_CHANNEL_ID_STREAM_CONTROL = (5) # macro
MUX_ARSDK_CHANNEL_ID_RTP = (6) # macro
MUX_ARSDK_MSG_ID_DISCOVER = (1) # macro
MUX_ARSDK_MSG_ID_DEVICE_ADDED = (2) # macro
MUX_ARSDK_MSG_FMT_ENC_DEVICE_ADDED = ("%s%u%s") # macro
MUX_ARSDK_MSG_FMT_DEC_DEVICE_ADDED = ("%ms%u%ms") # macro
MUX_ARSDK_MSG_ID_DEVICE_REMOVED = (3) # macro
MUX_ARSDK_MSG_FMT_ENC_DEVICE_REMOVED = ("%s%u%s") # macro
MUX_ARSDK_MSG_FMT_DEC_DEVICE_REMOVED = ("%ms%u%ms") # macro
MUX_ARSDK_MSG_ID_CONN_REQ = (1) # macro
MUX_ARSDK_MSG_FMT_ENC_CONN_REQ = ("%s%s%s%s") # macro
MUX_ARSDK_MSG_FMT_DEC_CONN_REQ = ("%ms%ms%ms%ms") # macro
MUX_ARSDK_MSG_ID_CONN_RESP = (2) # macro
MUX_ARSDK_MSG_FMT_ENC_CONN_RESP = ("%d%s") # macro
MUX_ARSDK_MSG_FMT_DEC_CONN_RESP = ("%d%ms") # macro
MUX_ARSDK_MSG_ID_RTP_DATA = (1) # macro
MUX_ARSDK_MSG_FMT_ENC_RTP_DATA = ("%hu%p%u") # macro
MUX_ARSDK_MSG_FMT_DEC_RTP_DATA = ("%hu%p%u") # macro
MUX_ARSDK_MSG_ID_RTCP_DATA = (2) # macro
MUX_ARSDK_MSG_FMT_ENC_RTCP_DATA = ("%hu%p%u") # macro
MUX_ARSDK_MSG_FMT_DEC_RTCP_DATA = ("%hu%p%u") # macro

__all__ = \
    ['ARSDKCTRL_BACKEND_MUX_PROTO_MAX',
    'ARSDKCTRL_BACKEND_MUX_PROTO_MIN',
    'ARSDKCTRL_BACKEND_NET_PROTO_MAX',
    'ARSDKCTRL_BACKEND_NET_PROTO_MIN', 'ARSDK_ARG_TYPE_BINARY',
    'ARSDK_ARG_TYPE_DOUBLE', 'ARSDK_ARG_TYPE_ENUM',
    'ARSDK_ARG_TYPE_FLOAT', 'ARSDK_ARG_TYPE_I16',
    'ARSDK_ARG_TYPE_I32', 'ARSDK_ARG_TYPE_I64', 'ARSDK_ARG_TYPE_I8',
    'ARSDK_ARG_TYPE_STRING', 'ARSDK_ARG_TYPE_U16',
    'ARSDK_ARG_TYPE_U32', 'ARSDK_ARG_TYPE_U64', 'ARSDK_ARG_TYPE_U8',
    'ARSDK_BACKEND_MUX_PROTO_MAX', 'ARSDK_BACKEND_MUX_PROTO_MIN',
    'ARSDK_BACKEND_NET_PROTO_MAX', 'ARSDK_BACKEND_NET_PROTO_MIN',
    'ARSDK_BACKEND_TYPE_BLE', 'ARSDK_BACKEND_TYPE_MUX',
    'ARSDK_BACKEND_TYPE_NET', 'ARSDK_BACKEND_TYPE_UNKNOWN',
    'ARSDK_CMD_BUFFER_TYPE_ACK', 'ARSDK_CMD_BUFFER_TYPE_HIGH_PRIO',
    'ARSDK_CMD_BUFFER_TYPE_INVALID', 'ARSDK_CMD_BUFFER_TYPE_NON_ACK',
    'ARSDK_CMD_DIR_RX', 'ARSDK_CMD_DIR_TX',
    'ARSDK_CMD_ITF_SEND_STATUS_ACK_RECEIVED',
    'ARSDK_CMD_ITF_SEND_STATUS_CANCELED',
    'ARSDK_CMD_ITF_SEND_STATUS_SENT',
    'ARSDK_CMD_ITF_SEND_STATUS_TIMEOUT',
    'ARSDK_CMD_LIST_TYPE_LIST_ITEM', 'ARSDK_CMD_LIST_TYPE_MAP_ITEM',
    'ARSDK_CMD_LIST_TYPE_NONE', 'ARSDK_CMD_TIMEOUT_POLICY_FLUSH',
    'ARSDK_CMD_TIMEOUT_POLICY_POP', 'ARSDK_CMD_TIMEOUT_POLICY_RETRY',
    'ARSDK_CONN_CANCEL_REASON_LOCAL',
    'ARSDK_CONN_CANCEL_REASON_REJECTED',
    'ARSDK_CONN_CANCEL_REASON_REMOTE',
    'ARSDK_CRASHML_REQ_STATUS_ABORTED',
    'ARSDK_CRASHML_REQ_STATUS_CANCELED',
    'ARSDK_CRASHML_REQ_STATUS_FAILED', 'ARSDK_CRASHML_REQ_STATUS_OK',
    'ARSDK_CRASHML_TYPE_DIR', 'ARSDK_CRASHML_TYPE_TARGZ',
    'ARSDK_DEVICE_API_FULL', 'ARSDK_DEVICE_API_UNKNOWN',
    'ARSDK_DEVICE_API_UPDATE_ONLY', 'ARSDK_DEVICE_INVALID_HANDLE',
    'ARSDK_DEVICE_STATE_CONNECTED', 'ARSDK_DEVICE_STATE_CONNECTING',
    'ARSDK_DEVICE_STATE_IDLE', 'ARSDK_DEVICE_STATE_REMOVING',
    'ARSDK_DEVICE_TYPE_ANAFI4K', 'ARSDK_DEVICE_TYPE_ANAFI_2',
    'ARSDK_DEVICE_TYPE_ANAFI_THERMAL', 'ARSDK_DEVICE_TYPE_ANAFI_UA',
    'ARSDK_DEVICE_TYPE_ANAFI_USA', 'ARSDK_DEVICE_TYPE_BEBOP',
    'ARSDK_DEVICE_TYPE_BEBOP_2', 'ARSDK_DEVICE_TYPE_CHIMERA',
    'ARSDK_DEVICE_TYPE_EVINRUDE', 'ARSDK_DEVICE_TYPE_JS',
    'ARSDK_DEVICE_TYPE_JS_EVO_LIGHT', 'ARSDK_DEVICE_TYPE_JS_EVO_RACE',
    'ARSDK_DEVICE_TYPE_PAROS', 'ARSDK_DEVICE_TYPE_POWERUP',
    'ARSDK_DEVICE_TYPE_RS', 'ARSDK_DEVICE_TYPE_RS3',
    'ARSDK_DEVICE_TYPE_RS_EVO_BRICK',
    'ARSDK_DEVICE_TYPE_RS_EVO_HYDROFOIL',
    'ARSDK_DEVICE_TYPE_RS_EVO_LIGHT', 'ARSDK_DEVICE_TYPE_SKYCTRL',
    'ARSDK_DEVICE_TYPE_SKYCTRL_2', 'ARSDK_DEVICE_TYPE_SKYCTRL_2P',
    'ARSDK_DEVICE_TYPE_SKYCTRL_3', 'ARSDK_DEVICE_TYPE_SKYCTRL_4',
    'ARSDK_DEVICE_TYPE_SKYCTRL_NG', 'ARSDK_DEVICE_TYPE_SKYCTRL_UA',
    'ARSDK_DEVICE_TYPE_UNKNOWN', 'ARSDK_DEVICE_TYPE_WINGX',
    'ARSDK_EPHEMERIS_REQ_STATUS_ABORTED',
    'ARSDK_EPHEMERIS_REQ_STATUS_CANCELED',
    'ARSDK_EPHEMERIS_REQ_STATUS_FAILED',
    'ARSDK_EPHEMERIS_REQ_STATUS_OK', 'ARSDK_FTP_FILE_TYPE_DIR',
    'ARSDK_FTP_FILE_TYPE_FILE', 'ARSDK_FTP_FILE_TYPE_LINK',
    'ARSDK_FTP_FILE_TYPE_UNKNOWN', 'ARSDK_FTP_REQ_STATUS_ABORTED',
    'ARSDK_FTP_REQ_STATUS_CANCELED', 'ARSDK_FTP_REQ_STATUS_FAILED',
    'ARSDK_FTP_REQ_STATUS_OK', 'ARSDK_FTP_SRV_TYPE_FLIGHT_PLAN',
    'ARSDK_FTP_SRV_TYPE_MEDIA', 'ARSDK_FTP_SRV_TYPE_UNKNOWN',
    'ARSDK_FTP_SRV_TYPE_UPDATE', 'ARSDK_INVALID_HANDLE',
    'ARSDK_LINK_STATUS_KO', 'ARSDK_LINK_STATUS_OK',
    'ARSDK_MEDIA_REQ_STATUS_ABORTED',
    'ARSDK_MEDIA_REQ_STATUS_CANCELED',
    'ARSDK_MEDIA_REQ_STATUS_FAILED', 'ARSDK_MEDIA_REQ_STATUS_OK',
    'ARSDK_MEDIA_RES_FMT_DNG', 'ARSDK_MEDIA_RES_FMT_JPG',
    'ARSDK_MEDIA_RES_FMT_MP4', 'ARSDK_MEDIA_RES_FMT_UNKNOWN',
    'ARSDK_MEDIA_RES_TYPE_PHOTO', 'ARSDK_MEDIA_RES_TYPE_THUMBNAIL',
    'ARSDK_MEDIA_RES_TYPE_UNKNOWN', 'ARSDK_MEDIA_RES_TYPE_VIDEO',
    'ARSDK_MEDIA_TYPE_ALL', 'ARSDK_MEDIA_TYPE_PHOTO',
    'ARSDK_MEDIA_TYPE_UNKNOWN', 'ARSDK_MEDIA_TYPE_VIDEO',
    'ARSDK_PROTOCOL_VERSION_1', 'ARSDK_PROTOCOL_VERSION_2',
    'ARSDK_PROTOCOL_VERSION_3', 'ARSDK_PUD_REQ_STATUS_ABORTED',
    'ARSDK_PUD_REQ_STATUS_CANCELED', 'ARSDK_PUD_REQ_STATUS_FAILED',
    'ARSDK_PUD_REQ_STATUS_OK', 'ARSDK_SOCKET_KIND_COMMAND',
    'ARSDK_SOCKET_KIND_CONNECTION', 'ARSDK_SOCKET_KIND_DISCOVERY',
    'ARSDK_SOCKET_KIND_FTP', 'ARSDK_SOCKET_KIND_VIDEO',
    'ARSDK_UPDATER_REQ_STATUS_ABORTED',
    'ARSDK_UPDATER_REQ_STATUS_CANCELED',
    'ARSDK_UPDATER_REQ_STATUS_FAILED', 'ARSDK_UPDATER_REQ_STATUS_OK',
    'H264_NALU_TYPE_AUD', 'H264_NALU_TYPE_END_OF_SEQ',
    'H264_NALU_TYPE_END_OF_STREAM', 'H264_NALU_TYPE_FILLER',
    'H264_NALU_TYPE_PPS', 'H264_NALU_TYPE_SEI',
    'H264_NALU_TYPE_SLICE', 'H264_NALU_TYPE_SLICE_DPA',
    'H264_NALU_TYPE_SLICE_DPB', 'H264_NALU_TYPE_SLICE_DPC',
    'H264_NALU_TYPE_SLICE_IDR', 'H264_NALU_TYPE_SPS',
    'H264_NALU_TYPE_UNKNOWN', 'H264_SLICE_TYPE_B',
    'H264_SLICE_TYPE_I', 'H264_SLICE_TYPE_P', 'H264_SLICE_TYPE_SI',
    'H264_SLICE_TYPE_SP', 'H264_SLICE_TYPE_UNKNOWN',
    'H265_NALU_TYPE_AUD_NUT', 'H265_NALU_TYPE_BLA_N_LP',
    'H265_NALU_TYPE_BLA_W_LP', 'H265_NALU_TYPE_BLA_W_RADL',
    'H265_NALU_TYPE_CRA_NUT', 'H265_NALU_TYPE_EOB_NUT',
    'H265_NALU_TYPE_EOS_NUT', 'H265_NALU_TYPE_FD_NUT',
    'H265_NALU_TYPE_IDR_N_LP', 'H265_NALU_TYPE_IDR_W_RADL',
    'H265_NALU_TYPE_PPS_NUT', 'H265_NALU_TYPE_PREFIX_SEI_NUT',
    'H265_NALU_TYPE_RADL_N', 'H265_NALU_TYPE_RADL_R',
    'H265_NALU_TYPE_RASL_N', 'H265_NALU_TYPE_RASL_R',
    'H265_NALU_TYPE_RSV_IRAP_VCL22', 'H265_NALU_TYPE_RSV_IRAP_VCL23',
    'H265_NALU_TYPE_RSV_NVCL41', 'H265_NALU_TYPE_RSV_NVCL42',
    'H265_NALU_TYPE_RSV_NVCL43', 'H265_NALU_TYPE_RSV_NVCL44',
    'H265_NALU_TYPE_RSV_NVCL45', 'H265_NALU_TYPE_RSV_NVCL46',
    'H265_NALU_TYPE_RSV_NVCL47', 'H265_NALU_TYPE_RSV_VCL24',
    'H265_NALU_TYPE_RSV_VCL25', 'H265_NALU_TYPE_RSV_VCL26',
    'H265_NALU_TYPE_RSV_VCL27', 'H265_NALU_TYPE_RSV_VCL28',
    'H265_NALU_TYPE_RSV_VCL29', 'H265_NALU_TYPE_RSV_VCL30',
    'H265_NALU_TYPE_RSV_VCL31', 'H265_NALU_TYPE_RSV_VCL_N10',
    'H265_NALU_TYPE_RSV_VCL_N12', 'H265_NALU_TYPE_RSV_VCL_N14',
    'H265_NALU_TYPE_RSV_VCL_R11', 'H265_NALU_TYPE_RSV_VCL_R13',
    'H265_NALU_TYPE_RSV_VCL_R15', 'H265_NALU_TYPE_SPS_NUT',
    'H265_NALU_TYPE_STSA_N', 'H265_NALU_TYPE_STSA_R',
    'H265_NALU_TYPE_SUFFIX_SEI_NUT', 'H265_NALU_TYPE_TRAIL_N',
    'H265_NALU_TYPE_TRAIL_R', 'H265_NALU_TYPE_TSA_N',
    'H265_NALU_TYPE_TSA_R', 'H265_NALU_TYPE_UNKNOWN',
    'H265_NALU_TYPE_UNSPEC48', 'H265_NALU_TYPE_UNSPEC49',
    'H265_NALU_TYPE_UNSPEC50', 'H265_NALU_TYPE_UNSPEC51',
    'H265_NALU_TYPE_UNSPEC52', 'H265_NALU_TYPE_UNSPEC53',
    'H265_NALU_TYPE_UNSPEC54', 'H265_NALU_TYPE_UNSPEC55',
    'H265_NALU_TYPE_UNSPEC56', 'H265_NALU_TYPE_UNSPEC57',
    'H265_NALU_TYPE_UNSPEC58', 'H265_NALU_TYPE_UNSPEC59',
    'H265_NALU_TYPE_UNSPEC60', 'H265_NALU_TYPE_UNSPEC61',
    'H265_NALU_TYPE_UNSPEC62', 'H265_NALU_TYPE_UNSPEC63',
    'H265_NALU_TYPE_VPS_NUT', 'INT16_MAX', 'INT16_MIN', 'INT16_WIDTH',
    'INT32_MAX', 'INT32_MIN', 'INT32_WIDTH', 'INT64_MAX', 'INT64_MIN',
    'INT64_WIDTH', 'INT8_MAX', 'INT8_MIN', 'INT8_WIDTH', 'INTMAX_MAX',
    'INTMAX_MIN', 'INTMAX_WIDTH', 'INTPTR_MAX', 'INTPTR_MIN',
    'INT_FAST16_MAX', 'INT_FAST16_MIN', 'INT_FAST32_MAX',
    'INT_FAST32_MIN', 'INT_FAST64_MAX', 'INT_FAST64_MIN',
    'INT_FAST64_WIDTH', 'INT_FAST8_MAX', 'INT_FAST8_MIN',
    'INT_FAST8_WIDTH', 'INT_LEAST16_MAX', 'INT_LEAST16_MIN',
    'INT_LEAST16_WIDTH', 'INT_LEAST32_MAX', 'INT_LEAST32_MIN',
    'INT_LEAST32_WIDTH', 'INT_LEAST64_MAX', 'INT_LEAST64_MIN',
    'INT_LEAST64_WIDTH', 'INT_LEAST8_MAX', 'INT_LEAST8_MIN',
    'INT_LEAST8_WIDTH', 'MBUF_ANCILLARY_KEY_USERDATA_SEI',
    'MBUF_POOL_GROW', 'MBUF_POOL_LOW_MEM_GROW', 'MBUF_POOL_NO_GROW',
    'MBUF_POOL_SMART_GROW', 'MP4_AUDIO_CODEC_AAC_LC',
    'MP4_AUDIO_CODEC_UNKNOWN', 'MP4_METADATA_COVER_TYPE_BMP',
    'MP4_METADATA_COVER_TYPE_JPEG', 'MP4_METADATA_COVER_TYPE_PNG',
    'MP4_METADATA_COVER_TYPE_UNKNOWN', 'MP4_META_KEY_COMMENT',
    'MP4_META_KEY_COPYRIGHT', 'MP4_META_KEY_FRIENDLY_NAME',
    'MP4_META_KEY_LOCATION', 'MP4_META_KEY_MAKER',
    'MP4_META_KEY_MEDIA_DATE', 'MP4_META_KEY_MODEL',
    'MP4_META_KEY_SOFTWARE_VERSION', 'MP4_META_KEY_TITLE',
    'MP4_SEEK_METHOD_NEAREST_SYNC', 'MP4_SEEK_METHOD_NEXT_SYNC',
    'MP4_SEEK_METHOD_PREVIOUS', 'MP4_SEEK_METHOD_PREVIOUS_SYNC',
    'MP4_TRACK_TYPE_AUDIO', 'MP4_TRACK_TYPE_CHAPTERS',
    'MP4_TRACK_TYPE_HINT', 'MP4_TRACK_TYPE_METADATA',
    'MP4_TRACK_TYPE_TEXT', 'MP4_TRACK_TYPE_UNKNOWN',
    'MP4_TRACK_TYPE_VIDEO', 'MP4_UDTA_KEY_COMMENT',
    'MP4_UDTA_KEY_COPYRIGHT', 'MP4_UDTA_KEY_FRIENDLY_NAME',
    'MP4_UDTA_KEY_LOCATION', 'MP4_UDTA_KEY_MAKER',
    'MP4_UDTA_KEY_MEDIA_DATE', 'MP4_UDTA_KEY_MODEL',
    'MP4_UDTA_KEY_SOFTWARE_VERSION', 'MP4_UDTA_KEY_TITLE',
    'MP4_VIDEO_CODEC_AVC', 'MP4_VIDEO_CODEC_HEVC',
    'MP4_VIDEO_CODEC_UNKNOWN', 'MUX_ARSDK_CHANNEL_ID_BACKEND',
    'MUX_ARSDK_CHANNEL_ID_DISCOVERY', 'MUX_ARSDK_CHANNEL_ID_RTP',
    'MUX_ARSDK_CHANNEL_ID_STREAM_CONTROL',
    'MUX_ARSDK_CHANNEL_ID_STREAM_DATA',
    'MUX_ARSDK_CHANNEL_ID_TRANSPORT',
    'MUX_ARSDK_MSG_FMT_DEC_CONN_REQ',
    'MUX_ARSDK_MSG_FMT_DEC_CONN_RESP',
    'MUX_ARSDK_MSG_FMT_DEC_DEVICE_ADDED',
    'MUX_ARSDK_MSG_FMT_DEC_DEVICE_REMOVED',
    'MUX_ARSDK_MSG_FMT_DEC_RTCP_DATA',
    'MUX_ARSDK_MSG_FMT_DEC_RTP_DATA',
    'MUX_ARSDK_MSG_FMT_ENC_CONN_REQ',
    'MUX_ARSDK_MSG_FMT_ENC_CONN_RESP',
    'MUX_ARSDK_MSG_FMT_ENC_DEVICE_ADDED',
    'MUX_ARSDK_MSG_FMT_ENC_DEVICE_REMOVED',
    'MUX_ARSDK_MSG_FMT_ENC_RTCP_DATA',
    'MUX_ARSDK_MSG_FMT_ENC_RTP_DATA', 'MUX_ARSDK_MSG_ID_CONN_REQ',
    'MUX_ARSDK_MSG_ID_CONN_RESP', 'MUX_ARSDK_MSG_ID_DEVICE_ADDED',
    'MUX_ARSDK_MSG_ID_DEVICE_REMOVED', 'MUX_ARSDK_MSG_ID_DISCOVER',
    'MUX_ARSDK_MSG_ID_RTCP_DATA', 'MUX_ARSDK_MSG_ID_RTP_DATA',
    'MUX_CHANNEL_DATA', 'MUX_CHANNEL_RESET',
    'MUX_FLAG_FD_NOT_POLLABLE', 'MUX_IP_PROXY_APPLICATION_FTP',
    'MUX_IP_PROXY_APPLICATION_NONE', 'MUX_IP_PROXY_TRANSPORT_TCP',
    'MUX_IP_PROXY_TRANSPORT_UDP', 'MUX_PROTOCOL_VERSION',
    'PDRAW_ANCILLARY_DATA_KEY_VIDEOFRAME', 'PDRAW_API_VAR',
    'PDRAW_HISTOGRAM_CHANNEL_BLUE', 'PDRAW_HISTOGRAM_CHANNEL_GREEN',
    'PDRAW_HISTOGRAM_CHANNEL_LUMA', 'PDRAW_HISTOGRAM_CHANNEL_MAX',
    'PDRAW_HISTOGRAM_CHANNEL_RED', 'PDRAW_HMD_MODEL_COCKPITGLASSES',
    'PDRAW_HMD_MODEL_COCKPITGLASSES_2', 'PDRAW_HMD_MODEL_UNKNOWN',
    'PDRAW_MEDIA_TYPE_UNKNOWN', 'PDRAW_MEDIA_TYPE_VIDEO',
    'PDRAW_PIPELINE_MODE_DECODE_ALL',
    'PDRAW_PIPELINE_MODE_DECODE_NONE', 'PDRAW_PLAYBACK_TYPE_LIVE',
    'PDRAW_PLAYBACK_TYPE_REPLAY', 'PDRAW_PLAYBACK_TYPE_UNKNOWN',
    'PDRAW_PLAY_SPEED_MAX', 'PDRAW_VIDEO_RENDERER_FILL_MODE_CROP',
    'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT',
    'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_CROP',
    'PDRAW_VIDEO_RENDERER_FILL_MODE_FIT_PAD_BLUR_EXTEND',
    'PDRAW_VIDEO_RENDERER_FILL_MODE_MAX',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_ALL',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_EOS',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_PHOTO_TRIGGER',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_RECONFIGURE',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_SOS',
    'PDRAW_VIDEO_RENDERER_TRANSITION_FLAG_TIMEOUT',
    'PDRAW_VIDEO_TYPE_DEFAULT_CAMERA',
    'PDRAW_VIDEO_TYPE_FRONT_CAMERA', 'POMP_EVENT_CONNECTED',
    'POMP_EVENT_DISCONNECTED', 'POMP_EVENT_MSG', 'POMP_FD_EVENT_ERR',
    'POMP_FD_EVENT_HUP', 'POMP_FD_EVENT_IN', 'POMP_FD_EVENT_OUT',
    'POMP_FD_EVENT_PRI', 'POMP_LOOP_IMPL_EPOLL',
    'POMP_LOOP_IMPL_POLL', 'POMP_LOOP_IMPL_WIN32',
    'POMP_SEND_STATUS_ABORTED', 'POMP_SEND_STATUS_ERROR',
    'POMP_SEND_STATUS_OK', 'POMP_SEND_STATUS_QUEUE_EMPTY',
    'POMP_SOCKET_KIND_CLIENT', 'POMP_SOCKET_KIND_DGRAM',
    'POMP_SOCKET_KIND_PEER', 'POMP_SOCKET_KIND_SERVER',
    'POMP_TIMER_IMPL_KQUEUE', 'POMP_TIMER_IMPL_POSIX',
    'POMP_TIMER_IMPL_TIMER_FD', 'POMP_TIMER_IMPL_WIN32',
    'PROTOBUF_C_LABEL_NONE', 'PROTOBUF_C_LABEL_OPTIONAL',
    'PROTOBUF_C_LABEL_REPEATED', 'PROTOBUF_C_LABEL_REQUIRED',
    'PROTOBUF_C_TYPE_BOOL', 'PROTOBUF_C_TYPE_BYTES',
    'PROTOBUF_C_TYPE_DOUBLE', 'PROTOBUF_C_TYPE_ENUM',
    'PROTOBUF_C_TYPE_FIXED32', 'PROTOBUF_C_TYPE_FIXED64',
    'PROTOBUF_C_TYPE_FLOAT', 'PROTOBUF_C_TYPE_INT32',
    'PROTOBUF_C_TYPE_INT64', 'PROTOBUF_C_TYPE_MESSAGE',
    'PROTOBUF_C_TYPE_SFIXED32', 'PROTOBUF_C_TYPE_SFIXED64',
    'PROTOBUF_C_TYPE_SINT32', 'PROTOBUF_C_TYPE_SINT64',
    'PROTOBUF_C_TYPE_STRING', 'PROTOBUF_C_TYPE_UINT32',
    'PROTOBUF_C_TYPE_UINT64', 'PROTOBUF_C_WIRE_TYPE_32BIT',
    'PROTOBUF_C_WIRE_TYPE_64BIT',
    'PROTOBUF_C_WIRE_TYPE_LENGTH_PREFIXED',
    'PROTOBUF_C_WIRE_TYPE_VARINT', 'PTRDIFF_MAX', 'PTRDIFF_MIN',
    'SIG_ATOMIC_MAX', 'SIG_ATOMIC_MIN', 'SIG_ATOMIC_WIDTH',
    'SIZE_MAX', 'UINT16_MAX', 'UINT16_WIDTH', 'UINT32_MAX',
    'UINT32_WIDTH', 'UINT64_MAX', 'UINT64_WIDTH', 'UINT8_MAX',
    'UINT8_WIDTH', 'UINTMAX_MAX', 'UINTMAX_WIDTH', 'UINTPTR_MAX',
    'UINT_FAST16_MAX', 'UINT_FAST32_MAX', 'UINT_FAST64_MAX',
    'UINT_FAST64_WIDTH', 'UINT_FAST8_MAX', 'UINT_FAST8_WIDTH',
    'UINT_LEAST16_MAX', 'UINT_LEAST16_WIDTH', 'UINT_LEAST32_MAX',
    'UINT_LEAST32_WIDTH', 'UINT_LEAST64_MAX', 'UINT_LEAST64_WIDTH',
    'UINT_LEAST8_MAX', 'UINT_LEAST8_WIDTH',
    'VDEF_CODED_DATA_FORMAT_AVCC',
    'VDEF_CODED_DATA_FORMAT_BYTE_STREAM',
    'VDEF_CODED_DATA_FORMAT_HVCC', 'VDEF_CODED_DATA_FORMAT_JFIF',
    'VDEF_CODED_DATA_FORMAT_RAW_NALU',
    'VDEF_CODED_DATA_FORMAT_UNKNOWN', 'VDEF_CODED_FORMAT_TO_STR_FMT',
    'VDEF_CODED_FRAME_TYPE_CODED', 'VDEF_CODED_FRAME_TYPE_I',
    'VDEF_CODED_FRAME_TYPE_IDR', 'VDEF_CODED_FRAME_TYPE_NOT_CODED',
    'VDEF_CODED_FRAME_TYPE_P', 'VDEF_CODED_FRAME_TYPE_P_IR_START',
    'VDEF_CODED_FRAME_TYPE_P_NON_REF',
    'VDEF_CODED_FRAME_TYPE_UNKNOWN', 'VDEF_COLOR_PRIMARIES_BT2020',
    'VDEF_COLOR_PRIMARIES_BT2100', 'VDEF_COLOR_PRIMARIES_BT601_525',
    'VDEF_COLOR_PRIMARIES_BT601_625', 'VDEF_COLOR_PRIMARIES_BT709',
    'VDEF_COLOR_PRIMARIES_DCI_P3', 'VDEF_COLOR_PRIMARIES_DISPLAY_P3',
    'VDEF_COLOR_PRIMARIES_MAX', 'VDEF_COLOR_PRIMARIES_SRGB',
    'VDEF_COLOR_PRIMARIES_UNKNOWN', 'VDEF_DYNAMIC_RANGE_HDR10',
    'VDEF_DYNAMIC_RANGE_HDR8', 'VDEF_DYNAMIC_RANGE_MAX',
    'VDEF_DYNAMIC_RANGE_SDR', 'VDEF_DYNAMIC_RANGE_UNKNOWN',
    'VDEF_ENCODING_AVC', 'VDEF_ENCODING_H264', 'VDEF_ENCODING_H265',
    'VDEF_ENCODING_HEVC', 'VDEF_ENCODING_JPEG', 'VDEF_ENCODING_MJPEG',
    'VDEF_ENCODING_UNKNOWN', 'VDEF_FRAME_FLAG_DATA_ERROR',
    'VDEF_FRAME_FLAG_NONE', 'VDEF_FRAME_FLAG_NOT_MAPPED',
    'VDEF_FRAME_FLAG_NO_CACHE_CLEAN',
    'VDEF_FRAME_FLAG_NO_CACHE_INVALIDATE', 'VDEF_FRAME_FLAG_SILENT',
    'VDEF_FRAME_FLAG_USES_LTR', 'VDEF_FRAME_FLAG_VISUAL_ERROR',
    'VDEF_FRAME_TYPE_CODED', 'VDEF_FRAME_TYPE_RAW',
    'VDEF_FRAME_TYPE_UNKNOWN', 'VDEF_MATRIX_COEFS_BT2020_CST',
    'VDEF_MATRIX_COEFS_BT2020_NON_CST', 'VDEF_MATRIX_COEFS_BT2100',
    'VDEF_MATRIX_COEFS_BT601_525', 'VDEF_MATRIX_COEFS_BT601_625',
    'VDEF_MATRIX_COEFS_BT709', 'VDEF_MATRIX_COEFS_IDENTITY',
    'VDEF_MATRIX_COEFS_MAX', 'VDEF_MATRIX_COEFS_SRGB',
    'VDEF_MATRIX_COEFS_UNKNOWN', 'VDEF_RAW_DATA_LAYOUT_INTERLEAVED',
    'VDEF_RAW_DATA_LAYOUT_OPAQUE', 'VDEF_RAW_DATA_LAYOUT_PACKED',
    'VDEF_RAW_DATA_LAYOUT_PLANAR',
    'VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B',
    'VDEF_RAW_DATA_LAYOUT_PLANAR_R_G_B_A',
    'VDEF_RAW_DATA_LAYOUT_PLANAR_Y_U_V', 'VDEF_RAW_DATA_LAYOUT_RGB24',
    'VDEF_RAW_DATA_LAYOUT_RGBA32', 'VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR',
    'VDEF_RAW_DATA_LAYOUT_SEMI_PLANAR_Y_UV',
    'VDEF_RAW_DATA_LAYOUT_UNKNOWN', 'VDEF_RAW_DATA_LAYOUT_YUYV',
    'VDEF_RAW_FORMAT_TO_STR_FMT', 'VDEF_RAW_MAX_PLANE_COUNT',
    'VDEF_RAW_MIME_TYPE', 'VDEF_RAW_PIX_FORMAT_BAYER',
    'VDEF_RAW_PIX_FORMAT_DEPTH', 'VDEF_RAW_PIX_FORMAT_DEPTH_FLOAT',
    'VDEF_RAW_PIX_FORMAT_GRAY', 'VDEF_RAW_PIX_FORMAT_RAW',
    'VDEF_RAW_PIX_FORMAT_RGB24', 'VDEF_RAW_PIX_FORMAT_RGBA32',
    'VDEF_RAW_PIX_FORMAT_UNKNOWN', 'VDEF_RAW_PIX_FORMAT_YUV420',
    'VDEF_RAW_PIX_FORMAT_YUV422', 'VDEF_RAW_PIX_FORMAT_YUV444',
    'VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16',
    'VDEF_RAW_PIX_LAYOUT_HISI_TILE_64x16_COMPRESSED',
    'VDEF_RAW_PIX_LAYOUT_LINEAR', 'VDEF_RAW_PIX_LAYOUT_UNKNOWN',
    'VDEF_RAW_PIX_ORDER_A', 'VDEF_RAW_PIX_ORDER_AB',
    'VDEF_RAW_PIX_ORDER_ABC', 'VDEF_RAW_PIX_ORDER_ABCD',
    'VDEF_RAW_PIX_ORDER_ABDC', 'VDEF_RAW_PIX_ORDER_ABGR',
    'VDEF_RAW_PIX_ORDER_ACB', 'VDEF_RAW_PIX_ORDER_ACBD',
    'VDEF_RAW_PIX_ORDER_ACDB', 'VDEF_RAW_PIX_ORDER_ADBC',
    'VDEF_RAW_PIX_ORDER_ADCB', 'VDEF_RAW_PIX_ORDER_BA',
    'VDEF_RAW_PIX_ORDER_BAC', 'VDEF_RAW_PIX_ORDER_BACD',
    'VDEF_RAW_PIX_ORDER_BADC', 'VDEF_RAW_PIX_ORDER_BCA',
    'VDEF_RAW_PIX_ORDER_BCAD', 'VDEF_RAW_PIX_ORDER_BCDA',
    'VDEF_RAW_PIX_ORDER_BDAC', 'VDEF_RAW_PIX_ORDER_BDCA',
    'VDEF_RAW_PIX_ORDER_BGGR', 'VDEF_RAW_PIX_ORDER_BGR',
    'VDEF_RAW_PIX_ORDER_BGRA', 'VDEF_RAW_PIX_ORDER_CAB',
    'VDEF_RAW_PIX_ORDER_CABD', 'VDEF_RAW_PIX_ORDER_CADB',
    'VDEF_RAW_PIX_ORDER_CBA', 'VDEF_RAW_PIX_ORDER_CBAD',
    'VDEF_RAW_PIX_ORDER_CBDA', 'VDEF_RAW_PIX_ORDER_CDAB',
    'VDEF_RAW_PIX_ORDER_CDBA', 'VDEF_RAW_PIX_ORDER_DABC',
    'VDEF_RAW_PIX_ORDER_DACB', 'VDEF_RAW_PIX_ORDER_DBAC',
    'VDEF_RAW_PIX_ORDER_DBCA', 'VDEF_RAW_PIX_ORDER_DCAB',
    'VDEF_RAW_PIX_ORDER_DCBA', 'VDEF_RAW_PIX_ORDER_GBRG',
    'VDEF_RAW_PIX_ORDER_GRBG', 'VDEF_RAW_PIX_ORDER_RGB',
    'VDEF_RAW_PIX_ORDER_RGBA', 'VDEF_RAW_PIX_ORDER_RGGB',
    'VDEF_RAW_PIX_ORDER_UNKNOWN', 'VDEF_RAW_PIX_ORDER_YUV',
    'VDEF_RAW_PIX_ORDER_YUYV', 'VDEF_RAW_PIX_ORDER_YVU',
    'VDEF_RAW_PIX_ORDER_YVYU', 'VDEF_TONE_MAPPING_MAX',
    'VDEF_TONE_MAPPING_P_LOG', 'VDEF_TONE_MAPPING_STANDARD',
    'VDEF_TONE_MAPPING_UNKNOWN', 'VDEF_TRANSFER_FUNCTION_BT2020',
    'VDEF_TRANSFER_FUNCTION_BT601', 'VDEF_TRANSFER_FUNCTION_BT709',
    'VDEF_TRANSFER_FUNCTION_HLG', 'VDEF_TRANSFER_FUNCTION_MAX',
    'VDEF_TRANSFER_FUNCTION_PQ', 'VDEF_TRANSFER_FUNCTION_SRGB',
    'VDEF_TRANSFER_FUNCTION_UNKNOWN', 'VMETA_API_VERSION',
    'VMETA_AUTOMATION_ANIM_BOOMERANG', 'VMETA_AUTOMATION_ANIM_CANDLE',
    'VMETA_AUTOMATION_ANIM_DOLLY_SLIDE',
    'VMETA_AUTOMATION_ANIM_DOLLY_ZOOM',
    'VMETA_AUTOMATION_ANIM_FLIP_BACK',
    'VMETA_AUTOMATION_ANIM_FLIP_FRONT',
    'VMETA_AUTOMATION_ANIM_FLIP_LEFT',
    'VMETA_AUTOMATION_ANIM_FLIP_RIGHT', 'VMETA_AUTOMATION_ANIM_NONE',
    'VMETA_AUTOMATION_ANIM_ORBIT',
    'VMETA_AUTOMATION_ANIM_PANORAMA_HORZ',
    'VMETA_AUTOMATION_ANIM_PARABOLA',
    'VMETA_AUTOMATION_ANIM_POSITION_TWISTUP',
    'VMETA_AUTOMATION_ANIM_REVEAL_HORZ',
    'VMETA_AUTOMATION_ANIM_REVEAL_VERT',
    'VMETA_AUTOMATION_ANIM_TWISTUP', 'VMETA_CAMERA_TYPE_DISPARITY',
    'VMETA_CAMERA_TYPE_FRONT', 'VMETA_CAMERA_TYPE_FRONT_STEREO_LEFT',
    'VMETA_CAMERA_TYPE_FRONT_STEREO_RIGHT',
    'VMETA_CAMERA_TYPE_UNKNOWN', 'VMETA_CAMERA_TYPE_VERTICAL',
    'VMETA_DYNAMIC_RANGE_HDR10', 'VMETA_DYNAMIC_RANGE_HDR8',
    'VMETA_DYNAMIC_RANGE_SDR', 'VMETA_DYNAMIC_RANGE_UNKNOWN',
    'VMETA_FLYING_STATE_EMERGENCY',
    'VMETA_FLYING_STATE_EMERGENCY_LANDING',
    'VMETA_FLYING_STATE_FLYING', 'VMETA_FLYING_STATE_HOVERING',
    'VMETA_FLYING_STATE_LANDED', 'VMETA_FLYING_STATE_LANDING',
    'VMETA_FLYING_STATE_MOTOR_RAMPING',
    'VMETA_FLYING_STATE_TAKINGOFF', 'VMETA_FLYING_STATE_USER_TAKEOFF',
    'VMETA_FOLLOWME_ANIM_BOOMERANG', 'VMETA_FOLLOWME_ANIM_NONE',
    'VMETA_FOLLOWME_ANIM_ORBIT', 'VMETA_FOLLOWME_ANIM_PARABOLA',
    'VMETA_FOLLOWME_ANIM_ZENITH', 'VMETA_FRAME_EXT_AUTOMATION_ID',
    'VMETA_FRAME_EXT_FOLLOWME_ID', 'VMETA_FRAME_EXT_THERMAL_ID',
    'VMETA_FRAME_EXT_TIMESTAMP_ID', 'VMETA_FRAME_MAX_SIZE',
    'VMETA_FRAME_PROTO_CONTENT_ENCODING',
    'VMETA_FRAME_PROTO_MIME_TYPE', 'VMETA_FRAME_PROTO_RTP_EXT_ID',
    'VMETA_FRAME_TYPE_NONE', 'VMETA_FRAME_TYPE_PROTO',
    'VMETA_FRAME_TYPE_V1_RECORDING',
    'VMETA_FRAME_TYPE_V1_STREAMING_BASIC',
    'VMETA_FRAME_TYPE_V1_STREAMING_EXTENDED', 'VMETA_FRAME_TYPE_V2',
    'VMETA_FRAME_TYPE_V3',
    'VMETA_FRAME_V1_RECORDING_CONTENT_ENCODING',
    'VMETA_FRAME_V1_RECORDING_MIME_TYPE',
    'VMETA_FRAME_V1_RECORDING_SIZE',
    'VMETA_FRAME_V1_STREAMING_BASIC_SIZE',
    'VMETA_FRAME_V1_STREAMING_EXTENDED_SIZE',
    'VMETA_FRAME_V1_STREAMING_ID', 'VMETA_FRAME_V2_BASE_ID',
    'VMETA_FRAME_V2_CONTENT_ENCODING', 'VMETA_FRAME_V2_MAX_SIZE',
    'VMETA_FRAME_V2_MIME_TYPE', 'VMETA_FRAME_V3_BASE_ID',
    'VMETA_FRAME_V3_CONTENT_ENCODING', 'VMETA_FRAME_V3_MAX_SIZE',
    'VMETA_FRAME_V3_MIME_TYPE', 'VMETA_PILOTING_MODE_FLIGHT_PLAN',
    'VMETA_PILOTING_MODE_FOLLOW_ME',
    'VMETA_PILOTING_MODE_MAGIC_CARPET', 'VMETA_PILOTING_MODE_MANUAL',
    'VMETA_PILOTING_MODE_MOVE_TO', 'VMETA_PILOTING_MODE_RETURN_HOME',
    'VMETA_PILOTING_MODE_TRACKING', 'VMETA_REC_META',
    'VMETA_REC_META_KEY_BOOT_ID', 'VMETA_REC_META_KEY_BUILD_ID',
    'VMETA_REC_META_KEY_CAMERA_TYPE', 'VMETA_REC_META_KEY_COMMENT',
    'VMETA_REC_META_KEY_COPYRIGHT', 'VMETA_REC_META_KEY_CUSTOM_ID',
    'VMETA_REC_META_KEY_DYNAMIC_RANGE',
    'VMETA_REC_META_KEY_FLIGHT_ID',
    'VMETA_REC_META_KEY_FRIENDLY_NAME', 'VMETA_REC_META_KEY_MAKER',
    'VMETA_REC_META_KEY_MEDIA_DATE', 'VMETA_REC_META_KEY_MODEL',
    'VMETA_REC_META_KEY_MODEL_ID', 'VMETA_REC_META_KEY_PICTURE_FOV',
    'VMETA_REC_META_KEY_PICTURE_HORZ_FOV',
    'VMETA_REC_META_KEY_PICTURE_VERT_FOV',
    'VMETA_REC_META_KEY_RUN_DATE', 'VMETA_REC_META_KEY_RUN_ID',
    'VMETA_REC_META_KEY_SERIAL_NUMBER',
    'VMETA_REC_META_KEY_SOFTWARE_VERSION',
    'VMETA_REC_META_KEY_TAKEOFF_LOC',
    'VMETA_REC_META_KEY_THERMAL_ALIGNMENT',
    'VMETA_REC_META_KEY_THERMAL_CAMSERIAL',
    'VMETA_REC_META_KEY_THERMAL_CONV_HIGH',
    'VMETA_REC_META_KEY_THERMAL_CONV_LOW',
    'VMETA_REC_META_KEY_THERMAL_METAVERSION',
    'VMETA_REC_META_KEY_THERMAL_SCALE_FACTOR',
    'VMETA_REC_META_KEY_TITLE', 'VMETA_REC_META_KEY_TONE_MAPPING',
    'VMETA_REC_META_KEY_VIDEO_MODE',
    'VMETA_REC_META_KEY_VIDEO_STOP_REASON', 'VMETA_REC_UDTA',
    'VMETA_REC_UDTA_JSON_KEY_MEDIA_DATE',
    'VMETA_REC_UDTA_JSON_KEY_PICTURE_HORZ_FOV',
    'VMETA_REC_UDTA_JSON_KEY_PICTURE_VERT_FOV',
    'VMETA_REC_UDTA_JSON_KEY_RUN_ID',
    'VMETA_REC_UDTA_JSON_KEY_SOFTWARE_VERSION',
    'VMETA_REC_UDTA_JSON_KEY_TAKEOFF_LOC',
    'VMETA_REC_UDTA_KEY_COMMENT', 'VMETA_REC_UDTA_KEY_COPYRIGHT',
    'VMETA_REC_UDTA_KEY_FRIENDLY_NAME', 'VMETA_REC_UDTA_KEY_MAKER',
    'VMETA_REC_UDTA_KEY_MEDIA_DATE', 'VMETA_REC_UDTA_KEY_MODEL',
    'VMETA_REC_UDTA_KEY_SERIAL_NUMBER',
    'VMETA_REC_UDTA_KEY_SOFTWARE_VERSION',
    'VMETA_REC_UDTA_KEY_TAKEOFF_LOC', 'VMETA_REC_UDTA_KEY_TITLE',
    'VMETA_REC_XYZ', 'VMETA_SESSION_DATE_MAX_LEN',
    'VMETA_SESSION_FOV_FORMAT', 'VMETA_SESSION_FOV_MAX_LEN',
    'VMETA_SESSION_LOCATION_CSV', 'VMETA_SESSION_LOCATION_FORMAT_CSV',
    'VMETA_SESSION_LOCATION_FORMAT_ISO6709',
    'VMETA_SESSION_LOCATION_FORMAT_XYZ',
    'VMETA_SESSION_LOCATION_ISO6709',
    'VMETA_SESSION_LOCATION_MAX_LEN', 'VMETA_SESSION_LOCATION_XYZ',
    'VMETA_SESSION_THERMAL_ALIGNMENT_FORMAT',
    'VMETA_SESSION_THERMAL_ALIGNMENT_MAX_LEN',
    'VMETA_SESSION_THERMAL_CONVERSION_FORMAT',
    'VMETA_SESSION_THERMAL_CONVERSION_MAX_LEN',
    'VMETA_SESSION_THERMAL_SCALE_FACTOR_FORMAT',
    'VMETA_SESSION_THERMAL_SCALE_FACTOR_MAX_LEN',
    'VMETA_STRM_SDES_KEY_BOOT_ID', 'VMETA_STRM_SDES_KEY_BUILD_ID',
    'VMETA_STRM_SDES_KEY_CAMERA_TYPE', 'VMETA_STRM_SDES_KEY_COMMENT',
    'VMETA_STRM_SDES_KEY_COPYRIGHT', 'VMETA_STRM_SDES_KEY_CUSTOM_ID',
    'VMETA_STRM_SDES_KEY_DYNAMIC_RANGE',
    'VMETA_STRM_SDES_KEY_FLIGHT_ID', 'VMETA_STRM_SDES_KEY_MAKER',
    'VMETA_STRM_SDES_KEY_MEDIA_DATE', 'VMETA_STRM_SDES_KEY_MODEL',
    'VMETA_STRM_SDES_KEY_MODEL_ID', 'VMETA_STRM_SDES_KEY_PICTURE_FOV',
    'VMETA_STRM_SDES_KEY_PICTURE_HORZ_FOV',
    'VMETA_STRM_SDES_KEY_PICTURE_VERT_FOV',
    'VMETA_STRM_SDES_KEY_RUN_DATE', 'VMETA_STRM_SDES_KEY_RUN_ID',
    'VMETA_STRM_SDES_KEY_THERMAL_ALIGNMENT',
    'VMETA_STRM_SDES_KEY_THERMAL_CAMSERIAL',
    'VMETA_STRM_SDES_KEY_THERMAL_CONV_HIGH',
    'VMETA_STRM_SDES_KEY_THERMAL_CONV_LOW',
    'VMETA_STRM_SDES_KEY_THERMAL_METAVERSION',
    'VMETA_STRM_SDES_KEY_THERMAL_SCALE_FACTOR',
    'VMETA_STRM_SDES_KEY_TITLE', 'VMETA_STRM_SDES_KEY_TONE_MAPPING',
    'VMETA_STRM_SDES_KEY_VIDEO_MODE',
    'VMETA_STRM_SDES_KEY_VIDEO_STOP_REASON',
    'VMETA_STRM_SDES_TYPE_CNAME', 'VMETA_STRM_SDES_TYPE_EMAIL',
    'VMETA_STRM_SDES_TYPE_END', 'VMETA_STRM_SDES_TYPE_LOC',
    'VMETA_STRM_SDES_TYPE_NAME', 'VMETA_STRM_SDES_TYPE_NOTE',
    'VMETA_STRM_SDES_TYPE_PHONE', 'VMETA_STRM_SDES_TYPE_PRIV',
    'VMETA_STRM_SDES_TYPE_TOOL', 'VMETA_STRM_SDP_KEY_BOOT_ID',
    'VMETA_STRM_SDP_KEY_BUILD_ID', 'VMETA_STRM_SDP_KEY_CAMERA_TYPE',
    'VMETA_STRM_SDP_KEY_COMMENT', 'VMETA_STRM_SDP_KEY_COPYRIGHT',
    'VMETA_STRM_SDP_KEY_CUSTOM_ID',
    'VMETA_STRM_SDP_KEY_DYNAMIC_RANGE',
    'VMETA_STRM_SDP_KEY_FLIGHT_ID', 'VMETA_STRM_SDP_KEY_MAKER',
    'VMETA_STRM_SDP_KEY_MEDIA_DATE', 'VMETA_STRM_SDP_KEY_MODEL',
    'VMETA_STRM_SDP_KEY_MODEL_ID', 'VMETA_STRM_SDP_KEY_PICTURE_FOV',
    'VMETA_STRM_SDP_KEY_RUN_DATE', 'VMETA_STRM_SDP_KEY_RUN_ID',
    'VMETA_STRM_SDP_KEY_SERIAL_NUMBER',
    'VMETA_STRM_SDP_KEY_TAKEOFF_LOC',
    'VMETA_STRM_SDP_KEY_THERMAL_ALIGNMENT',
    'VMETA_STRM_SDP_KEY_THERMAL_CAMSERIAL',
    'VMETA_STRM_SDP_KEY_THERMAL_CONV_HIGH',
    'VMETA_STRM_SDP_KEY_THERMAL_CONV_LOW',
    'VMETA_STRM_SDP_KEY_THERMAL_METAVERSION',
    'VMETA_STRM_SDP_KEY_THERMAL_SCALE_FACTOR',
    'VMETA_STRM_SDP_KEY_TONE_MAPPING',
    'VMETA_STRM_SDP_KEY_VIDEO_MODE',
    'VMETA_STRM_SDP_KEY_VIDEO_STOP_REASON',
    'VMETA_STRM_SDP_TYPE_MEDIA_ATTR',
    'VMETA_STRM_SDP_TYPE_MEDIA_INFO',
    'VMETA_STRM_SDP_TYPE_SESSION_ATTR',
    'VMETA_STRM_SDP_TYPE_SESSION_INFO',
    'VMETA_STRM_SDP_TYPE_SESSION_NAME',
    'VMETA_STRM_SDP_TYPE_SESSION_TOOL',
    'VMETA_THERMAL_CALIB_STATE_DONE',
    'VMETA_THERMAL_CALIB_STATE_IN_PROGRESS',
    'VMETA_THERMAL_CALIB_STATE_REQUESTED', 'VMETA_TONE_MAPPING_P_LOG',
    'VMETA_TONE_MAPPING_STANDARD', 'VMETA_TONE_MAPPING_UNKNOWN',
    'VMETA_VIDEO_MODE_HYPERLAPSE', 'VMETA_VIDEO_MODE_SLOWMOTION',
    'VMETA_VIDEO_MODE_STANDARD', 'VMETA_VIDEO_MODE_UNKNOWN',
    'VMETA_VIDEO_STOP_REASON_END_OF_STREAM',
    'VMETA_VIDEO_STOP_REASON_POOR_STORAGE_PERF',
    'VMETA_VIDEO_STOP_REASON_RECONFIGURATION',
    'VMETA_VIDEO_STOP_REASON_RECOVERY',
    'VMETA_VIDEO_STOP_REASON_SHUTDOWN',
    'VMETA_VIDEO_STOP_REASON_STORAGE_FULL',
    'VMETA_VIDEO_STOP_REASON_UNKNOWN', 'VMETA_VIDEO_STOP_REASON_USER',
    'VMETA__FLYING_STATE__FS_EMERGENCY',
    'VMETA__FLYING_STATE__FS_FLYING',
    'VMETA__FLYING_STATE__FS_HOVERING',
    'VMETA__FLYING_STATE__FS_LANDED',
    'VMETA__FLYING_STATE__FS_LANDING',
    'VMETA__FLYING_STATE__FS_TAKINGOFF',
    'VMETA__LINK_METADATA__PROTOCOL_STARFISH',
    'VMETA__LINK_METADATA__PROTOCOL_WIFI',
    'VMETA__LINK_METADATA__PROTOCOL__NOT_SET',
    'VMETA__LINK_STATUS__LINK_STATUS_CONNECTING',
    'VMETA__LINK_STATUS__LINK_STATUS_DOWN',
    'VMETA__LINK_STATUS__LINK_STATUS_ERROR',
    'VMETA__LINK_STATUS__LINK_STATUS_READY',
    'VMETA__LINK_STATUS__LINK_STATUS_RUNNING',
    'VMETA__LINK_STATUS__LINK_STATUS_UP',
    'VMETA__LINK_TYPE__LINK_TYPE_CELLULAR',
    'VMETA__LINK_TYPE__LINK_TYPE_LAN',
    'VMETA__LINK_TYPE__LINK_TYPE_LO',
    'VMETA__LINK_TYPE__LINK_TYPE_UNKNOWN',
    'VMETA__LINK_TYPE__LINK_TYPE_WLAN',
    'VMETA__TRACKING_CLASS__TC_ANIMAL',
    'VMETA__TRACKING_CLASS__TC_BICYCLE',
    'VMETA__TRACKING_CLASS__TC_BOAT', 'VMETA__TRACKING_CLASS__TC_CAR',
    'VMETA__TRACKING_CLASS__TC_HORSE',
    'VMETA__TRACKING_CLASS__TC_MOTORBIKE',
    'VMETA__TRACKING_CLASS__TC_PERSON',
    'VMETA__TRACKING_CLASS__TC_UNDEFINED',
    'VMETA__TRACKING_STATE__TS_SEARCHING',
    'VMETA__TRACKING_STATE__TS_TRACKING', 'Vmeta__FlyingState',
    'Vmeta__FlyingState__enumvalues', 'WCHAR_WIDTH', 'WINT_MAX',
    'WINT_MIN', 'WINT_WIDTH', '_ARSDKCTRL_BACKEND_H_',
    '_ARSDKCTRL_BACKEND_MUX_H_', '_ARSDKCTRL_BACKEND_NET_H_',
    '_ARSDKCTRL_H_', '_ARSDK_BACKEND_H_', '_ARSDK_BACKEND_MUX_H_',
    '_ARSDK_BACKEND_NET_H_', '_ARSDK_BLACKBOX_ITF_H_',
    '_ARSDK_CMD_ITF_H_', '_ARSDK_CRASHML_ITF_H_', '_ARSDK_CTRL_H_',
    '_ARSDK_DESC_H_', '_ARSDK_DEVICE_H_', '_ARSDK_DISCOVERY_AVAHI_H_',
    '_ARSDK_DISCOVERY_INTERNAL_H_', '_ARSDK_DISCOVERY_MUX_H_',
    '_ARSDK_DISCOVERY_NET_H_', '_ARSDK_EPHEMERIS_ITF_H_',
    '_ARSDK_FTP_ITF_H_', '_ARSDK_H_', '_ARSDK_MEDIA_ITF_H_',
    '_ARSDK_MNGR_H_', '_ARSDK_PEER_H_', '_ARSDK_PUBLISHER_AVAHI_H_',
    '_ARSDK_PUBLISHER_MUX_H_', '_ARSDK_PUBLISHER_NET_H_',
    '_ARSDK_PUD_ITF_H_', '_ARSDK_UPDATER_ITF_H_', '_LIBMP4_H_',
    '_LIBMUX_ARSDK_H_', '_LIBMUX_H_', '_LIBPOMP_H_',
    '_MBUF_ANCILLARY_DATA_H_', '_MBUF_CODED_VIDEO_FRAME_H_',
    '_MBUF_MEM_GENERIC_H_', '_MBUF_MEM_H_',
    '_MBUF_RAW_VIDEO_FRAME_H_', '_PDRAW_DEFS_H_', '_PDRAW_H_',
    '_STDINT_H', '_VDEFS_H_', '_VMETA_FRAME_H_',
    '_VMETA_FRAME_PROTO_H_', '_VMETA_FRAME_V1_H_',
    '_VMETA_FRAME_V2_H_', '_VMETA_FRAME_V3_H_', '_VMETA_H_',
    '_VMETA_SESSION_H_', '_VMETA__FLYING_STATE_IS_INT_SIZE',
    '_VMETA__LINK_METADATA__PROTOCOL_IS_INT_SIZE',
    '_VMETA__LINK_STATUS_IS_INT_SIZE',
    '_VMETA__LINK_TYPE_IS_INT_SIZE',
    '_VMETA__TRACKING_CLASS_IS_INT_SIZE',
    '_VMETA__TRACKING_STATE_IS_INT_SIZE', '_Vmeta__FlyingState',
    '_Vmeta__LinkStatus', '_Vmeta__LinkType', '_Vmeta__TrackingClass',
    '_Vmeta__TrackingState',
    '__GLIBC_INTERNAL_STARTING_HEADER_IMPLEMENTATION',
    '__intptr_t_defined', 'arsdk_arg_type', 'arsdk_arg_type_str',
    'arsdk_backend_mux_destroy', 'arsdk_backend_mux_get_mux_ctx',
    'arsdk_backend_mux_get_parent', 'arsdk_backend_mux_new',
    'arsdk_backend_mux_start_listen', 'arsdk_backend_mux_stop_listen',
    'arsdk_backend_net_destroy', 'arsdk_backend_net_get_parent',
    'arsdk_backend_net_new', 'arsdk_backend_net_set_socket_cb',
    'arsdk_backend_net_socket_cb_t', 'arsdk_backend_net_start_listen',
    'arsdk_backend_net_stop_listen', 'arsdk_backend_type',
    'arsdk_backend_type_str', 'arsdk_blackbox_itf_create_listener',
    'arsdk_blackbox_listener_unregister', 'arsdk_cmd_buffer_type',
    'arsdk_cmd_clear', 'arsdk_cmd_copy', 'arsdk_cmd_dec',
    'arsdk_cmd_dec_header', 'arsdk_cmd_dir', 'arsdk_cmd_enc',
    'arsdk_cmd_enc_argv', 'arsdk_cmd_find_desc', 'arsdk_cmd_fmt',
    'arsdk_cmd_get_name', 'arsdk_cmd_get_values', 'arsdk_cmd_init',
    'arsdk_cmd_init_with_buf', 'arsdk_cmd_itf_get_osdata',
    'arsdk_cmd_itf_send', 'arsdk_cmd_itf_send_status',
    'arsdk_cmd_itf_send_status_cb_t', 'arsdk_cmd_itf_send_status_str',
    'arsdk_cmd_itf_set_osdata', 'arsdk_cmd_list_type',
    'arsdk_cmd_timeout_policy', 'arsdk_conn_cancel_reason',
    'arsdk_conn_cancel_reason_str', 'arsdk_crashml_itf_cancel_all',
    'arsdk_crashml_itf_create_req', 'arsdk_crashml_req_cancel',
    'arsdk_crashml_req_get_dev_type', 'arsdk_crashml_req_status',
    'arsdk_crashml_type', 'arsdk_ctrl_destroy',
    'arsdk_ctrl_get_device', 'arsdk_ctrl_get_loop', 'arsdk_ctrl_new',
    'arsdk_ctrl_next_device', 'arsdk_ctrl_set_device_cbs',
    'arsdk_device_api', 'arsdk_device_connect',
    'arsdk_device_create_cmd_itf', 'arsdk_device_create_tcp_proxy',
    'arsdk_device_destroy_tcp_proxy', 'arsdk_device_disconnect',
    'arsdk_device_get_backend', 'arsdk_device_get_blackbox_itf',
    'arsdk_device_get_cmd_itf', 'arsdk_device_get_crashml_itf',
    'arsdk_device_get_ephemeris_itf',
    'arsdk_device_get_flight_log_itf', 'arsdk_device_get_ftp_itf',
    'arsdk_device_get_handle', 'arsdk_device_get_info',
    'arsdk_device_get_media_itf', 'arsdk_device_get_pud_itf',
    'arsdk_device_get_updater_itf', 'arsdk_device_state',
    'arsdk_device_state_str', 'arsdk_device_tcp_proxy_get_addr',
    'arsdk_device_tcp_proxy_get_port', 'arsdk_device_type',
    'arsdk_device_type_str', 'arsdk_discovery_add_device',
    'arsdk_discovery_avahi_destroy', 'arsdk_discovery_avahi_new',
    'arsdk_discovery_avahi_start', 'arsdk_discovery_avahi_stop',
    'arsdk_discovery_destroy', 'arsdk_discovery_mux_destroy',
    'arsdk_discovery_mux_new', 'arsdk_discovery_mux_start',
    'arsdk_discovery_mux_stop', 'arsdk_discovery_net_destroy',
    'arsdk_discovery_net_new', 'arsdk_discovery_net_new_with_port',
    'arsdk_discovery_net_start', 'arsdk_discovery_net_stop',
    'arsdk_discovery_new', 'arsdk_discovery_remove_device',
    'arsdk_discovery_start', 'arsdk_discovery_stop',
    'arsdk_ephemeris_itf_cancel_all',
    'arsdk_ephemeris_itf_create_req_upload',
    'arsdk_ephemeris_req_status', 'arsdk_ephemeris_req_upload_cancel',
    'arsdk_ephemeris_req_upload_get_dev_type',
    'arsdk_ephemeris_req_upload_get_file_path',
    'arsdk_ftp_file_get_name', 'arsdk_ftp_file_get_size',
    'arsdk_ftp_file_get_type', 'arsdk_ftp_file_list_get_count',
    'arsdk_ftp_file_list_next_file', 'arsdk_ftp_file_list_ref',
    'arsdk_ftp_file_list_unref', 'arsdk_ftp_file_ref',
    'arsdk_ftp_file_type', 'arsdk_ftp_file_unref',
    'arsdk_ftp_itf_cancel_all', 'arsdk_ftp_itf_create_req_delete',
    'arsdk_ftp_itf_create_req_get', 'arsdk_ftp_itf_create_req_list',
    'arsdk_ftp_itf_create_req_put',
    'arsdk_ftp_itf_create_req_put_buff',
    'arsdk_ftp_itf_create_req_rename', 'arsdk_ftp_req_delete_cancel',
    'arsdk_ftp_req_delete_get_dev_type',
    'arsdk_ftp_req_delete_get_path', 'arsdk_ftp_req_get_cancel',
    'arsdk_ftp_req_get_get_buffer', 'arsdk_ftp_req_get_get_dev_type',
    'arsdk_ftp_req_get_get_dlsize',
    'arsdk_ftp_req_get_get_local_path',
    'arsdk_ftp_req_get_get_remote_path',
    'arsdk_ftp_req_get_get_total_size', 'arsdk_ftp_req_list_cancel',
    'arsdk_ftp_req_list_get_dev_type', 'arsdk_ftp_req_list_get_path',
    'arsdk_ftp_req_list_get_result', 'arsdk_ftp_req_put_cancel',
    'arsdk_ftp_req_put_get_dev_type',
    'arsdk_ftp_req_put_get_local_path',
    'arsdk_ftp_req_put_get_remote_path',
    'arsdk_ftp_req_put_get_total_size',
    'arsdk_ftp_req_put_get_ulsize', 'arsdk_ftp_req_rename_cancel',
    'arsdk_ftp_req_rename_get_dev_type',
    'arsdk_ftp_req_rename_get_dst', 'arsdk_ftp_req_rename_get_src',
    'arsdk_ftp_req_status', 'arsdk_ftp_srv_type',
    'arsdk_get_cmd_table', 'arsdk_link_status',
    'arsdk_link_status_str', 'arsdk_media_get_date',
    'arsdk_media_get_name', 'arsdk_media_get_res_count',
    'arsdk_media_get_runid', 'arsdk_media_get_type',
    'arsdk_media_itf_cancel_all', 'arsdk_media_itf_create_req_delete',
    'arsdk_media_itf_create_req_download',
    'arsdk_media_itf_create_req_list', 'arsdk_media_list_get_count',
    'arsdk_media_list_next_media', 'arsdk_media_list_ref',
    'arsdk_media_list_unref', 'arsdk_media_next_res',
    'arsdk_media_ref', 'arsdk_media_req_delete_get_dev_type',
    'arsdk_media_req_delete_get_media',
    'arsdk_media_req_download_cancel',
    'arsdk_media_req_download_get_buffer',
    'arsdk_media_req_download_get_dev_type',
    'arsdk_media_req_download_get_local_path',
    'arsdk_media_req_download_get_uri', 'arsdk_media_req_list_cancel',
    'arsdk_media_req_list_get_dev_type',
    'arsdk_media_req_list_get_result', 'arsdk_media_req_status',
    'arsdk_media_res_format', 'arsdk_media_res_get_fmt',
    'arsdk_media_res_get_name', 'arsdk_media_res_get_size',
    'arsdk_media_res_get_type', 'arsdk_media_res_get_uri',
    'arsdk_media_res_type', 'arsdk_media_type', 'arsdk_media_unref',
    'arsdk_mngr_destroy', 'arsdk_mngr_get_loop',
    'arsdk_mngr_get_peer', 'arsdk_mngr_new', 'arsdk_mngr_next_peer',
    'arsdk_mngr_set_peer_cbs', 'arsdk_peer_accept',
    'arsdk_peer_create_cmd_itf', 'arsdk_peer_disconnect',
    'arsdk_peer_get_backend', 'arsdk_peer_get_cmd_itf',
    'arsdk_peer_get_handle', 'arsdk_peer_get_info',
    'arsdk_peer_reject', 'arsdk_publisher_avahi_destroy',
    'arsdk_publisher_avahi_new', 'arsdk_publisher_avahi_start',
    'arsdk_publisher_avahi_stop', 'arsdk_publisher_mux_destroy',
    'arsdk_publisher_mux_new', 'arsdk_publisher_mux_start',
    'arsdk_publisher_mux_stop', 'arsdk_publisher_net_destroy',
    'arsdk_publisher_net_new', 'arsdk_publisher_net_start',
    'arsdk_publisher_net_stop', 'arsdk_pud_itf_cancel_all',
    'arsdk_pud_itf_create_req', 'arsdk_pud_req_cancel',
    'arsdk_pud_req_get_dev_type', 'arsdk_pud_req_status',
    'arsdk_socket_kind', 'arsdk_socket_kind_str',
    'arsdk_updater_appid_to_devtype', 'arsdk_updater_itf_cancel_all',
    'arsdk_updater_itf_create_req_upload', 'arsdk_updater_req_status',
    'arsdk_updater_req_upload_cancel',
    'arsdk_updater_req_upload_get_dev_type',
    'arsdkctrl_backend_mux_destroy',
    'arsdkctrl_backend_mux_get_mux_ctx',
    'arsdkctrl_backend_mux_get_parent', 'arsdkctrl_backend_mux_new',
    'arsdkctrl_backend_net_destroy',
    'arsdkctrl_backend_net_get_parent', 'arsdkctrl_backend_net_new',
    'arsdkctrl_backend_net_set_socket_cb',
    'arsdkctrl_backend_net_socket_cb_t', 'c__EA_ProtobufCLabel',
    'c__EA_ProtobufCType', 'c__EA_ProtobufCWireType',
    'c__EA_Vmeta__LinkMetadata__ProtocolCase', 'h264_nalu_type',
    'h264_slice_type', 'h265_nalu_type', 'int16_t', 'int32_t',
    'int64_t', 'int8_t', 'int_fast16_t', 'int_fast32_t',
    'int_fast64_t', 'int_fast8_t', 'int_least16_t', 'int_least32_t',
    'int_least64_t', 'int_least8_t', 'intmax_t', 'intptr_t',
    'mbuf_ancillary_data_cb_t', 'mbuf_ancillary_data_get_buffer',
    'mbuf_ancillary_data_get_name', 'mbuf_ancillary_data_get_string',
    'mbuf_ancillary_data_is_string', 'mbuf_ancillary_data_ref',
    'mbuf_ancillary_data_unref',
    'mbuf_coded_video_frame_add_ancillary_buffer',
    'mbuf_coded_video_frame_add_ancillary_data',
    'mbuf_coded_video_frame_add_ancillary_string',
    'mbuf_coded_video_frame_add_nalu',
    'mbuf_coded_video_frame_ancillary_data_copier',
    'mbuf_coded_video_frame_copy', 'mbuf_coded_video_frame_finalize',
    'mbuf_coded_video_frame_foreach_ancillary_data',
    'mbuf_coded_video_frame_get_ancillary_data',
    'mbuf_coded_video_frame_get_frame_info',
    'mbuf_coded_video_frame_get_metadata',
    'mbuf_coded_video_frame_get_nalu',
    'mbuf_coded_video_frame_get_nalu_count',
    'mbuf_coded_video_frame_get_nalu_mem_info',
    'mbuf_coded_video_frame_get_packed_buffer',
    'mbuf_coded_video_frame_get_packed_size',
    'mbuf_coded_video_frame_get_rw_nalu',
    'mbuf_coded_video_frame_get_rw_packed_buffer',
    'mbuf_coded_video_frame_insert_nalu',
    'mbuf_coded_video_frame_new',
    'mbuf_coded_video_frame_pre_release_t',
    'mbuf_coded_video_frame_queue_destroy',
    'mbuf_coded_video_frame_queue_filter_t',
    'mbuf_coded_video_frame_queue_flush',
    'mbuf_coded_video_frame_queue_get_event',
    'mbuf_coded_video_frame_queue_new',
    'mbuf_coded_video_frame_queue_new_with_args',
    'mbuf_coded_video_frame_queue_peek',
    'mbuf_coded_video_frame_queue_pop',
    'mbuf_coded_video_frame_queue_push', 'mbuf_coded_video_frame_ref',
    'mbuf_coded_video_frame_release_nalu',
    'mbuf_coded_video_frame_release_packed_buffer',
    'mbuf_coded_video_frame_release_rw_nalu',
    'mbuf_coded_video_frame_release_rw_packed_buffer',
    'mbuf_coded_video_frame_remove_ancillary_data',
    'mbuf_coded_video_frame_set_callbacks',
    'mbuf_coded_video_frame_set_frame_info',
    'mbuf_coded_video_frame_set_metadata',
    'mbuf_coded_video_frame_unref',
    'mbuf_coded_video_frame_uses_mem_from_pool',
    'mbuf_mem_generic_cookie', 'mbuf_mem_generic_impl',
    'mbuf_mem_generic_new', 'mbuf_mem_generic_releaser_free',
    'mbuf_mem_generic_wrap', 'mbuf_mem_generic_wrap_cookie',
    'mbuf_mem_generic_wrap_release_t', 'mbuf_mem_get_data',
    'mbuf_mem_ref', 'mbuf_mem_unref', 'mbuf_pool_destroy',
    'mbuf_pool_get', 'mbuf_pool_get_count', 'mbuf_pool_get_name',
    'mbuf_pool_grow_policy', 'mbuf_pool_new',
    'mbuf_raw_video_frame_add_ancillary_buffer',
    'mbuf_raw_video_frame_add_ancillary_data',
    'mbuf_raw_video_frame_add_ancillary_string',
    'mbuf_raw_video_frame_ancillary_data_copier',
    'mbuf_raw_video_frame_copy', 'mbuf_raw_video_frame_finalize',
    'mbuf_raw_video_frame_foreach_ancillary_data',
    'mbuf_raw_video_frame_get_ancillary_data',
    'mbuf_raw_video_frame_get_frame_info',
    'mbuf_raw_video_frame_get_metadata',
    'mbuf_raw_video_frame_get_packed_buffer',
    'mbuf_raw_video_frame_get_packed_size',
    'mbuf_raw_video_frame_get_plane',
    'mbuf_raw_video_frame_get_plane_mem_info',
    'mbuf_raw_video_frame_get_rw_packed_buffer',
    'mbuf_raw_video_frame_get_rw_plane', 'mbuf_raw_video_frame_new',
    'mbuf_raw_video_frame_pre_release_t',
    'mbuf_raw_video_frame_queue_destroy',
    'mbuf_raw_video_frame_queue_filter_t',
    'mbuf_raw_video_frame_queue_flush',
    'mbuf_raw_video_frame_queue_get_event',
    'mbuf_raw_video_frame_queue_new',
    'mbuf_raw_video_frame_queue_new_with_args',
    'mbuf_raw_video_frame_queue_peek',
    'mbuf_raw_video_frame_queue_pop',
    'mbuf_raw_video_frame_queue_push', 'mbuf_raw_video_frame_ref',
    'mbuf_raw_video_frame_release_packed_buffer',
    'mbuf_raw_video_frame_release_plane',
    'mbuf_raw_video_frame_release_rw_packed_buffer',
    'mbuf_raw_video_frame_release_rw_plane',
    'mbuf_raw_video_frame_remove_ancillary_data',
    'mbuf_raw_video_frame_set_callbacks',
    'mbuf_raw_video_frame_set_frame_info',
    'mbuf_raw_video_frame_set_metadata',
    'mbuf_raw_video_frame_set_plane', 'mbuf_raw_video_frame_unref',
    'mbuf_raw_video_frame_uses_mem_from_pool', 'mp4_audio_codec',
    'mp4_audio_codec_str', 'mp4_convert_timescale', 'mp4_demux_close',
    'mp4_demux_get_chapters', 'mp4_demux_get_media_info',
    'mp4_demux_get_metadata_cover', 'mp4_demux_get_metadata_strings',
    'mp4_demux_get_track_audio_specific_config',
    'mp4_demux_get_track_count', 'mp4_demux_get_track_info',
    'mp4_demux_get_track_metadata_strings',
    'mp4_demux_get_track_next_sample_time',
    'mp4_demux_get_track_next_sample_time_after',
    'mp4_demux_get_track_prev_sample_time',
    'mp4_demux_get_track_prev_sample_time_before',
    'mp4_demux_get_track_sample',
    'mp4_demux_get_track_video_decoder_config', 'mp4_demux_open',
    'mp4_demux_seek', 'mp4_demux_seek_to_track_next_sample',
    'mp4_demux_seek_to_track_prev_sample',
    'mp4_generate_avc_decoder_config', 'mp4_metadata_cover_type',
    'mp4_metadata_cover_type_str', 'mp4_mux_add_file_metadata',
    'mp4_mux_add_ref_to_track', 'mp4_mux_add_track',
    'mp4_mux_add_track_metadata', 'mp4_mux_close', 'mp4_mux_dump',
    'mp4_mux_open', 'mp4_mux_open2', 'mp4_mux_set_file_cover',
    'mp4_mux_sync', 'mp4_mux_track_add_sample',
    'mp4_mux_track_add_scattered_sample',
    'mp4_mux_track_set_audio_specific_config',
    'mp4_mux_track_set_metadata_mime_type',
    'mp4_mux_track_set_video_decoder_config',
    'mp4_sample_time_to_usec', 'mp4_seek_method', 'mp4_track_type',
    'mp4_track_type_str', 'mp4_usec_to_sample_time',
    'mp4_video_codec', 'mp4_video_codec_str',
    'mux_channel_alloc_queue', 'mux_channel_cb_t',
    'mux_channel_close', 'mux_channel_event', 'mux_channel_open',
    'mux_decode', 'mux_encode', 'mux_get_loop',
    'mux_get_remote_version', 'mux_ip_proxy_application',
    'mux_ip_proxy_destroy', 'mux_ip_proxy_get_local_info',
    'mux_ip_proxy_get_peerport', 'mux_ip_proxy_get_remote_addr',
    'mux_ip_proxy_get_remote_host', 'mux_ip_proxy_get_remote_port',
    'mux_ip_proxy_new', 'mux_ip_proxy_set_udp_redirect_port',
    'mux_ip_proxy_set_udp_remote', 'mux_ip_proxy_transport',
    'mux_new', 'mux_queue_get_buf', 'mux_queue_timed_get_buf',
    'mux_queue_try_get_buf', 'mux_ref', 'mux_reset', 'mux_resolve',
    'mux_run', 'mux_stop', 'mux_unref',
    'pdraw_coded_video_sink_destroy',
    'pdraw_coded_video_sink_get_queue', 'pdraw_coded_video_sink_new',
    'pdraw_coded_video_sink_queue_flushed',
    'pdraw_coded_video_sink_resync', 'pdraw_demuxer_close',
    'pdraw_demuxer_destroy', 'pdraw_demuxer_get_current_time',
    'pdraw_demuxer_get_duration',
    'pdraw_demuxer_get_single_stream_local_control_port',
    'pdraw_demuxer_get_single_stream_local_stream_port',
    'pdraw_demuxer_is_paused', 'pdraw_demuxer_is_ready_to_play',
    'pdraw_demuxer_new_from_url', 'pdraw_demuxer_new_from_url_on_mux',
    'pdraw_demuxer_new_single_stream', 'pdraw_demuxer_next_frame',
    'pdraw_demuxer_pause', 'pdraw_demuxer_play',
    'pdraw_demuxer_play_with_speed', 'pdraw_demuxer_previous_frame',
    'pdraw_demuxer_seek', 'pdraw_demuxer_seek_back',
    'pdraw_demuxer_seek_forward', 'pdraw_demuxer_seek_to',
    'pdraw_destroy', 'pdraw_dump_pipeline',
    'pdraw_get_display_screen_settings',
    'pdraw_get_friendly_name_setting', 'pdraw_get_hmd_model_setting',
    'pdraw_get_pipeline_mode_setting',
    'pdraw_get_serial_number_setting',
    'pdraw_get_software_version_setting', 'pdraw_histogram_channel',
    'pdraw_histogram_channel_str', 'pdraw_hmd_model',
    'pdraw_hmd_model_str', 'pdraw_media_info_dup',
    'pdraw_media_info_free', 'pdraw_media_type',
    'pdraw_media_type_str', 'pdraw_muxer_add_media',
    'pdraw_muxer_destroy', 'pdraw_muxer_new', 'pdraw_new',
    'pdraw_pipeline_mode', 'pdraw_pipeline_mode_str',
    'pdraw_playback_type', 'pdraw_playback_type_str',
    'pdraw_raw_video_sink_destroy', 'pdraw_raw_video_sink_get_queue',
    'pdraw_raw_video_sink_new', 'pdraw_raw_video_sink_queue_flushed',
    'pdraw_set_android_jvm', 'pdraw_set_display_screen_settings',
    'pdraw_set_friendly_name_setting', 'pdraw_set_hmd_model_setting',
    'pdraw_set_pipeline_mode_setting',
    'pdraw_set_serial_number_setting',
    'pdraw_set_software_version_setting', 'pdraw_stop',
    'pdraw_video_frame_to_json', 'pdraw_video_frame_to_json_str',
    'pdraw_video_renderer_destroy', 'pdraw_video_renderer_fill_mode',
    'pdraw_video_renderer_fill_mode_str',
    'pdraw_video_renderer_get_media_id',
    'pdraw_video_renderer_get_params', 'pdraw_video_renderer_new',
    'pdraw_video_renderer_new_egl', 'pdraw_video_renderer_render',
    'pdraw_video_renderer_render_mat', 'pdraw_video_renderer_resize',
    'pdraw_video_renderer_set_media_id',
    'pdraw_video_renderer_set_params',
    'pdraw_video_renderer_transition_flag',
    'pdraw_video_renderer_transition_flag_str', 'pdraw_video_type',
    'pdraw_video_type_str', 'pomp_addr_format',
    'pomp_addr_get_real_addr', 'pomp_addr_is_unix', 'pomp_addr_parse',
    'pomp_buffer_append_buffer', 'pomp_buffer_append_data',
    'pomp_buffer_cread', 'pomp_buffer_ensure_capacity',
    'pomp_buffer_get_cdata', 'pomp_buffer_get_data',
    'pomp_buffer_is_shared', 'pomp_buffer_new',
    'pomp_buffer_new_copy', 'pomp_buffer_new_get_data',
    'pomp_buffer_new_with_data', 'pomp_buffer_read',
    'pomp_buffer_ref', 'pomp_buffer_set_capacity',
    'pomp_buffer_set_len', 'pomp_buffer_unref', 'pomp_buffer_write',
    'pomp_conn_disconnect', 'pomp_conn_get_fd',
    'pomp_conn_get_local_addr', 'pomp_conn_get_peer_addr',
    'pomp_conn_get_peer_cred', 'pomp_conn_resume_read',
    'pomp_conn_send', 'pomp_conn_send_msg', 'pomp_conn_send_raw_buf',
    'pomp_conn_sendv', 'pomp_conn_set_read_buffer_len',
    'pomp_conn_suspend_read', 'pomp_ctx_bind', 'pomp_ctx_connect',
    'pomp_ctx_destroy', 'pomp_ctx_get_conn', 'pomp_ctx_get_fd',
    'pomp_ctx_get_local_addr', 'pomp_ctx_get_loop',
    'pomp_ctx_get_next_conn', 'pomp_ctx_listen',
    'pomp_ctx_listen_with_access_mode', 'pomp_ctx_new',
    'pomp_ctx_new_with_loop', 'pomp_ctx_process_fd',
    'pomp_ctx_raw_cb_t', 'pomp_ctx_send', 'pomp_ctx_send_msg',
    'pomp_ctx_send_msg_to', 'pomp_ctx_send_raw_buf',
    'pomp_ctx_send_raw_buf_to', 'pomp_ctx_sendv', 'pomp_ctx_set_raw',
    'pomp_ctx_set_read_buffer_len', 'pomp_ctx_set_send_cb',
    'pomp_ctx_set_socket_cb', 'pomp_ctx_setup_keepalive',
    'pomp_ctx_stop', 'pomp_ctx_wait_and_process', 'pomp_ctx_wakeup',
    'pomp_decoder_adump', 'pomp_decoder_clear',
    'pomp_decoder_destroy', 'pomp_decoder_dump', 'pomp_decoder_init',
    'pomp_decoder_new', 'pomp_decoder_read', 'pomp_decoder_read_buf',
    'pomp_decoder_read_cbuf', 'pomp_decoder_read_cstr',
    'pomp_decoder_read_f32', 'pomp_decoder_read_f64',
    'pomp_decoder_read_fd', 'pomp_decoder_read_i16',
    'pomp_decoder_read_i32', 'pomp_decoder_read_i64',
    'pomp_decoder_read_i8', 'pomp_decoder_read_str',
    'pomp_decoder_read_u16', 'pomp_decoder_read_u32',
    'pomp_decoder_read_u64', 'pomp_decoder_read_u8',
    'pomp_decoder_readv', 'pomp_encoder_clear',
    'pomp_encoder_destroy', 'pomp_encoder_init', 'pomp_encoder_new',
    'pomp_encoder_write', 'pomp_encoder_write_argv',
    'pomp_encoder_write_buf', 'pomp_encoder_write_f32',
    'pomp_encoder_write_f64', 'pomp_encoder_write_fd',
    'pomp_encoder_write_i16', 'pomp_encoder_write_i32',
    'pomp_encoder_write_i64', 'pomp_encoder_write_i8',
    'pomp_encoder_write_str', 'pomp_encoder_write_u16',
    'pomp_encoder_write_u32', 'pomp_encoder_write_u64',
    'pomp_encoder_write_u8', 'pomp_encoder_writev', 'pomp_event',
    'pomp_event_cb_t', 'pomp_event_str', 'pomp_evt_attach_to_loop',
    'pomp_evt_cb_t', 'pomp_evt_clear', 'pomp_evt_destroy',
    'pomp_evt_detach_from_loop', 'pomp_evt_is_attached',
    'pomp_evt_new', 'pomp_evt_signal', 'pomp_fd_event',
    'pomp_fd_event_cb_t', 'pomp_idle_cb_t',
    'pomp_internal_set_loop_impl', 'pomp_internal_set_timer_impl',
    'pomp_loop_add', 'pomp_loop_destroy', 'pomp_loop_get_fd',
    'pomp_loop_has_fd', 'pomp_loop_idle_add',
    'pomp_loop_idle_add_with_cookie', 'pomp_loop_idle_flush',
    'pomp_loop_idle_flush_by_cookie', 'pomp_loop_idle_remove',
    'pomp_loop_idle_remove_by_cookie', 'pomp_loop_impl',
    'pomp_loop_new', 'pomp_loop_process_fd', 'pomp_loop_remove',
    'pomp_loop_update', 'pomp_loop_update2',
    'pomp_loop_wait_and_process', 'pomp_loop_wakeup',
    'pomp_loop_watchdog_disable', 'pomp_loop_watchdog_enable',
    'pomp_msg_adump', 'pomp_msg_clear', 'pomp_msg_destroy',
    'pomp_msg_dump', 'pomp_msg_finish', 'pomp_msg_get_buffer',
    'pomp_msg_get_id', 'pomp_msg_init', 'pomp_msg_new',
    'pomp_msg_new_copy', 'pomp_msg_new_with_buffer', 'pomp_msg_read',
    'pomp_msg_readv', 'pomp_msg_write', 'pomp_msg_write_argv',
    'pomp_msg_writev', 'pomp_prot_decode_msg', 'pomp_prot_destroy',
    'pomp_prot_new', 'pomp_prot_release_msg', 'pomp_send_cb_t',
    'pomp_send_status', 'pomp_socket_cb_t', 'pomp_socket_kind',
    'pomp_socket_kind_str', 'pomp_timer_cb_t', 'pomp_timer_clear',
    'pomp_timer_destroy', 'pomp_timer_impl', 'pomp_timer_new',
    'pomp_timer_set', 'pomp_timer_set_periodic', 'pomp_watchdog_cb_t',
    'size_t', 'ssize_t', 'struct_ProtobufCFieldDescriptor',
    'struct_ProtobufCIntRange', 'struct_ProtobufCMessage',
    'struct_ProtobufCMessageDescriptor',
    'struct_ProtobufCMessageUnknownField',
    'struct__Vmeta__BoundingBox', 'struct__Vmeta__CameraMetadata',
    'struct__Vmeta__DroneMetadata', 'struct__Vmeta__LinkMetadata',
    'struct__Vmeta__Location', 'struct__Vmeta__NED',
    'struct__Vmeta__Quaternion', 'struct__Vmeta__StarfishLinkInfo',
    'struct__Vmeta__StarfishLinkMetadata',
    'struct__Vmeta__TimedMetadata', 'struct__Vmeta__TrackingMetadata',
    'struct__Vmeta__TrackingProposalMetadata',
    'struct__Vmeta__Vector3', 'struct__Vmeta__WifiLinkMetadata',
    'struct___va_list_tag', 'struct_arsdk_arg_desc',
    'struct_arsdk_backend', 'struct_arsdk_backend_listen_cbs',
    'struct_arsdk_backend_mux', 'struct_arsdk_backend_mux_cfg',
    'struct_arsdk_backend_net', 'struct_arsdk_backend_net_cfg',
    'struct_arsdk_binary', 'struct_arsdk_blackbox_itf',
    'struct_arsdk_blackbox_listener',
    'struct_arsdk_blackbox_listener_cbs',
    'struct_arsdk_blackbox_rc_piloting_info', 'struct_arsdk_cmd',
    'struct_arsdk_cmd_desc', 'struct_arsdk_cmd_itf',
    'struct_arsdk_cmd_itf_cbs', 'struct_arsdk_crashml_itf',
    'struct_arsdk_crashml_req', 'struct_arsdk_crashml_req_cbs',
    'struct_arsdk_ctrl', 'struct_arsdk_ctrl_device_cbs',
    'struct_arsdk_device', 'struct_arsdk_device_conn_cbs',
    'struct_arsdk_device_conn_cfg', 'struct_arsdk_device_info',
    'struct_arsdk_device_mngr', 'struct_arsdk_device_tcp_proxy',
    'struct_arsdk_device_tcp_proxy_cbs', 'struct_arsdk_discovery',
    'struct_arsdk_discovery_avahi', 'struct_arsdk_discovery_cfg',
    'struct_arsdk_discovery_device_info',
    'struct_arsdk_discovery_mux', 'struct_arsdk_discovery_net',
    'struct_arsdk_enum_desc', 'struct_arsdk_ephemeris_itf',
    'struct_arsdk_ephemeris_req_upload',
    'struct_arsdk_ephemeris_req_upload_cbs',
    'struct_arsdk_flight_log_itf', 'struct_arsdk_ftp_file',
    'struct_arsdk_ftp_file_list', 'struct_arsdk_ftp_itf',
    'struct_arsdk_ftp_req_delete', 'struct_arsdk_ftp_req_delete_cbs',
    'struct_arsdk_ftp_req_get', 'struct_arsdk_ftp_req_get_cbs',
    'struct_arsdk_ftp_req_list', 'struct_arsdk_ftp_req_list_cbs',
    'struct_arsdk_ftp_req_put', 'struct_arsdk_ftp_req_put_cbs',
    'struct_arsdk_ftp_req_rename', 'struct_arsdk_ftp_req_rename_cbs',
    'struct_arsdk_media', 'struct_arsdk_media_itf',
    'struct_arsdk_media_list', 'struct_arsdk_media_req_delete',
    'struct_arsdk_media_req_delete_cbs',
    'struct_arsdk_media_req_download',
    'struct_arsdk_media_req_download_cbs',
    'struct_arsdk_media_req_list', 'struct_arsdk_media_req_list_cbs',
    'struct_arsdk_media_res', 'struct_arsdk_mngr',
    'struct_arsdk_mngr_peer_cbs', 'struct_arsdk_peer',
    'struct_arsdk_peer_conn_cbs', 'struct_arsdk_peer_conn_cfg',
    'struct_arsdk_peer_info', 'struct_arsdk_publisher_avahi',
    'struct_arsdk_publisher_avahi_cfg', 'struct_arsdk_publisher_cfg',
    'struct_arsdk_publisher_mux', 'struct_arsdk_publisher_net',
    'struct_arsdk_publisher_net_cfg', 'struct_arsdk_pud_itf',
    'struct_arsdk_pud_req', 'struct_arsdk_pud_req_cbs',
    'struct_arsdk_stream_itf', 'struct_arsdk_updater_itf',
    'struct_arsdk_updater_req_upload',
    'struct_arsdk_updater_req_upload_cbs',
    'struct_arsdk_updater_transport', 'struct_arsdk_value',
    'struct_arsdkctrl_backend', 'struct_arsdkctrl_backend_mux',
    'struct_arsdkctrl_backend_mux_cfg',
    'struct_arsdkctrl_backend_net',
    'struct_arsdkctrl_backend_net_cfg', 'struct_egl_display',
    'struct_json_object', 'struct_mbuf_ancillary_data',
    'struct_mbuf_coded_video_frame',
    'struct_mbuf_coded_video_frame_cbs',
    'struct_mbuf_coded_video_frame_queue',
    'struct_mbuf_coded_video_frame_queue_args', 'struct_mbuf_mem',
    'struct_mbuf_mem_implem', 'struct_mbuf_mem_info',
    'struct_mbuf_pool', 'struct_mbuf_raw_video_frame',
    'struct_mbuf_raw_video_frame_cbs',
    'struct_mbuf_raw_video_frame_queue',
    'struct_mbuf_raw_video_frame_queue_args', 'struct_mp4_demux',
    'struct_mp4_hvcc_info', 'struct_mp4_media_info', 'struct_mp4_mux',
    'struct_mp4_mux_sample', 'struct_mp4_mux_scattered_sample',
    'struct_mp4_mux_track_params', 'struct_mp4_track_info',
    'struct_mp4_track_sample', 'struct_mp4_video_decoder_config',
    'struct_mp4_video_decoder_config_0_0',
    'struct_mp4_video_decoder_config_0_1', 'struct_mux_ctx',
    'struct_mux_ip_proxy', 'struct_mux_ip_proxy_cbs',
    'struct_mux_ip_proxy_info', 'struct_mux_ip_proxy_protocol',
    'struct_mux_ops', 'struct_mux_queue', 'struct_pdraw',
    'struct_pdraw_cbs', 'struct_pdraw_coded_video_info',
    'struct_pdraw_coded_video_info_0_0',
    'struct_pdraw_coded_video_info_0_1',
    'struct_pdraw_coded_video_sink',
    'struct_pdraw_coded_video_sink_cbs', 'struct_pdraw_demuxer',
    'struct_pdraw_demuxer_cbs', 'struct_pdraw_demuxer_media',
    'struct_pdraw_media_info', 'struct_pdraw_muxer',
    'struct_pdraw_muxer_video_media_params',
    'struct_pdraw_raw_video_info', 'struct_pdraw_raw_video_sink',
    'struct_pdraw_raw_video_sink_cbs', 'struct_pdraw_rect',
    'struct_pdraw_video_frame', 'struct_pdraw_video_frame_extra',
    'struct_pdraw_video_info', 'struct_pdraw_video_renderer',
    'struct_pdraw_video_renderer_cbs',
    'struct_pdraw_video_renderer_params',
    'struct_pdraw_video_sink_params', 'struct_pomp_buffer',
    'struct_pomp_conn', 'struct_pomp_cred', 'struct_pomp_ctx',
    'struct_pomp_decoder', 'struct_pomp_encoder', 'struct_pomp_evt',
    'struct_pomp_loop', 'struct_pomp_msg', 'struct_pomp_prot',
    'struct_pomp_sockaddr_storage', 'struct_pomp_timer',
    'struct_sockaddr', 'struct_timespec', 'struct_tm',
    'struct_vdef_coded_format', 'struct_vdef_coded_frame',
    'struct_vdef_color_primaries_value',
    'struct_vdef_color_primaries_value_0',
    'struct_vdef_color_primaries_value_1', 'struct_vdef_dim',
    'struct_vdef_format_info', 'struct_vdef_format_info_0',
    'struct_vdef_format_info_1', 'struct_vdef_frac',
    'struct_vdef_frame_info', 'struct_vdef_nalu',
    'struct_vdef_nalu_0_0', 'struct_vdef_nalu_0_1',
    'struct_vdef_raw_format', 'struct_vdef_raw_frame',
    'struct_vdef_rect', 'struct_vmeta_buffer', 'struct_vmeta_euler',
    'struct_vmeta_fov', 'struct_vmeta_frame',
    'struct_vmeta_frame_ext_automation',
    'struct_vmeta_frame_ext_followme',
    'struct_vmeta_frame_ext_thermal',
    'struct_vmeta_frame_ext_timestamp', 'struct_vmeta_frame_proto',
    'struct_vmeta_frame_v1_recording',
    'struct_vmeta_frame_v1_streaming_basic',
    'struct_vmeta_frame_v1_streaming_extended',
    'struct_vmeta_frame_v2', 'struct_vmeta_frame_v2_base',
    'struct_vmeta_frame_v3', 'struct_vmeta_frame_v3_base',
    'struct_vmeta_location', 'struct_vmeta_ned',
    'struct_vmeta_quaternion', 'struct_vmeta_session',
    'struct_vmeta_thermal', 'struct_vmeta_thermal_alignment',
    'struct_vmeta_thermal_conversion', 'struct_vmeta_thermal_spot',
    'struct_vmeta_xyz', 'time_t', 'uint16_t', 'uint32_t', 'uint64_t',
    'uint8_t', 'uint_fast16_t', 'uint_fast32_t', 'uint_fast64_t',
    'uint_fast8_t', 'uint_least16_t', 'uint_least32_t',
    'uint_least64_t', 'uint_least8_t', 'uintmax_t', 'uintptr_t',
    'union__Vmeta__LinkMetadata_0', 'union_arsdk_value_0',
    'union_mp4_video_decoder_config_0',
    'union_mp4_video_decoder_config_0_0_0',
    'union_mp4_video_decoder_config_0_0_1',
    'union_mp4_video_decoder_config_0_1_0',
    'union_mp4_video_decoder_config_0_1_1',
    'union_mp4_video_decoder_config_0_1_2',
    'union_pdraw_coded_video_info_0', 'union_pdraw_media_info_0',
    'union_pdraw_video_frame_0', 'union_pdraw_video_info_0',
    'union_pdraw_video_sink_params_0', 'union_vdef_nalu_0',
    'union_vmeta_buffer_0', 'union_vmeta_euler_0',
    'union_vmeta_euler_1', 'union_vmeta_euler_2',
    'union_vmeta_frame_0', 'va_list', 'vdef_abgr', 'vdef_bayer_bggr',
    'vdef_bayer_bggr_10', 'vdef_bayer_bggr_10_packed',
    'vdef_bayer_bggr_12', 'vdef_bayer_bggr_12_packed',
    'vdef_bayer_bggr_14', 'vdef_bayer_bggr_14_packed',
    'vdef_bayer_gbrg', 'vdef_bayer_gbrg_10',
    'vdef_bayer_gbrg_10_packed', 'vdef_bayer_gbrg_12',
    'vdef_bayer_gbrg_12_packed', 'vdef_bayer_gbrg_14',
    'vdef_bayer_gbrg_14_packed', 'vdef_bayer_grbg',
    'vdef_bayer_grbg_10', 'vdef_bayer_grbg_10_packed',
    'vdef_bayer_grbg_12', 'vdef_bayer_grbg_12_packed',
    'vdef_bayer_grbg_14', 'vdef_bayer_grbg_14_packed',
    'vdef_bayer_rggb', 'vdef_bayer_rggb_10',
    'vdef_bayer_rggb_10_packed', 'vdef_bayer_rggb_12',
    'vdef_bayer_rggb_12_packed', 'vdef_bayer_rggb_14',
    'vdef_bayer_rggb_14_packed', 'vdef_bgr', 'vdef_bgra',
    'vdef_bt2020_to_bt709_matrix', 'vdef_bt709_to_bt2020_matrix',
    'vdef_calc_raw_contiguous_frame_size', 'vdef_calc_raw_frame_size',
    'vdef_coded_data_format', 'vdef_coded_data_format_from_str',
    'vdef_coded_data_format_to_str', 'vdef_coded_format_cmp',
    'vdef_coded_format_from_csv', 'vdef_coded_format_from_str',
    'vdef_coded_format_intersect', 'vdef_coded_format_to_csv',
    'vdef_coded_format_to_str', 'vdef_coded_frame_type',
    'vdef_coded_frame_type_from_str', 'vdef_coded_frame_type_to_str',
    'vdef_color_primaries', 'vdef_color_primaries_from_h264',
    'vdef_color_primaries_from_h265', 'vdef_color_primaries_from_str',
    'vdef_color_primaries_from_values',
    'vdef_color_primaries_to_h264', 'vdef_color_primaries_to_h265',
    'vdef_color_primaries_to_str', 'vdef_color_primaries_values',
    'vdef_dim_cmp', 'vdef_dim_is_aligned', 'vdef_dim_is_null',
    'vdef_dynamic_range', 'vdef_dynamic_range_from_str',
    'vdef_dynamic_range_to_str', 'vdef_encoding',
    'vdef_encoding_from_str', 'vdef_encoding_to_str',
    'vdef_format_info_from_csv', 'vdef_format_info_to_csv',
    'vdef_format_info_to_json', 'vdef_format_to_frame_info',
    'vdef_frac_diff', 'vdef_frac_is_null', 'vdef_frame_flag',
    'vdef_frame_info_to_json', 'vdef_frame_to_format_info',
    'vdef_frame_type', 'vdef_frame_type_from_str',
    'vdef_frame_type_to_str', 'vdef_get_encoding_mime_type',
    'vdef_get_raw_frame_plane_count', 'vdef_gray', 'vdef_gray16',
    'vdef_h264_avcc', 'vdef_h264_byte_stream', 'vdef_h264_raw_nalu',
    'vdef_h265_byte_stream', 'vdef_h265_hvcc', 'vdef_h265_raw_nalu',
    'vdef_i420', 'vdef_i420_10_16be', 'vdef_i420_10_16be_high',
    'vdef_i420_10_16le', 'vdef_i420_10_16le_high',
    'vdef_is_coded_format_valid', 'vdef_is_raw_format_valid',
    'vdef_jpeg_jfif', 'vdef_matrix_coefs',
    'vdef_matrix_coefs_from_h264', 'vdef_matrix_coefs_from_h265',
    'vdef_matrix_coefs_from_str', 'vdef_matrix_coefs_to_h264',
    'vdef_matrix_coefs_to_h265', 'vdef_matrix_coefs_to_str',
    'vdef_mmal_opaque', 'vdef_nv12', 'vdef_nv12_10_16be',
    'vdef_nv12_10_16be_high', 'vdef_nv12_10_16le',
    'vdef_nv12_10_16le_high', 'vdef_nv12_10_packed', 'vdef_nv21',
    'vdef_nv21_10_16be', 'vdef_nv21_10_16be_high',
    'vdef_nv21_10_16le', 'vdef_nv21_10_16le_high',
    'vdef_nv21_10_packed', 'vdef_nv21_hisi_tile',
    'vdef_nv21_hisi_tile_10_packed', 'vdef_nv21_hisi_tile_compressed',
    'vdef_nv21_hisi_tile_compressed_10_packed', 'vdef_raw10',
    'vdef_raw10_packed', 'vdef_raw12', 'vdef_raw12_packed',
    'vdef_raw14', 'vdef_raw14_packed', 'vdef_raw16', 'vdef_raw32',
    'vdef_raw8', 'vdef_raw_data_layout',
    'vdef_raw_data_layout_from_str', 'vdef_raw_data_layout_to_str',
    'vdef_raw_format_cmp', 'vdef_raw_format_from_csv',
    'vdef_raw_format_from_str', 'vdef_raw_format_intersect',
    'vdef_raw_format_to_csv', 'vdef_raw_format_to_str',
    'vdef_raw_pix_format', 'vdef_raw_pix_format_from_str',
    'vdef_raw_pix_format_to_str', 'vdef_raw_pix_layout',
    'vdef_raw_pix_layout_from_str', 'vdef_raw_pix_layout_to_str',
    'vdef_raw_pix_order', 'vdef_raw_pix_order_from_str',
    'vdef_raw_pix_order_to_str', 'vdef_rect_align', 'vdef_rect_cmp',
    'vdef_rect_fit', 'vdef_rect_is_aligned', 'vdef_rgb',
    'vdef_rgb_to_yuv_norm_matrix', 'vdef_rgb_to_yuv_norm_offset',
    'vdef_rgba', 'vdef_tone_mapping', 'vdef_tone_mapping_from_str',
    'vdef_tone_mapping_to_str', 'vdef_transfer_function',
    'vdef_transfer_function_from_h264',
    'vdef_transfer_function_from_h265',
    'vdef_transfer_function_from_str',
    'vdef_transfer_function_to_h264',
    'vdef_transfer_function_to_h265', 'vdef_transfer_function_to_str',
    'vdef_yuv_to_rgb_norm_matrix', 'vdef_yuv_to_rgb_norm_offset',
    'vdef_yv12', 'vdef_yv12_10_16be', 'vdef_yv12_10_16be_high',
    'vdef_yv12_10_16le', 'vdef_yv12_10_16le_high',
    'vmeta_automation_anim', 'vmeta_automation_anim_str',
    'vmeta_buffer_set_cdata', 'vmeta_buffer_set_data',
    'vmeta_camera_type', 'vmeta_camera_type_from_str',
    'vmeta_camera_type_to_str', 'vmeta_dynamic_range',
    'vmeta_dynamic_range_from_str', 'vmeta_dynamic_range_to_str',
    'vmeta_euler_to_quat', 'vmeta_flying_state',
    'vmeta_flying_state_str', 'vmeta_followme_anim',
    'vmeta_followme_anim_str', 'vmeta_frame_csv_header',
    'vmeta_frame_flying_state_proto_to_vmeta',
    'vmeta_frame_get_air_speed', 'vmeta_frame_get_awb_b_gain',
    'vmeta_frame_get_awb_r_gain',
    'vmeta_frame_get_battery_percentage',
    'vmeta_frame_get_camera_pan', 'vmeta_frame_get_camera_tilt',
    'vmeta_frame_get_drone_euler', 'vmeta_frame_get_drone_quat',
    'vmeta_frame_get_exposure_time', 'vmeta_frame_get_flying_state',
    'vmeta_frame_get_frame_base_euler',
    'vmeta_frame_get_frame_base_quat', 'vmeta_frame_get_frame_euler',
    'vmeta_frame_get_frame_quat', 'vmeta_frame_get_frame_timestamp',
    'vmeta_frame_get_gain', 'vmeta_frame_get_ground_distance',
    'vmeta_frame_get_link_goodput', 'vmeta_frame_get_link_quality',
    'vmeta_frame_get_location', 'vmeta_frame_get_mime_type',
    'vmeta_frame_get_picture_h_fov', 'vmeta_frame_get_picture_v_fov',
    'vmeta_frame_get_piloting_mode', 'vmeta_frame_get_ref_count',
    'vmeta_frame_get_speed_ned', 'vmeta_frame_get_wifi_rssi',
    'vmeta_frame_new', 'vmeta_frame_proto_add_starfish_link',
    'vmeta_frame_proto_add_starfish_link_info',
    'vmeta_frame_proto_add_wifi_link', 'vmeta_frame_proto_get_buffer',
    'vmeta_frame_proto_get_camera',
    'vmeta_frame_proto_get_camera_base_quat',
    'vmeta_frame_proto_get_camera_quat',
    'vmeta_frame_proto_get_drone',
    'vmeta_frame_proto_get_drone_local_position',
    'vmeta_frame_proto_get_drone_location',
    'vmeta_frame_proto_get_drone_position',
    'vmeta_frame_proto_get_drone_quat',
    'vmeta_frame_proto_get_drone_speed',
    'vmeta_frame_proto_get_packed_size',
    'vmeta_frame_proto_get_proposal',
    'vmeta_frame_proto_get_tracking',
    'vmeta_frame_proto_get_tracking_target',
    'vmeta_frame_proto_get_unpacked',
    'vmeta_frame_proto_get_unpacked_rw',
    'vmeta_frame_proto_proposal_add_box',
    'vmeta_frame_proto_release_buffer',
    'vmeta_frame_proto_release_unpacked',
    'vmeta_frame_proto_release_unpacked_rw', 'vmeta_frame_read',
    'vmeta_frame_ref', 'vmeta_frame_to_csv', 'vmeta_frame_to_json',
    'vmeta_frame_to_json_str', 'vmeta_frame_type',
    'vmeta_frame_type_str', 'vmeta_frame_unref',
    'vmeta_frame_v1_recording_csv_header',
    'vmeta_frame_v1_recording_read',
    'vmeta_frame_v1_recording_to_csv',
    'vmeta_frame_v1_recording_to_json',
    'vmeta_frame_v1_recording_write',
    'vmeta_frame_v1_streaming_basic_csv_header',
    'vmeta_frame_v1_streaming_basic_read',
    'vmeta_frame_v1_streaming_basic_to_csv',
    'vmeta_frame_v1_streaming_basic_to_json',
    'vmeta_frame_v1_streaming_basic_write',
    'vmeta_frame_v1_streaming_extended_csv_header',
    'vmeta_frame_v1_streaming_extended_read',
    'vmeta_frame_v1_streaming_extended_to_csv',
    'vmeta_frame_v1_streaming_extended_to_json',
    'vmeta_frame_v1_streaming_extended_write',
    'vmeta_frame_v2_csv_header', 'vmeta_frame_v2_read',
    'vmeta_frame_v2_to_csv', 'vmeta_frame_v2_to_json',
    'vmeta_frame_v2_write', 'vmeta_frame_v3_csv_header',
    'vmeta_frame_v3_read', 'vmeta_frame_v3_to_csv',
    'vmeta_frame_v3_to_json', 'vmeta_frame_v3_write',
    'vmeta_frame_write', 'vmeta_piloting_mode',
    'vmeta_piloting_mode_str', 'vmeta_quat_to_euler',
    'vmeta_record_type', 'vmeta_session_date_read',
    'vmeta_session_date_write', 'vmeta_session_fov_read',
    'vmeta_session_fov_write', 'vmeta_session_location_format',
    'vmeta_session_location_read', 'vmeta_session_location_write',
    'vmeta_session_recording_read', 'vmeta_session_recording_write',
    'vmeta_session_recording_write_cb_t',
    'vmeta_session_streaming_sdes_read',
    'vmeta_session_streaming_sdes_write',
    'vmeta_session_streaming_sdes_write_cb_t',
    'vmeta_session_streaming_sdp_read',
    'vmeta_session_streaming_sdp_write',
    'vmeta_session_streaming_sdp_write_cb_t',
    'vmeta_session_thermal_alignment_read',
    'vmeta_session_thermal_alignment_write',
    'vmeta_session_thermal_conversion_read',
    'vmeta_session_thermal_conversion_write',
    'vmeta_session_thermal_scale_factor_read',
    'vmeta_session_thermal_scale_factor_write',
    'vmeta_session_to_json', 'vmeta_session_to_str',
    'vmeta_stream_sdes_type', 'vmeta_stream_sdp_type',
    'vmeta_thermal_calib_state', 'vmeta_thermal_calib_state_str',
    'vmeta_tone_mapping', 'vmeta_tone_mapping_from_str',
    'vmeta_tone_mapping_to_str', 'vmeta_video_mode',
    'vmeta_video_mode_from_str', 'vmeta_video_mode_to_str',
    'vmeta_video_stop_reason', 'vmeta_video_stop_reason_from_str',
    'vmeta_video_stop_reason_to_str']
