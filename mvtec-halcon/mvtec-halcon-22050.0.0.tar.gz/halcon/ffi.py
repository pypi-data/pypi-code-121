"""
************************************************************
ffi.py - wrapper for HALCON LI functions
************************************************************

Project: HALCON/Python

Description:
Handles ALL FFI and related error handling.

HALCON API
  ^
  | FFI (Foreign Function Interface)
  v
 HLI (Halcon Language Interface C Library)
  ^
  | C calls
  v
HALCON (Halcon C Library)

HLI and HALCON are both inside the halcon shared library.

************************************************************

(c) 1996-2020 by MVTec Software GmbH

Software by: MVTec Software GmbH, www.mvtec.com
"""

import ctypes
import os
import sys

from typing import Sequence, Final, Union, Optional, Dict, Any, cast

from . import mixin

from .util import MaybeSequence
from .meta import halcon_native_lib_names, expected_halcon_version

import halcon

__all__ = [
    'get_sem_type',
    'H_MSG_FAIL',
    'H_MSG_OK',
    'HalconOperator',
    'HCkP',
    'Herror',
    'HError',
    'HHandleBase',
    'Hkey',
    'HNull',
    'HObjectBase',
    'HOperatorError',
    'HTupleConversionError',
    'HTupleElementType',
    'HTupleType',
    'make_c_func_prototype',
]


# --- Exported Classes ---


class HError(Exception):
    """HALCON base exception."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message


class HOperatorError(HError):
    """HALCON operator exception."""

    def __init__(self, error_code: int):
        self.error_code = error_code
        self.message = _get_error_text(error_code)
        self.extended_error_message = ''

    def __str__(self) -> str:
        if self.extended_error_message == '':
            return self.message

        return f'{self.message}: {self.extended_error_message}'

    def _update_extended_info(self) -> None:
        try:
            _, extended_code, extended_msg = halcon.get_extended_error_info()
            self.extended_error_code = extended_code
            self.extended_error_message = extended_msg
        except HOperatorError as exc:
            sys.stderr.write(
                '[WARNING] failed to call get_extended_error_info: '
                f'{exc}'
            )


class HTupleConversionError(HError):
    """HALCON tuple conversion exception."""
    pass


class HHandleBase(object):
    """
    HALCON handle base class.

    Interface only creates derived object instances.
    """

    def __init__(self, handle_ptr: ctypes.c_void_p):
        """Initialize HALCON handle from valid pointer."""
        self._handle_ptr = ctypes.c_void_p()
        HCkP(_halcon_lib.HLICopyHandle(
            handle_ptr,
            ctypes.byref(self._handle_ptr)
        ))

    def __del__(self) -> None:
        HCkP(_halcon_lib.HLIClearHandle(self._handle_ptr))


# TODO what should and what shouldn't be valid with HNull?
class HNull(HHandleBase):
    """HALCON HNULL handle class."""
    def __init__(self):
        self._handle_ptr = ctypes.c_void_p(0)

    def __del__(self) -> None:
        pass

    def __eq__(self, other: Any) -> bool:
        # HNull has no state.
        return isinstance(other, HNull)


# --- Type Definitions ---

# Defines type aliases for HALCON types used internally and in the interface.

HTupleElementType = Union[int, float, str, HHandleBase]
HTupleType = Union[HTupleElementType, Sequence[HTupleElementType]]

# Keep in sync with C definitions.
Herror = ctypes.c_uint32
# Technically long* on C side. But since we never intend to look at or modify
# the value on Python side. c_void_p is simpler than byref(c_long).
Hkey = ctypes.c_void_p

# TODO automatic constant and error code generation.
H_MSG_OK = 2
H_MSG_FAIL = 5


class HObjectBase(object):
    """
    HALCON iconic object base class.

    Interface only creates derived object instances.
    """

    def __init__(
        self,
        iconic_objects: Union[Hkey, MaybeSequence['HObjectBase']]
    ):
        """
        Construct based on key or concatenate list of iconic objects.

        Notes
        -----
        This constructor serves dual purpose, one internal for raw keys

        And one public one, for making owning copies or iconic objects,
        optionally concatenating a list of iconic objects.

        This probably does not perform pixel level copies, the implementation
        uses ref counting and other techniques to avoid expensive copies.

        Examples
        --------
        img_copy = HObject(img1)
        img_seq = HObject([img1, img2, img3])
        """
        if isinstance(iconic_objects, Hkey):
            self._key = iconic_objects
        else:
            if isinstance(iconic_objects, (list, set)):
                new_obj = mixin.upcast_obj_list(iconic_objects)
            else:
                new_obj = iconic_objects

            self._key = self._copy_key(new_obj._key)

    def __del__(self) -> None:
        """
        Cleans up associated native resources.

        Notes
        -----
        This might be a simple ref count decrease or some more expensive
        operation.
        """
        HCkP(_halcon_lib.HLIClearObject(self._key))

    @staticmethod
    def _copy_key(from_key: Hkey) -> Hkey:
        """Ref count increasing copy of iconic object key."""
        cloned_key = Hkey()
        HCkP(_halcon_lib.HLICopyObject(
            from_key,
            ctypes.byref(cloned_key)
        ))
        return cloned_key


class HalconOperator(object):
    """
    HALCON operator.

    Facilitates setting up, and calling operators.
    Manages proc_handle lifetime via context manager.

    Typical call order:
    __init__
    __enter__
    set_input_object x N
    set_input_tuple x N
    init_oct x N
    execute
    get_output_object_key x N
    get_output_tuple(_s/_m) x N
    __exit__
    """
    def __init__(self, operator_id: int):
        """Create procedure handle based on operator id."""
        assert _is_valid_i32(operator_id)
        self.proc_handle = ctypes.c_ssize_t()

        # Does not call destroy when create fails.
        HCkP(_halcon_lib.HLICreateProcedure(
            ctypes.c_int32(operator_id),
            ctypes.byref(self.proc_handle)
        ))

    def set_input_object(
        self,
        par_index: int,
        input_object: HObjectBase
    ) -> None:
        """Set procedure iconic input object."""
        # Assumes input_object private _key field was not modified by user.
        HCkP(_halcon_lib.HLISetInputObject(
            self.proc_handle,
            ctypes.c_int32(par_index),
            input_object._key
        ))

    def set_input_tuple(
        self,
        par_index: int,
        value: HTupleType
    ) -> None:
        """Set procedure control input tuple."""
        tuple_ptr = ctypes.c_ssize_t()
        HCkP(_halcon_lib.HLIGetInputTuple(
            self.proc_handle,
            ctypes.c_int32(par_index),
            ctypes.byref(tuple_ptr)
        ))
        _python_to_htuple(tuple_ptr, value)

    def init_oct(self, par_index: int) -> None:
        """Initialize output control tuple."""
        # TODO extend HLI to allow init multiple at once,
        # to avoid FFI roundtrips.
        HCkP(_halcon_lib.HLIInitOCT(
            self.proc_handle,
            ctypes.c_int32(par_index)
        ))

    def execute(self) -> None:
        """Execute procedure."""
        HCkP(_halcon_lib.HLICallProcedure(self.proc_handle))

    def get_output_object_key(self, par_index: int) -> Hkey:
        """Return procedure iconic output object key."""
        output_key = Hkey()
        HCkP(_halcon_lib.HLIGetOutputObject(
            self.proc_handle,
            ctypes.c_int32(par_index),
            ctypes.byref(output_key)
        ))
        return output_key

    def get_output_tuple_s(
        self,
        par_index: int
    ) -> HTupleElementType:
        """Return procedure control output tuple, as single value."""
        output_tuple_ptr = self._get_output_tuple_ptr(par_index)
        if output_tuple_ptr.value == 0:
            raise HTupleConversionError(
                'Expected exactly one tuple value, got 0.'
            )

        # Type checking disabled because we know it's a single value,
        # based on as_list False.
        return _htuple_to_python(output_tuple_ptr, False)  # type: ignore

    def get_output_tuple_m(
        self,
        par_index: int
    ) -> Sequence[HTupleElementType]:
        """Return procedure control output tuple, as list."""
        output_tuple_ptr = self._get_output_tuple_ptr(par_index)
        if output_tuple_ptr.value == 0:
            return []

        # Type checking disabled because we know it's a list,
        # based on as_list True.
        return _htuple_to_python(output_tuple_ptr, True)  # type: ignore

    def _get_output_tuple_ptr(self, par_index: int) -> ctypes.c_ssize_t:
        output_tuple_ptr = ctypes.c_ssize_t()
        HCkP(_halcon_lib.HLIGetOutputTuple(
            self.proc_handle,
            ctypes.c_int32(par_index),
            True,  # handle_type True == not legacy
            ctypes.byref(output_tuple_ptr)
        ))

        # assert output_tuple_ptr.value != 0
        return output_tuple_ptr

    def __enter__(self) -> 'HalconOperator':
        return self

    # Type checking disabled because the parameters are not user provided.
    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        """Destroy procedure handle, later use is UB."""
        # HDeleteHProc on the C side is severely underspecified, it's not
        # entirely clear what should happen if something goes wrong before the
        # procedure was called. The C++ interface passes the received Herror
        # into HDeleteHProc, if for example a tuple allocation fails. But what
        # if a python value could not be converted to a HALCON tuple? Then no
        # Herror exists, but the procedure still needs to be cleaned up.
        # A coarse analysis of HDeleteHProc and it's transitive function shows
        # that if the value is set to H_MSG_OK, associated functionality gets
        # mostly ignored. And it should be fine.

        proc_result = exc_value.error_code \
            if exc_type == HOperatorError else 2  # C H_MSG_OK

        HCkP(_halcon_lib.HLIClearAllIOCT(self.proc_handle))
        # TODO maybe only if already called and has proc_result.
        HCkP(_halcon_lib.HLIDestroyProcedure(
            self.proc_handle,
            # TODO more research is needed here, it's still unclear if this
            # isn't wrong.
            ctypes.c_int32(proc_result)
        ))

        if exc_type == HOperatorError:
            # Has to happen after HLIDestroyProcedure.
            exc_value._update_extended_info()


# --- Exported Functions ---


def HCkP(error_code: int) -> None:
    """Check the error number and raise exception if no ok."""
    if error_code != 2:  # C constant H_MSG_OK
        raise HOperatorError(error_code)


# Expects caller to call with valid handle.
def get_sem_type(handle_ptr: ctypes.c_void_p) -> str:
    out_string = ctypes.c_char_p()
    HCkP(_halcon_lib.HLIGetHandleSemType(handle_ptr, ctypes.byref(out_string)))
    if out_string.value is None:
        return 'hnull'

    return out_string.value.decode('utf-8')


# Load dynamic HALCON library. The name of the library to load depends on the
# operating system. Open with RTLD_GLOBAL on Linux and macOS so that other
# HALCON components like acquisition interfaces can find the HALCON symbols.
def load_native_lib(names: Dict[str, str]) -> ctypes.CDLL:
    # See sys.startswith docs for explanation about startswith pattern.
    if sys.platform.startswith('linux'):
        name = names['linux']
    elif sys.platform.startswith('darwin'):
        name = names['darwin']
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        name = names['win']
    else:
        raise HError(f'Unsupported operating system {sys.platform}')

    lib = _dlopen(name)

    return lib


def make_c_func_prototype(restype, *argtypes):
    if _is_32bit_win:
        return ctypes.WINFUNCTYPE(restype, *argtypes)

    return ctypes.CFUNCTYPE(restype, *argtypes)


# --- Private Implementation Details ---

_is_32bit_win = os.name == 'nt' and sys.maxsize == (2**31 - 1)


def _dlopen(name) -> ctypes.CDLL:
    # Python 3.8 added the winmode parameter. If it is not specified, Python
    # will attempt to open the DLL using LoadLibraryEx's
    # LOAD_LIBRARY_SEARCH_DEFAULT_DIRS mode, which does not take the PATH
    # environment variable into account. Since we expect the user to specify
    # the location of the HALCON libraries to load via the PATH environment
    # variable, that is not what we want, and we must specify winmode=0. Note
    # the Python 3.8 documentation is incorrect and claims winmode=0 is the
    # default; it is not.
    lib = ctypes.CDLL(name, mode=ctypes.RTLD_GLOBAL, winmode=0)

    if lib is None:
        raise HError(f'Failed to load {name} library')

    return lib


def _is_compatible_version(got: str) -> bool:
    return got.rpartition('.')[0] == expected_halcon_version.rpartition('.')[0]


def _is_compatible_mac_version(got: str) -> bool:
    # Mac HALCON_FRAMEWORK_VERSION eg 21.11P(progress) 21.11(steady)
    return got.replace('P', '') == expected_halcon_version.replace('P', '')


def _halcon_version_to_semver(version: str) -> str:
    return version.replace('.', '')


def _log_compatibility_warning(version: str):
    package_version = _halcon_version_to_semver(version)
    sys.stderr.write(
        '[WARNING] Wrong interface package version.\n'
        f'Expected {expected_halcon_version} but found {version}\n'
        'Compatibility is not guaranteed and crashes etc. are possible.\n'
        'Please install the matching interface package version: '
        f'"mvtec-halcon=={package_version}"\n'
    )


def _incompatible_versions(potential_version: str) -> str:
    package_version = _halcon_version_to_semver(potential_version)
    return (
        'Incompatible HALCON library versions. '
        f'Expected version {expected_halcon_version} but found: '
        f'{potential_version}.\n'
        f'Either change LD_LIBRARY_PATH to point to a HALCON '
        f'{expected_halcon_version} installation, '
        f'or install the matching interface package version: '
        f'"mvtec-halcon=={package_version}"'
    )


def _compat_load_halcon_linux() -> ctypes.CDLL:
    name = halcon_native_lib_names['linux']
    try:
        return _dlopen(name['base'].format(name['version']))
    except OSError:
        try:
            # If there is any HALCON version dynamically loadable this links
            # to it.
            # Compatibility will be checked by _halcon_version_check.
            return _dlopen('libhalcon.so')
        except OSError as exc:
            if 'No such file' in str(exc):
                raise HError(
                    'Unable to find any HALCON library.\n'
                    'Set LD_LIBRARY_PATH in your environment, for example:\n'
                    'export LD_LIBRARY_PATH=$HALCONROOT/lib/x64-linux'
                ) from None
            else:
                # There are other error that we don't want to mask.
                raise exc from None


def _compat_load_halcon_darwin() -> ctypes.CDLL:
    name = halcon_native_lib_names['darwin']
    try:
        return _dlopen(name['base'].format(name['version']))
    except OSError:
        try:
            # If there is any HALCON version dynamically loadable this links
            # to it.
            # Compatibility will be checked by _halcon_version_check.
            return _dlopen(name['base'].format('Current'))
        except OSError as exc:
            if 'image not found' in str(exc):
                raise HError(
                    'Unable to find any HALCON library.\n'
                    'Set DYLD_FRAMEWORK_PATH in your environment.'
                ) from None
            else:
                raise exc from None


def _compat_load_win() -> ctypes.CDLL:
    try:
        # This name is already non version specific, so there is no fallback
        # we could try.
        return _dlopen(halcon_native_lib_names['win'])
    except FileNotFoundError:
        # Only on windows we get a more specific error FileNotFoundError
        # instead of OSError. On the other platforms the error string is the
        # only source we have to differentiate the errors.
        raise HError(
            'Unable to find any HALCON library.\n'
            'Set PATH in your environment, for example:\n'
            'set PATH="$HALCONROOT/bin/x64-win64;%PATH%"'
        ) from None


def _compat_load_halcon() -> ctypes.CDLL:
    """
    Dynamically load native HALCON library with compatibility shim.

    Returns
    -------

    lib : ctypes.CDLL
          Native library handle.

    Notes
    -----
    Due to our requirement of having to find the correct dynamic library on
    Linux and Mac we have to have the full version string information on the
    Python side, instead of realxing the version requirements on the package
    side, we chose to give better and more helpful error messages and use a
    heuristic to find and use possibly incompatible HALCON dynamic libraries
    as follows:

    Users can end up with a version mismatch by doing:

    pip install (no version):
        -> HALCON major too new
        -> wrong steady / progress

    pip install (wrong version):
        -> HALCON major too old
        -> HALCON major too new
        -> wrong steady / progress

    We have no control about pip version resolution logic.
    We can catch the error when the package is imported, and library is
    loaded as a result.

    HALCON major too old:
    Hard error

    HALCON major too new:
    Hard error

    wrong steady / progress:
    Try search for compatible 2111X X: 0-9
    WARNING in stderr: Might be broken but could work:
    Expected package version X but got Y please install Y.

    The logic on each platfrom is a bit different.

    Technically this has TOCTTOU problems in the fallback mode,
    but they seem acceptable for the situation.
    """
    if sys.platform.startswith('linux'):
        return _compat_load_halcon_linux()
    elif sys.platform.startswith('darwin'):
        return _compat_load_halcon_darwin()
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        return _compat_load_win()
    else:
        raise HError(f'Unsupported operating system {sys.platform}')


def _halcon_version_check(halcon_lib: ctypes.CDLL):
    # For example on Windows its possible to have loaded an incompatible
    # HALCON library.
    if hasattr(halcon_lib, 'HLIVersion'):
        out_c_str = ctypes.c_char_p()
        halcon_lib.HLIVersion(ctypes.byref(out_c_str))
        halcon_version = out_c_str.value.decode('utf-8')
        if halcon_version != expected_halcon_version:
            if _is_compatible_version(halcon_version):
                _log_compatibility_warning()
            else:
                raise HError(_incompatible_versions(halcon_version))
    else:
        # Hlib versions that are too old.
        # HLIVersion was added with 21.05.
        raise HError(
            'Incompatible HALCON library version.\n'
            f'Expected version: {expected_halcon_version}.\n'
            'Configure your environment so that the correct version '
            'can be found.'
        )


# Load dynamic HALCON library.
_halcon_lib: Final[ctypes.CDLL] = _compat_load_halcon()
_halcon_version_check(_halcon_lib)


class _HTuple(object):
    """
    Internal convenience HALCON HTuple RAII wrapper.

    Notes
    -----
    HALCON/Python does NOT have a HTuple class a user is ever supposed to use.
    HTuple is represented as Python list.

    This is ONLY meant for internal use.
    """

    # Funky looking signature to avoid accidental user None passing through.
    def __init__(
        self,
        value: Optional[HTupleType],
        empty: Optional[int] = None
    ):
        """Construct HTuple with value."""
        self._tuple_ptr = ctypes.c_ssize_t()
        HCkP(_halcon_lib.HLICreateTuple(ctypes.byref(self._tuple_ptr)))

        if empty != 1:
            _python_to_htuple(self._tuple_ptr, value)

    @staticmethod
    def new_empty() -> '_HTuple':
        return _HTuple(value=None, empty=1)

    def as_python(self, as_list: bool) -> HTupleType:
        """Convert native HTuple to python object."""
        return _htuple_to_python(self._tuple_ptr, as_list)

    def __enter__(self) -> '_HTuple':
        """Do nothing on enter."""
        return self

    # Type checking disabled because the parameters are not user provided.
    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        """Destroy tuple, later use is UB."""
        HCkP(_halcon_lib.HLIDestroyTuple(self._tuple_ptr))


def _get_error_text(error_code: int) -> str:
    """Return the description associated to the error id."""
    # Keep in sync with #define MAX_STRING 1024
    out_string = ctypes.create_string_buffer(1024)
    # Returns void should not fail.
    _halcon_lib.HLIGetErrorMessage(error_code, out_string)
    return out_string.value.decode('utf-8')


def _is_valid_i32(number: int) -> bool:
    return number < 2_147_483_648 and number >= -2_147_483_648


def _is_valid_ssize_t(number: int) -> bool:
    return number <= sys.maxsize and number >= -sys.maxsize


# HTuple conversions are carefully optimized because it is used ubiquitously.

def _set_htuple_value(
    tuple_ptr: ctypes.c_ssize_t,
    index: ctypes.c_int32,
    value: HTupleElementType
) -> None:
    # Only lookup type once, no need for inheritance behavior of isinstance.
    value_type = type(value)

    # Order sorted by most common as optimization.
    if value_type == float:
        c_double_value = ctypes.c_double(cast(float, value))
        HCkP(_halcon_lib.HLISetD(tuple_ptr, index, c_double_value))
    elif value_type == int:
        int_value = cast(int, value)
        # NOTE: while the interface takes an int64 it treats it as ssize_t.
        assert _is_valid_ssize_t(int_value)
        HCkP(_halcon_lib.HLISetL(tuple_ptr, index, ctypes.c_int64(int_value)))
    elif isinstance(value, HHandleBase):
        HCkP(_halcon_lib.HLISetH(tuple_ptr, index, value._handle_ptr))
    elif value_type == str:
        c_string = ctypes.c_char_p(cast(str, value).encode('utf-8'))
        HCkP(_halcon_lib.HLISetS(tuple_ptr, index, c_string))
    else:
        raise HTupleConversionError(
            f'Type is not str, int, float or HHandleBase: {value_type}'
        )


def _python_to_htuple(
    tuple_ptr: ctypes.c_ssize_t,
    value: HTupleType
) -> None:
    """
    Convert python value to htuple.

    Parameters
    ----------

    tuple_ptr : ctypes.c_ssize_t
                Number representing pointer of successfully created htuple.

    value : HTupleType
            Python value that will be converted.

    Notes
    -----
    The specific FFI functions called depend on the run time layout of the
    Python value, and are subject to change while preserving the overall
    existing semantics.

    All invalid Python values will raise an HTupleConversionError.
    If an exception happens, the htuple is left in a valid but unspecified
    state.
    """
    value_type = type(value)

    if not hasattr(value, '__iter__') or value_type == str:
        # TODO leverage Hctuple's SBO capabilites.
        _halcon_lib.HLICreateElements(tuple_ptr, ctypes.c_int32(1))
        _set_htuple_value(
            tuple_ptr,
            ctypes.c_int32(0),
            cast(HTupleElementType, value)
        )
        return

    if hasattr(value, '__len__'):
        # Type checking disabled because with hasattr we know it has len.
        tuple_length = len(value)  # type: ignore

        assert _is_valid_i32(tuple_length)

        # Reserve elements of known size if possible as optimization.
        _halcon_lib.HLICreateElements(tuple_ptr, ctypes.c_int32(tuple_length))

        # TODO try out homogenous check and single call array copy.

        # Type checking disabled because with hasattr we know it has len,
        # and the only types in the union are sequence which have iter.
        for i, element in enumerate(value):  # type: ignore
            _set_htuple_value(tuple_ptr, ctypes.c_int32(i), element)
    else:
        raise HTupleConversionError(
            'Type is not str, int, float, HHandleBase or Sequence of those:'
            f' {value_type}'
        )


def _htuple_element_to_python(
    tuple_ptr: ctypes.c_ssize_t,
    py_index: int,
    element_type: int
) -> HTupleElementType:
    """Return native HTuple value and convert it into Python representation."""

    # No need to check for 32 bit range, becuase output of c call.
    index = ctypes.c_int32(py_index)

    # Order sorted by most common as optimization.
    # Direct values because used once and constant propagation in Python :|

    if element_type == 2:  # C constant DOUBLE_PAR
        out_c_double = ctypes.c_double()
        HCkP(_halcon_lib.HLIGetD(tuple_ptr, index, ctypes.byref(out_c_double)))
        return out_c_double.value

    if element_type == 1:  # C constant LONG_PAR
        out_c_int64 = ctypes.c_int64()
        HCkP(_halcon_lib.HLIGetL(tuple_ptr, index, ctypes.byref(out_c_int64)))
        return out_c_int64.value

    if element_type == 16:  # C constant HANDLE_PAR
        out_handle_ptr = ctypes.c_void_p()
        HCkP(_halcon_lib.HLIGetH(
            tuple_ptr,
            index,
            ctypes.byref(out_handle_ptr)
        ))

        if out_handle_ptr.value is None:
            return HNull()

        return mixin.to_handle(out_handle_ptr)

    if element_type == 4:  # C constant STRING_PAR
        out_c_str = ctypes.c_char_p()
        HCkP(_halcon_lib.HLIGetS(tuple_ptr, index, ctypes.byref(out_c_str)))
        c_str_bytes = out_c_str.value
        if c_str_bytes is None:
            raise Exception('TODO What should be done here?')

        return c_str_bytes.decode('utf-8')

    raise HTupleConversionError(
        f'Unknown HTuple element type {element_type}'
    )


def _htuple_to_python(
    tuple_ptr: ctypes.c_ssize_t,
    as_list: bool
) -> HTupleType:
    """
    Convert htuple to python value.

    Parameters
    ----------

    tuple_ptr : ctypes.c_ssize_t
                Number representing pointer of successfully created htuple.

    as_list : bool
              Should the output always be a list.

    Returns
    -------

    value : Optional[HTupleType]
            Python value representation of htuple.

    Notes
    -----
    The specific FFI functions called depend on the run time layout of the
    Python value, and are subject to change while preserving the overall
    existing semantics.

    If the htuple cannot be represented as Python value, raises
    HTupleConversionError.

    If as_list is set to False, but the tuple has not exactly 1 value,
    raises HTupleConversionError.

    Does not modify the htuple, regardless of execution path.
    """
    # TODO SBO store type in pointer without alloc if len == 1.
    # and SBO value in additional parameter.
    # TODO check for homogenous type and pull out via one GatArr call.

    # Guessing that allocation and complexity cost of pulling out all
    # elements of a hetergenous tuple in a single call won't be worth it.

    c_tuple_len = ctypes.c_int32()
    types = ctypes.POINTER(ctypes.c_int32)()

    try:
        HCkP(_halcon_lib.HLIGetElementTypes(
            tuple_ptr,
            ctypes.byref(c_tuple_len),
            ctypes.byref(types)
        ))

        tuple_len = c_tuple_len.value

        if as_list:
            return [
                _htuple_element_to_python(tuple_ptr, i, cast(int, types[i]))
                for i in range(tuple_len)
            ]
        elif tuple_len != 1:
            raise HTupleConversionError(
                f'Invalid tuple length: {tuple_len}, expected single value.'
            )

        return _htuple_element_to_python(tuple_ptr, 0, cast(int, types[0]))

    finally:
        HCkP(_halcon_lib.HLIDestroyTupleTypes(types))

# TODO test fail import with path set to only pipenv virtualenv.
