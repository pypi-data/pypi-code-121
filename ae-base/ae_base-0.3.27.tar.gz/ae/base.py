"""
basic constants, helper functions and context manager
=====================================================

this module is pure python and has no external dependencies. apart from providing base constants, common helper
functions and context managers, it is also patching the :mod:`shutil` module to prevent crashes on Android OS.


base constants
--------------

ISO format strings for `date` and `datetime` values are provided by the constants :data:`DATE_ISO` and
:data:`DATE_TIME_ISO`.

the :data:`UNSET` constant is useful in cases where `None` is a valid data value and another special value is needed
to specify that e.g. an argument or attribute has no (valid) value or did not get specified/passed.

the string :data:`os_platform` provides the OS where your app is running.


base helper functions
---------------------

the function :func:`duplicates` returns the duplicates of an iterable type.

use :func:`env_str` to determine the value of an OS environment variable with automatic variable name conversion. other
helper functions provided by this namespace portion to determine the values of the most important system environment
variables for your application are :func:`sys_env_dict` and :func:`sys_env_text`.

:func:`app_name_guess` guesses the name of o running Python application from the application environment, with the help
of :func:`build_config_variable_values`, which determines config-variable-values from the app's build spec file.

:func:`norm_line_sep` is converting any combination of line separators of a string to a single new-line character.

:func:`norm_name` converts any string into a name that can be used e.g. as file name or as method/attribute name.

to normalize a file path, in order to remove `.`, `..` placeholders, to resolve symbolic links or to make it relative or
absolute, call the function :func:`norm_path`.

:func:`camel_to_snake` and :func:`snake_to_camel` providing name conversions of class and method names.

to encode unicode strings to other codecs the functions :func:`force_encoding` and :func:`to_ascii` can be used.

the :func:`round_traditional` function get provided by this module for traditional rounding of float values. the
function signature is fully compatible to Python's :func:`round` function.

the function :func:`instantiate_config_parser` ensures that the :class:`~configparser.ConfigParser` instance is
correctly configured, e.g. to support case-sensitive config variable names and to use :class:`ExtendedInterpolation` for
the interpolation argument.


generic context manager
-----------------------

the context manager :func:`in_wd` changes the current working directory in the temporary context. the following example
demonstrate a typical usage, together with a temporary path, created with the help of Pythons
:class:`~tempfile.TemporaryDirectory` class::

    with tempfile.TemporaryDirectory() as tmp_dir, in_wd(tmp_dir):
        assert os.getcwd() == tmp_dir
        # the tmp_dir is set as the current working directory
    # current working directory set back to the original path and the temporary directory got removed

"""
import datetime
import getpass
import importlib.abc
import importlib.util
import os
import platform
import shutil
import socket
import sys
import unicodedata

from configparser import ConfigParser, ExtendedInterpolation
from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, AnyStr, Dict, Generator, Iterable, List, Optional, Tuple, Union

__version__ = '0.3.27'


DOCS_FOLDER = 'docs'                            #: project documentation root folder name
TESTS_FOLDER = 'tests'                          #: name of project folder to store unit/integration tests
TEMPLATES_FOLDER = 'templates'
""" template folder name, used in template and namespace root projects to maintain and provide common file templates """

BUILD_CONFIG_FILE = 'buildozer.spec'            #: gui app build config file
PACKAGE_INCLUDE_FILES_PREFIX = 'ae_'            #: prefix of file/folder names to be included into the package_data

PY_EXT = '.py'                                  #: file extension for modules and hooks
PY_INIT = '__init__' + PY_EXT                   #: init-module file name of a python package

CFG_EXT = '.cfg'                                #: CFG config file extension
INI_EXT = '.ini'                                #: INI config file extension

DATE_ISO = "%Y-%m-%d"                           #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO = "%Y-%m-%d %H:%M:%S.%f"          #: ISO string format for datetime values

DEF_ENCODE_ERRORS = 'backslashreplace'          #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING = 'ascii'
""" encoding for :func:`force_encoding` that will always work independent from destination (console, file sys, ...).
"""

NAME_PARTS_SEP = '_'                            #: name parts separator character, e.g. for :func:`norm_name`


# using only object() does not provide proper representation string
class UnsetType:
    """ (singleton) UNSET (type) object class. """
    def __bool__(self):
        """ ensure to be evaluated as False, like None. """
        return False

    def __len__(self):
        """ ensure to be evaluated as empty. """
        return 0


UNSET = UnsetType()     #: pseudo value used for attributes/arguments if `None` is needed as a valid value


def app_name_guess() -> str:
    """ guess/try to determine the name of the currently running app (w/o assessing not yet initialized app instance).

    :return:                    application name/id or "unguessable" if not guessable.
    """
    app_name = build_config_variable_values(('package.name', ""))[0]
    if not app_name:
        unspecified_app_names = ('ae_base', 'app', '_jb_pytest_runner', 'main', '__main__', 'pydevconsole', 'src')
        path = sys.argv[0]
        app_name = os.path.splitext(os.path.basename(path))[0]
        if app_name.lower() in unspecified_app_names:
            path = os.getcwd()
            app_name = os.path.basename(path)
            if app_name.lower() in unspecified_app_names:
                app_name = "unguessable"
    return app_name


def build_config_variable_values(*names_defaults: Tuple[str, Any], section: str = 'app') -> Tuple[Any, ...]:
    """ determine build config variable values from the ``buildozer.spec`` file in the current directory.

    :param names_defaults:      tuple of tuples of build config variable names and default values.
    :param section:             name of the spec file section, using 'app' as default.
    :return:                    tuple of build config variable values (using the passed default value if not specified
                                in the :data:`BUILD_CONFIG_FILE` spec file or if the spec file does not exist in cwd).
    """
    if not os.path.exists(BUILD_CONFIG_FILE):
        return tuple(def_val for name, def_val in names_defaults)

    config = instantiate_config_parser()
    config.read(BUILD_CONFIG_FILE, 'utf-8')

    return tuple(config.get(section, name, fallback=def_val) for name, def_val in names_defaults)


def camel_to_snake(name: str) -> str:
    """ convert name from CamelCase to snake_case.

    :param name:                name string in CamelCaseFormat.
    :return:                    name in snake_case_format.
    """
    str_parts = []
    for char in name:
        if char.isupper():
            str_parts.append(NAME_PARTS_SEP + char)
        else:
            str_parts.append(char)
    return "".join(str_parts)


def deep_dict_update(data: dict, update: dict):
    """ update the optionally nested data dict in-place with the items and sub-items from the update dict.

    :param data:                dict to be updated/extended. non-existing keys of dict-sub-items will be added.
    :param update:              dict with the [sub-]items to update in the :paramref:`.data` dict.

    .. hint:: the module/portion :mod:`ae.deep` is providing more deep update helper functions.

    """
    for upd_key, upd_val in update.items():
        if isinstance(upd_val, dict):
            if upd_key not in data:
                data[upd_key] = {}
            deep_dict_update(data[upd_key], upd_val)
        else:
            data[upd_key] = upd_val


def duplicates(values: Iterable) -> list:
    """ determine all duplicates in the iterable specified in the :paramref:`.values` argument.

    inspired by Ritesh Kumars answer to https://stackoverflow.com/questions/9835762.

    :param values:              iterable (list, tuple, str, ...) to search for duplicate items.
    :return:                    list of the duplicate items found (can contain the same duplicate multiple times).
    """
    seen_set: set = set()
    seen_add = seen_set.add
    dup_list: list = []
    dup_add = dup_list.append
    for item in values:
        if item in seen_set:
            dup_add(item)
        else:
            seen_add(item)
    return dup_list


def env_str(name: str, convert_name: bool = False) -> Optional[str]:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of an OS environment variable.
    :param convert_name:        pass True to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else None.
    """
    if convert_name:
        name = norm_name(camel_to_snake(name)).upper()
    return os.environ.get(name)


def force_encoding(text: AnyStr, encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:                text as str/bytes.
    :param encoding:            encoding (def= :data:`DEF_ENCODING`).
    :param errors:              encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:                    text as str (with all characters checked/converted/replaced to be encode-able).
    """
    enc_str: bytes = text.encode(encoding=encoding, errors=errors) if isinstance(text, str) else text   # type: ignore
    return enc_str.decode(encoding=encoding)


def import_module(import_name: str, path: Optional[Union[str, UnsetType]] = UNSET) -> Optional[ModuleType]:
    """ search, import and execute a Python module dynamically without adding it to sys.modules.

    :param import_name:         dot-name of the module to import.
    :param path:                optional file path of the module to import. if this arg is not specified or has the
                                default value (:data:`UNSET`), then the path will be determined from the import name.
                                specify ``None`` to prevent the module search.
    :return:                    a reference to the loaded module or ``None`` if module could not be imported.
    """
    if path is UNSET:
        path = import_name.replace('.', os.path.sep)
        path += PY_EXT if os.path.isfile(path + PY_EXT) else os.path.sep + PY_INIT
    mod_ref = None

    spec = importlib.util.spec_from_file_location(import_name, path)    # type: ignore # silly mypy
    if isinstance(spec, ModuleSpec):
        mod_ref = importlib.util.module_from_spec(spec)
        # added isinstance and imported importlib.abc to suppress PyCharm+mypy inspections
        if isinstance(spec.loader, importlib.abc.Loader):
            try:
                spec.loader.exec_module(mod_ref)
            except FileNotFoundError:
                mod_ref = None

    return mod_ref


def instantiate_config_parser() -> ConfigParser:
    """ instantiate and prepare config file parser. """
    cfg_parser = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
    # set optionxform to have case-sensitive var names (or use 'lambda option: option')
    # mypy V 0.740 bug - see mypy issue #5062: adding pragma "type: ignore" breaks PyCharm (showing
    # .. inspection warning "Non-self attribute could not be type-hinted"), but
    # .. also cast(Callable[[Arg(str, 'option')], str], str) and # type: ... is not working
    # .. (because Arg is not available in plain mypy, only in the extra mypy_extensions package)
    setattr(cfg_parser, 'optionxform', str)
    return cfg_parser


@contextmanager
def in_wd(new_cwd: str) -> Generator[None, None, None]:
    """ context manager to temporary switch the current working directory / cwd.

    :param new_cwd:             path to the directory to switch to (within the context/with block).
    """
    cur_dir = os.getcwd()
    try:
        os.chdir(new_cwd)
        yield
    finally:
        os.chdir(cur_dir)


def main_file_paths_parts(portion_name: str) -> Tuple[Tuple[str, ...], ...]:
    """ determine tuple of supported main/version file name path part tuples.

    :param portion_name:        portion or package name.
    :return:                    tuple of tuples of main/version file name path parts.
    """
    return (
        ('main' + PY_EXT, ),
        ('__main__' + PY_EXT, ),
        (PY_INIT, ),
        ('main', PY_INIT),          # django main project
        (portion_name + PY_EXT, ),
        (portion_name, PY_INIT),
    )


def norm_line_sep(text: str) -> str:
    """ convert any combination of line separators in the :paramref:`~norm_line_sep.text` arg to new-line characters.

    :param text:                string containing any combination of line separators ('\\\\r\\\\n' or '\\\\r').
    :return:                    normalized/converted string with only new-line ('\\\\n') line separator characters.
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str, allow_num_prefix: bool = False) -> str:
    """ normalize name to start with a letter/alphabetic/underscore and to contain only alphanumeric/underscore chars.

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :param allow_num_prefix:    pass True to allow leading digits in the returned normalized name.
    :return:                    cleaned/normalized/converted name string (e.g. for a variable-/method-/file-name).
    """
    str_parts: List[str] = []
    for char in name:
        if char.isalpha() or char.isalnum() and (allow_num_prefix or str_parts):
            str_parts.append(char)
        else:
            str_parts.append('_')
    return "".join(str_parts)


def norm_path(path: str, make_absolute: bool = True, remove_base_path: str = "", remove_dots: bool = True,
              resolve_sym_links: bool = True) -> str:
    """ normalize path, replacing `..`/`.` parts or the tilde character (for home folder) and transform to relative/abs.

    :param path:                path string to normalize/transform.
    :param make_absolute:       pass False to not convert path to an absolute path.
    :param remove_base_path:    pass a valid base path to return a relative path, even if the argument values of
                                :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links` are
                                `True`.
    :param remove_dots:         pass False to not replace/remove the `.` and `..` placeholders.
    :param resolve_sym_links:   pass False to not resolve symbolic links, passing True implies a `True` value also for
                                the :paramref:`~norm_path.make_absolute` argument.
    :return:                    normalized path string: absolute if :paramref:`~norm_path.remove_base_path` is empty and
                                either :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links`
                                is `True`; relative if :paramref:`~norm_path.remove_base_path` is a base path of
                                :paramref:`~norm_path.path` or if :paramref:`~norm_path.path` got specified as relative
                                path and neither :paramref:`~norm_path.make_absolute` nor
                                :paramref:`~norm_path.resolve_sym_links` is `True`.

    .. hint:: the :func:`~ae.paths.normalize` function additionally replaces :data:`~ae.paths.PATH_PLACEHOLDERS`.

    """
    path = path or "."
    if path[0] == "~":
        path = os.path.expanduser(path)

    if remove_dots:
        path = os.path.normpath(path)

    if resolve_sym_links:
        path = os.path.realpath(path)
    elif make_absolute:
        path = os.path.abspath(path)

    if remove_base_path:
        if remove_base_path[0] == "~":
            remove_base_path = os.path.expanduser(remove_base_path)
        path = os.path.relpath(path, remove_base_path)

    return path


def now_str(sep: str = "") -> str:
    """ return the current timestamp as string (to use as suffix for file and variable/attribute names).

    :param sep:                 optional prefix and separator character (separating date from time and in time part
                                the seconds from the microseconds).
    :return:                    timestamp as string (length=20 + 3 * len(sep)).
    """
    return datetime.datetime.now().strftime("{sep}%Y%m%d{sep}%H%M%S{sep}%f".format(sep=sep))


def os_host_name() -> str:
    """ determine the operating system host/machine name.

    :return:                    machine name string.
    """
    return platform.node()


def os_local_ip() -> str:
    """ determine ip address of this system/machine in the local network (LAN or WLAN).

    inspired by answers of SO users @dml and @fatal_error to the question: https://stackoverflow.com/questions/166506.

    :return:                    ip address of this machine in the local network (WLAN or LAN/ethernet)
                                or empty string if this machine is not connected to any network.
    """
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket1.connect(('10.255.255.255', 1))      # doesn't even have to be reachable
        ip_address = socket1.getsockname()[0]
    except (OSError, IOError):                      # pragma: no cover
        # ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError inherit from OSError
        socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            socket2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket2.connect(('<broadcast>', 0))
            ip_address = socket2.getsockname()[0]
        except (OSError, IOError):
            ip_address = ""
        finally:
            socket2.close()
    finally:
        socket1.close()

    return ip_address


def _os_platform() -> str:
    """ determine the operating system where this code is running (used to initialize the :data:`os_platform` variable).

    :return:                    operating system (extension) as string:

                                * `'android'` for all Android systems.
                                * `'cygwin'` for MS Windows with an installed Cygwin extension.
                                * `'darwin'` for all Apple Mac OS X systems.
                                * `'freebsd'` for all other BSD-based unix systems.
                                * `'ios'` for all Apple iOS systems.
                                * `'linux'` for all other unix systems (like Arch, Debian/Ubuntu, Suse, ...).
                                * `'win32'` for MS Windows systems (w/o the Cygwin extension).

    """
    if env_str('ANDROID_ARGUMENT') is not None:     # p4a env variable; alternatively use ANDROID_PRIVATE
        return 'android'
    return env_str('KIVY_BUILD') or sys.platform    # KIVY_BUILD == 'android'/'ios' on Android/iOS


os_platform = _os_platform()
""" operating system / platform string (see :func:`_os_platform`).

this string value gets determined for most of the operating systems with the help of Python's :func:`sys.platform`
function and additionally detects the operating systems iOS and Android (not supported by Python).
"""


if os_platform == 'android':                                    # pragma: no cover
    # monkey patch the :func:`shutil.copystat` and :func:`shutil.copymode` helper functions, which are crashing on
    # 'android' (see # https://bugs.python.org/issue28141 and https://bugs.python.org/issue32073). these functions are
    # used by shutil.copy2/copy/copytree/move to copy OS-specific file attributes.
    # although shutil.copytree() and shutil.move() are copying/moving the files correctly when the copy_function
    # arg is set to :func:`shutil.copyfile`, they will finally also crash afterwards when they try to set the attributes
    # on the destination root directory.
    shutil.copymode = lambda *args, **kwargs: None      # print("shutil.copymode ae.base.PATCH", args, kwargs)
    shutil.copystat = lambda *args, **kwargs: None      # print("shutil.copystat ae.base.PATCH", args, kwargs)


def os_user_name() -> str:
    """ determine the operating system username.

    :return:                    username string.
    """
    return getpass.getuser()


def project_main_file(import_name: str, project_path: str = "") -> str:
    """ determine the main module file path of a package project, containing the package __version__ module variable.

    :param import_name:         import name of the module/package (including namespace prefixes for namespace packages).
    :param project_path:        optional path where the project of the package/module is situated. not needed if the
                                current working directory is the root folder of either the import_name project or of a
                                sister project (under the same project parent folder).
    :return:                    absolute file path/name of main module or empty string if no main/version file found.
    """
    join = os.path.join
    *namespace_dirs, portion_name = import_name.split('.')
    package_name = ('_'.join(namespace_dirs) + '_' if namespace_dirs else "") + portion_name
    paths_parts = main_file_paths_parts(portion_name)

    project_path = norm_path(project_path)
    module_paths = []
    if os.path.basename(project_path) != package_name:
        module_paths.append(join(os.path.dirname(project_path), package_name, *namespace_dirs))
    if namespace_dirs:
        module_paths.append(join(project_path, *namespace_dirs))
    module_paths.append(project_path)

    for module_path in module_paths:
        for path_parts in paths_parts:
            main_file = join(module_path, *path_parts)
            if os.path.isfile(main_file):
                return main_file
    return ""


def read_file(file_path: str, extra_mode: str = "", encoding: Optional[str] = None, error_handling: str = 'ignore'
              ) -> AnyStr:
    """ returning content of the text/binary file specified by file_path argument as string.

    :param file_path:           file path/name to load into a string or a bytes array.
    :param extra_mode:          extra open mode flag characters appended to "r" onto open() mode argument. pass "b" to
                                read the content of a binary file returned as bytes array. in binary mode the argument
                                passed in :paramref:`~read_file.error_handling` will be ignored.
    :param encoding:            encoding used to load and convert/interpret the file content.
    :param error_handling:      for files opened in text mode pass `'strict'` or `None` to return `None` (instead of an
                                empty string) for the cases where either a decoding `ValueError` exception or any
                                `OSError`, `FileNotFoundError` or `PermissionError` exception got raised.
                                the default value `'ignore'` will ignore any decoding errors (missing some characters)
                                and will return an empty string on any file/os exception. this parameter will be ignored
                                if the :paramref:`~read_file.extra_mode` argument contains the 'b' character (to read
                                the file content as binary/bytes-array).
    :return:                    file content string or bytes array.
    :raises FileNotFoundError:  if file does not exist.
    :raises OSError:            if :paramref:`~read_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.
    """
    extra_kwargs = {} if "b" in extra_mode else {'errors': error_handling}
    with open(file_path, "r" + extra_mode, encoding=encoding, **extra_kwargs) as file_handle:           # type: ignore
        return file_handle.read()


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    needed because python round() is working differently, e.g. round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:           float value to be round.
    :param num_digits:          number of digits to be round (def=0 - rounds to an integer value).

    :return:                    rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


def snake_to_camel(name: str, back_convertible: bool = False) -> str:
    """ convert name from snake_case to CamelCase.

    :param name:                name string composed of parts separated by an underscore character
                                (:data:`NAME_PARTS_SEP`).
    :param back_convertible:    pass `True` to get the first character of the returned name in lower-case
                                if the snake name has no leading underscore character (and to allow
                                the conversion between snake and camel case without information loss).
    :return:                    name in camel case.
    """
    ret = "".join(part.capitalize() for part in name.split(NAME_PARTS_SEP))
    if back_convertible and name[0] != NAME_PARTS_SEP:
        ret = ret[0].lower() + ret[1:]
    return ret


def sys_env_dict() -> Dict[str, Any]:
    """ returns dict with python system run-time environment values.

    :return:                    python system run-time environment values like python_ver, argv, cwd, executable,
                                frozen and bundle_dir (if bundled with pyinstaller).

    .. hint:: see also https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    """
    sed: Dict[str, Any] = {
        'python_ver': sys.version.replace('\n', ' '),
        'platform': os_platform,
        'argv': sys.argv,
        'executable': sys.executable,
        'cwd': os.getcwd(),
        'frozen': getattr(sys, 'frozen', False),
        'user_name': os_user_name(),
        'host_name': os_host_name(),
        'app_name_guess': app_name_guess(),
    }

    if sed['frozen']:
        sed['bundle_dir'] = getattr(sys, '_MEIPASS', '*#ERR#*')

    return sed


def sys_env_text(ind_ch: str = " ", ind_len: int = 12, key_ch: str = "=", key_len: int = 15,
                 extra_sys_env_dict: Optional[Dict[str, str]] = None) -> str:
    """ compile formatted text block with system environment info.

    :param ind_ch:              indent character (default=" ").
    :param ind_len:             indent depths (default=12 characters).
    :param key_ch:              key-value separator character (default="=").
    :param key_len:             key-name minimum length (default=15 characters).
    :param extra_sys_env_dict:  dict with additional system info items.
    :return:                    text block with system environment info.
    """
    sed = sys_env_dict()
    if extra_sys_env_dict:
        sed.update(extra_sys_env_dict)
    key_len = max([key_len] + [len(key) + 1 for key in sed])

    ind = ""
    text = "\n".join([f"{ind:{ind_ch}>{ind_len}}{key:{key_ch}<{key_len}}{val}" for key, val in sed.items()])

    return text


def to_ascii(unicode_str: str) -> str:
    """ converts unicode string into ascii representation.

    useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:         string to convert.
    :return:                    converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('ß', "ss").replace('€', "Euro")


def write_file(file_path: str, content: AnyStr, extra_mode: str = "", encoding: Optional[str] = None):
    """ (over)write the file specified by :paramref:`~write_file.file_path` with text or binary/bytes content.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content either passed as string or list of line strings (will be
                                concatenated with the line separator of the current OS: os.linesep).
    :param extra_mode:          open mode flag characters. passed unchanged to the `mode` argument of :func:`open` if
                                this argument starts with 'a', else this argument value will be appended to 'w'.
    :param encoding:            encoding used to write/convert/interpret the file content to write.
    :raises FileExistsError:    if file exists already and is write-protected.
    :raises FileNotFoundError:  if parts of the file path do not exist.
    :raises OSError:            if :paramref:`~read_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.
    """
    with open(file_path, ('' if extra_mode.startswith('a') else 'w') + extra_mode, encoding=encoding) as file_handle:
        file_handle.write(content)
