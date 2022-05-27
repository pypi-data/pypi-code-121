# -*- coding: utf-8 -*-
#
# TARGET arch is: x86_64
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes

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

_libraries['libulog.so'] = _load_library('libulog.so')



_PARROT_ULOG_H = True # macro
# ULOG_THREAD = __thread # macro
ULOG_USE_TLS = (1) # macro

# macro function ULOG_DECLARE_TAG
ULOG_CRIT = (2) # macro
ULOG_ERR = (3) # macro
ULOG_WARN = (4) # macro
ULOG_NOTICE = (5) # macro
ULOG_INFO = (6) # macro
ULOG_DEBUG = (7) # macro

# macro function ULOGC

# macro function ULOGE

# macro function ULOGW

# macro function ULOGN

# macro function ULOGI

# macro function ULOGD

# macro function ULOGC_ERRNO

# macro function ULOGE_ERRNO

# macro function ULOGW_ERRNO

# macro function ULOGN_ERRNO

# macro function ULOGI_ERRNO

# macro function ULOGD_ERRNO

# macro function ULOG_ERRNO

# macro function ULOG_ERRNO_RETURN_IF

# macro function ULOG_ERRNO_RETURN_ERR_IF

# macro function ULOG_ERRNO_RETURN_VAL_IF

# macro function ULOG_EVT

# macro function ULOG_EVTS
ULOG_BUF_SIZE = (256) # macro

# macro function ULOGC_THROTTLE

# macro function ULOGE_THROTTLE

# macro function ULOGW_THROTTLE

# macro function ULOGN_THROTTLE

# macro function ULOGI_THROTTLE

# macro function ULOGD_THROTTLE

# macro function ULOGC_CHANGE

# macro function ULOGE_CHANGE

# macro function ULOGW_CHANGE

# macro function ULOGN_CHANGE

# macro function ULOGI_CHANGE

# macro function ULOGD_CHANGE

# macro function ULOG_SET_LEVEL

# macro function ULOG_GET_LEVEL

# macro function ULOG_INIT

# macro function ULOG_PRI

# macro function ULOG_PRI_VA

# macro function ULOG_PRI_ERRNO

# macro function ULOG_STR

# macro function ULOG_BUF

# macro function ULOG_BIN
ULOG_PRIO_LEVEL_MASK = (7) # macro
ULOG_PRIO_BINARY_SHIFT = (7) # macro
ULOG_PRIO_COLOR_SHIFT = (8) # macro

# macro function __ULOG_REF

# macro function __ULOG_REF2

# macro function __ULOG_DECL

# macro function __ULOG_DECLARE_TAG

# macro function __ULOG_USE_TAG
# __ULOG_COOKIE = __ulog_default_cookie # macro

# macro function ULOG_UNLIKELY

# macro function ulog_vlog

# macro function ulog_log

# macro function ULOG_THROTTLE

# macro function ulog_log_throttle

# macro function ULOG_CHANGE

# macro function ULOG_DECLARE_CHANGE_STATE_INT

# macro function ULOG_INIT_CHANGE_STATE_INT

# macro function ulog_log_change
ulog_set_tag_level = _libraries['libulog.so'].ulog_set_tag_level
ulog_set_tag_level.restype = ctypes.c_int32
ulog_set_tag_level.argtypes = [POINTER_T(ctypes.c_char), ctypes.c_int32]
ulog_get_tag_names = _libraries['libulog.so'].ulog_get_tag_names
ulog_get_tag_names.restype = ctypes.c_int32
ulog_get_tag_names.argtypes = [POINTER_T(POINTER_T(ctypes.c_char)), ctypes.c_int32]
ulog_get_time_monotonic = _libraries['libulog.so'].ulog_get_time_monotonic
ulog_get_time_monotonic.restype = ctypes.c_int32
ulog_get_time_monotonic.argtypes = [POINTER_T(ctypes.c_uint64)]
class struct_ulog_cookie(Structure):
    pass

struct_ulog_cookie._pack_ = True # source:False
struct_ulog_cookie._fields_ = [
    ('name', POINTER_T(ctypes.c_char)),
    ('namesize', ctypes.c_int32),
    ('level', ctypes.c_int32),
    ('userdata', POINTER_T(None)),
    ('next', POINTER_T(struct_ulog_cookie)),
]

__ulog_default_cookie = (struct_ulog_cookie).in_dll(_libraries['libulog.so'], '__ulog_default_cookie')
ulog_init_cookie = _libraries['libulog.so'].ulog_init_cookie
ulog_init_cookie.restype = None
ulog_init_cookie.argtypes = [POINTER_T(struct_ulog_cookie)]
uint32_t = ctypes.c_uint32
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
ulog_vlog_write = _libraries['libulog.so'].ulog_vlog_write
ulog_vlog_write.restype = None
ulog_vlog_write.argtypes = [uint32_t, POINTER_T(struct_ulog_cookie), POINTER_T(ctypes.c_char), va_list]
ulog_log_write = _libraries['libulog.so'].ulog_log_write
ulog_log_write.restype = None
ulog_log_write.argtypes = [uint32_t, POINTER_T(struct_ulog_cookie), POINTER_T(ctypes.c_char)]
ulog_log_buf = _libraries['libulog.so'].ulog_log_buf
ulog_log_buf.restype = None
ulog_log_buf.argtypes = [uint32_t, POINTER_T(struct_ulog_cookie), POINTER_T(None), ctypes.c_int32]
ulog_log_str = _libraries['libulog.so'].ulog_log_str
ulog_log_str.restype = None
ulog_log_str.argtypes = [uint32_t, POINTER_T(struct_ulog_cookie), POINTER_T(ctypes.c_char)]
ulog_init = _libraries['libulog.so'].ulog_init
ulog_init.restype = None
ulog_init.argtypes = [POINTER_T(struct_ulog_cookie)]
ulog_set_level = _libraries['libulog.so'].ulog_set_level
ulog_set_level.restype = None
ulog_set_level.argtypes = [POINTER_T(struct_ulog_cookie), ctypes.c_int32]
ulog_get_level = _libraries['libulog.so'].ulog_get_level
ulog_get_level.restype = ctypes.c_int32
ulog_get_level.argtypes = [POINTER_T(struct_ulog_cookie)]
ulog_write_func_t = ctypes.CFUNCTYPE(None, ctypes.c_uint32, POINTER_T(struct_ulog_cookie), POINTER_T(ctypes.c_char), ctypes.c_int32)
ulog_set_write_func = _libraries['libulog.so'].ulog_set_write_func
ulog_set_write_func.restype = ctypes.c_int32
ulog_set_write_func.argtypes = [ulog_write_func_t]
ulog_get_write_func = _libraries['libulog.so'].ulog_get_write_func
ulog_get_write_func.restype = ulog_write_func_t
ulog_get_write_func.argtypes = []
ulog_cookie_register_func_t = ctypes.CFUNCTYPE(None, POINTER_T(struct_ulog_cookie))
ulog_set_cookie_register_func = _libraries['libulog.so'].ulog_set_cookie_register_func
ulog_set_cookie_register_func.restype = ctypes.c_int32
ulog_set_cookie_register_func.argtypes = [ulog_cookie_register_func_t]
ulog_foreach = _libraries['libulog.so'].ulog_foreach
ulog_foreach.restype = ctypes.c_int32
ulog_foreach.argtypes = [ctypes.CFUNCTYPE(None, POINTER_T(struct_ulog_cookie), POINTER_T(None)), POINTER_T(None)]
_PARROT_ULOGRAW_H = True # macro
class struct_ulogger_entry(Structure):
    pass

struct_ulogger_entry._pack_ = True # source:False
struct_ulogger_entry._fields_ = [
    ('len', ctypes.c_uint16),
    ('hdr_size', ctypes.c_uint16),
    ('pid', ctypes.c_int32),
    ('tid', ctypes.c_int32),
    ('sec', ctypes.c_int32),
    ('nsec', ctypes.c_int32),
    ('euid', ctypes.c_int32),
    ('msg', ctypes.c_char * 0),
]

class struct_ulog_raw_entry(Structure):
    pass

struct_ulog_raw_entry._pack_ = True # source:False
struct_ulog_raw_entry._fields_ = [
    ('entry', struct_ulogger_entry),
    ('prio', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pname', POINTER_T(ctypes.c_char)),
    ('tname', POINTER_T(ctypes.c_char)),
    ('tag', POINTER_T(ctypes.c_char)),
    ('message', POINTER_T(ctypes.c_char)),
    ('pname_len', ctypes.c_uint32),
    ('tname_len', ctypes.c_uint32),
    ('tag_len', ctypes.c_uint32),
    ('message_len', ctypes.c_uint32),
]

ulog_raw_open = _libraries['libulog.so'].ulog_raw_open
ulog_raw_open.restype = ctypes.c_int32
ulog_raw_open.argtypes = [POINTER_T(ctypes.c_char)]
ulog_raw_close = _libraries['libulog.so'].ulog_raw_close
ulog_raw_close.restype = None
ulog_raw_close.argtypes = [ctypes.c_int32]
ulog_raw_log = _libraries['libulog.so'].ulog_raw_log
ulog_raw_log.restype = ctypes.c_int32
ulog_raw_log.argtypes = [ctypes.c_int32, POINTER_T(struct_ulog_raw_entry)]
class struct_iovec(Structure):
    pass

struct_iovec._pack_ = True # source:False
struct_iovec._fields_ = [
    ('iov_base', POINTER_T(None)),
    ('iov_len', ctypes.c_uint64),
]

ulog_raw_logv = _libraries['libulog.so'].ulog_raw_logv
ulog_raw_logv.restype = ctypes.c_int32
ulog_raw_logv.argtypes = [ctypes.c_int32, POINTER_T(struct_ulog_raw_entry), POINTER_T(struct_iovec), ctypes.c_int32]

__all__ = \
    ['ULOG_BUF_SIZE', 'ULOG_CRIT', 'ULOG_DEBUG', 'ULOG_ERR',
    'ULOG_INFO', 'ULOG_NOTICE', 'ULOG_PRIO_BINARY_SHIFT',
    'ULOG_PRIO_COLOR_SHIFT', 'ULOG_PRIO_LEVEL_MASK', 'ULOG_USE_TLS',
    'ULOG_WARN', '_PARROT_ULOGRAW_H', '_PARROT_ULOG_H',
    '__ulog_default_cookie', 'struct___va_list_tag', 'struct_iovec',
    'struct_ulog_cookie', 'struct_ulog_raw_entry',
    'struct_ulogger_entry', 'uint32_t', 'ulog_cookie_register_func_t',
    'ulog_foreach', 'ulog_get_level', 'ulog_get_tag_names',
    'ulog_get_time_monotonic', 'ulog_get_write_func', 'ulog_init',
    'ulog_init_cookie', 'ulog_log_buf', 'ulog_log_str',
    'ulog_log_write', 'ulog_raw_close', 'ulog_raw_log',
    'ulog_raw_logv', 'ulog_raw_open', 'ulog_set_cookie_register_func',
    'ulog_set_level', 'ulog_set_tag_level', 'ulog_set_write_func',
    'ulog_vlog_write', 'ulog_write_func_t', 'va_list']
