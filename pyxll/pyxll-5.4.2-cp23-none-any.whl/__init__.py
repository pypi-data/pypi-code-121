"""
Copyright PyXLL Ltd
www.pyxll.com

PyXLL allows you to create Excel addins written in Python.

*************************************************************************
* IMPORTANT:                                                            *
*  This module is NOT the actual pyxll module used when your PyXLL      *
*  addin runs in Excel.                                                 *
*                                                                       *
*  It is just a module of stubs functions so that you can import pyxll  *
*  from other python interpreters outside of Excel (for unit testing,   *
*  for example).                                                        *
*************************************************************************

This module contains decorators used by the PyXLL Excel addin to expose
python functions as worksheet functions, macro functions and menu items
to Excel.

For full documentation please refer to www.pyxll.com.
"""
from xml.dom import minidom
import warnings
import traceback
import datetime
import logging
import sys

_log = logging.getLogger(__name__)

__version__ = "5.4.2"

nan = 1e10000 * 0

xlCalculationAutomatic = 1
xlCalculationSemiAutomatic = 2
xlCalculationManual = 3

xlDialogTypeNone = 0
xlDialogTypeFunctionWizard = 1
xlDialogTypeSearchAndReplace = 2

# Import typing for use by some type hints
if sys.version_info[:2] > (3, 5):
    try:
        import typing
        if typing.TYPE_CHECKING:
            try:
                import exceltypes
            except ImportError:
                pass
            try:
                import win32com.client
            except ImportError:
                pass
            try:
                import pythoncom
            except ImportError:
                pass
            try:
                import comtypes
            except ImportError:
                pass
            try:
                import types
            except ImportError:
                pass

            _ExcInfo = "Tuple[Type[BaseException], BaseException, types.TracebackType]"  # type: typing.TypeAlias
            _OptExcInfo = "Union[_ExcInfo, Tuple[None, None, None]]"  # type: typing.TypeAlias
            _COMObject = "typing.Union[win32com.client.Dispatch, pythoncom.PyIUnknown, comtypes.POINTER, typing.Any]"  # type: typing.TypeAlias
            _ExcelApplication = "typing.Union[exceltypes.Application, _COMObject]"  # type: typing.TypeAlias
            _ExcelRange = "typing.Union[exceltypes.Range, _COMObject]"  # type: typing.TypeAlias
            _Function = "typing.Callable[[...], typing.Any]"  # type: typing.TypeAlias
            _Decorator = "typing.Union[typing.Callable[[_Function], _Function], _Function]"  # type: typing.TypeAlias
    except ImportError:
        pass

def reload():
    """
    Causes the PyXLL addin and any modules listed in the config file to be reloaded
    once the calling function has returned control back to Excel.

    If the `deep_reload` configuration option is turned on then any dependencies
    of the modules listed in the config file will also be reloaded.

    The Python interpreter is not restarted.
    """
    raise Exception("Not supported when running outside of Excel")

def com_reload():
    """
    Causes the COM part of the PyXLL addin to be reloaded once the calling function
    has returned control back to Excel.

    This doesn't reload any Python modules or rebind any functions. The COM addin
    is responsible for the ribbon user interface and reloading it will cause the
    ribbon to be reloaded.
    """
    raise Exception("Not supported when running outside of Excel")

def rebind():
    """
    Causes the PyXLL addin to rebuild the bindings between the exposed Python
    functions and Excel once the calling function has returned control back to Excel.

    This can be useful when importing modules or declaring new Python functions
    dynamically and you want newly imported or created Python functions to be exposed to Excel without reloading.

    Example usage::

        from pyxll import xl_macro, rebind

        @xl_macro
        def load_python_modules():
            import another_module_with_pyxll_functions
            rebind()
    """
    raise Exception("Not supported when running outside of Excel")

def about():
    """
    Show the PyXLL 'about' dialog.
    """
    raise Exception("Not supported when running outside of Excel")

def xl_arg_type(name,  # type: name
                base_type,  # type: str
                allow_arrays=True,  # type: bool
                macro=None,  # type: bool
                thread_safe=None  # type: bool
                ):  # type: () -> typing.Callable[[typing.Callable[[...], typing.Any]], typing.Callable[[...], typing.Any]]
    """
    Decorator for adding custom types for use with
    functions exposed via xl_func and xl_macro.
    eg:

    class myobject:
        def __init__(self, name):
            self.name = name

    @xl_arg_type("myobject", "string")
    def myobject_from_string(name):
        return myobject(name)

    @xl_func("myobject obj: string")
    def get_name(obj):
        return obj.name

    in this example, get_name is called from excel with a string argument
    that is converted to a myobject instance via myobject_from_string.

    If allow_arrays is True, arrays of the custom type are allowed
    using the standard signature notation 'myobject[]' (for the example
    above).

    macro and thread_safe can be set if the function using this type
    must be a macro equivalent function (set macro=True) or must not
    be registered as thread safe (set thread_safe=False).
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_return_type(name,  # type: str
                   base_type,  # type: str
                   allow_arrays=True,  # type: bool
                   macro=None,  # type: bool
                   thread_safe=None  # type: bool
                   ):  # type: () -> _Decorator
    """
    Decorator for adding custom types for use with
    functions exposed via xl_func and xl_macro.
    eg:

    class myobject:
        def __init__(self, name):
            self.name = name

    @xl_return_type("myobject", "string")
    def myobject_to_string(obj):
        return obj.name

    @xl_func("string name: myobject")
    def get_object(name):
        return myobject(name)

    in this example, get_object is called from excel with a string
    argument and returns a myobject instance. That is converted to a
    string by the registered myobject_to_string function and returned
    to excel as a string.

    If allow_arrays is True, arrays of the custom type are allowed
    using the standard signature notation 'myobject[]' (for the example
    above).

    macro and thread_safe can be set if the function using this type
    must be a macro equivalent function (set macro=True) or must not
    be registered as thread safe (set thread_safe=False).
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_return(_type=None, **kwargs):
    # type: (str, ...) -> _Decorator
    """
    Add type information for a function's return type.

    This can be used instead or as well as providing the return type information
    in the function signature.

    Using this decorator can be simpler when the return type is generic and requires
    complex type arguments.

    @xl_func
    @xl_return("dataframe", index=True, columns=True)
    def return_pandas_dataframe():
        pass

    :param _type: Type expected to be returned by the function
    :param kwargs: Keyword arguments provided to the return type converter
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_arg(_name, _type=None, **kwargs):
    # type: (str, str, ...) -> _Decorator
    """
    Add type information for a function's argument type.

    This can be used instead or as well as providing the return type information
    in the function signature.

    Using this decorator can be simpler when the return type is generic and requires
    complex type arguments.

    @xl_func
    @xl_arg("x", "dataframe", index=True, columns=True)
    def return_pandas_dataframe(x):
        pass

    :param _name: Name of the argument this relates to
    :param _type: Type expected for the argument
    :param kwargs: Keyword arguments provided to the argument type converter
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def get_type_converter(src_type,  # type: typing.Union[str, typing.Type]
                       dest_type,   # type: typing.Union[str, typing.Type]
                       src_kwargs={},  # type: typing.Dict[str, typing.Any]
                       dest_kwargs={}  # type: typing.Dict[str, typing.Any]
                       ):  # type: () -> typing.Callable[[typing.Any], typing.Any]
    """
    Return a function that converts from one type registered
    with PyXLL to another.

    When this function is called from outside of Excel then it
    is purely a stub function. It returns a dummy function that simply
    returns the argument it is passed.

    This is so the functions can be written that take var arguments when
    called from Excel and use PyXLL's type conversion to convert to proper
    python types, but accept proper python types when called from other python
    code outside of Excel (e.g. when testing in an interactive prompt or in
    unit tests).

    For example::

        @xl_func("var a_date: var")
        def test_func(a_date):
            if a_date is not None:
                var_to_date = get_type_converter("var", "date")
                a_date = var_to_date(a_date) # does nothing if not called in Excel
                return a_date.strftime("%Y-%m-%d")

        >> test_func(datetime.date(2014,2,11))
        '2014-02-11'
    """
    # This is a dummy function here only so it can be imported and does not perform
    # any type conversion when no imported from inside Excel.
    return lambda x: x

def get_active_object():
    # type: (typing.Union[str, None]) -> _ExcelApplication
    """
    Deprecated. Use xl_app instead.
    """
    warnings.warn("pyxll.get_active_object is deprecated. Use xl_app instead.", DeprecationWarning)

    # this is only used when calling from outside Excel.
    # the builtin pyxll module does 'the right thing'.
    xl = xl_app()
    return xl.Windows[0]

def xl_app(com_package="win32com"):
    # type: (typing.Union[str, None]) -> _ExcelApplication
    """
    Return the COM Excel Application object for the Excel
    instance the PyXLL addin is running in.

    When called from outside of Excel, this will return the first
    open Excel found. If there is no Excel window open, this
    function will raise and Exception.
    """
    # this is only used when calling from outside Excel.
    # the builtin pyxll module does 'the right thing'.
    if com_package == "pythoncom":
        import pythoncom
        return pythoncom.GetActiveObject("Excel.Application")

    elif com_package == "win32com":
        import pythoncom
        xl = pythoncom.GetActiveObject("Excel.Application")
        return _wrap_iunknown(xl)

    elif com_package == "comtypes":
        import comtypes.client
        return comtypes.client.GetActiveObject("Excel.Application")

    elif com_package == "xlwings":
        import xlwings
        try:
            version = tuple(map(int, xlwings.__version__.split(".")[:2]))
        except Exception:
            _log.warning("Error parsing xlwings version '%s'" % xlwings.__version__)
            version = (0, 0)
        assert version >= (0, 9), "xlwings >= 0.9 required (%s is installed)" % xlwings.__version__
        if xlwings.apps.count == 0:
            return xlwings.App()
        return xlwings.apps.active

    else:
        raise ValueError("Unexpected com_package '%s'" % com_package)

def get_dialog_type():
    # type: () -> int
    """
    Returns a value indicating what type of dialog a function was
    called from, if any.

    This can be used to disable slow running calculations in the
    function wizard or when doing a search and replace operation.
    """
    return xlDialogTypeNone

def get_last_error(cell):
    # type: (Union[XLCell, exceltypes.Range]) -> _OptExcInfo
    """
    When a Python function is called from an Excel worksheet, if an uncaught exception is raised PyXLL
    caches the exception and traceback as well as logging it to the log file.

    The last exception raised while evaluating a cell can be retrieved using this function.

    The cache used by PyXLL to store thrown exceptions is limited to a maximum size, and so if there are
    more cells with errors than the cache size the least recently thrown exceptions are discarded. The
    cache size may be set via the error_cache_size setting in the config file.

    When a cell returns a value and no exception is thrown any previous error is **not** discarded. This
    is because doing so would add additional performance overhead to every function call.

    :param xl_cell: XLCell instance or a COM Range object (the exact type depends
                    on the com_package setting in the config file.

    :return: The last exception raised by a Python function evaluated in the cell, as a tuple
             (type, value, traceback).

    Example usage::

        from pyxll import xl_func, xl_menu, xl_version, get_last_error
        import traceback

        @xl_func("xl_cell: string")
        def python_error(cell):
            exc_type, exc_value, exc_traceback = pyxll.get_last_error(cell)
            if exc_type is None:
                return "No error"

            return "".join(traceback.format_exception_only(exc_type, exc_value))
    """
    raise Exception("Not supported when running outside of Excel")

def load_image(filename):
    # type: (str) -> _COMObject
    """
    Loads an image file and returns it as a COM IPicture object suitable for use when
    customizing the ribbon.

    This function can be set at the Ribbon image handler by setting the loadImage attribute on
    the customUI element in the ribbon XML file.

    .. code-block:: xml
        :emphasize-lines: 2, 11

        <customUI xmlns="http://schemas.microsoft.com/office/2006/01/customui"
                    loadImage="pyxll.load_image">
            <ribbon>
                <tabs>
                    <tab id="CustomTab" label="Custom Tab">
                        <group id="Tools" label="Tools">
                            <button id="Reload"
                                    size="large"
                                    label="Reload PyXLL"
                                    onAction="pyxll.reload"
                                    image="reload.png"/>
                        </group>
                    </tab>
                </tabs>
            </ribbon>
        </customUI>

    Or it can be used when returning an image from a getImage callback.

    :param string filename: Filename of the image file to load. This may be an absolute path or relative to
                            the ribbon XML file.

    :return: A COM IPicture object (the exact type depends
                on the com_package setting in the config file.
    """
    raise Exception("Not supported when running outside of Excel")

def cached_object_count():
    # type: () -> int
    """Return the number of objects cached in the internal object cache"""
    return 0

def message_box(message, caption="", flags=0):
    # type: (str, str, int) -> None
    """Show a message dialog box."""
    import win32api
    return win32api.MessageBox(None, message, caption, flags)

def xlfGetDocument(arg_num, name=None):
    raise Exception("Not supported when running outside of Excel")

def xlfGetWorkspace(arg_num):
    raise Exception("Not supported when running outside of Excel")

def xlfGetWorkbook(arg_num, workbook_name=None):
    raise Exception("Not supported when running outside of Excel")

def xlfGetWindow(arg_num, workbook_name=None):
    raise Exception("Not supported when running outside of Excel")

def xlfWindows(match_type=None, mask=None):
    raise Exception("Not supported when running outside of Excel")

def xlfCaller():
    # type: () -> XLCell
    raise Exception("Not supported when running outside of Excel")

def xlAsyncReturn(async_handle, value):
    raise Exception("Not supported when running outside of Excel")

def xlcAlert(message):
    # type: (str) -> None
    raise Exception("Not supported when running outside of Excel")

def xlcCalculation(calculation_type):
    raise Exception("Not supported when running outside of Excel")

def xlcCalculateNow():
    raise Exception("Not supported when running outside of Excel")

def xlcCalculateDocument():
    raise Exception("Not supported when running outside of Excel")

def xlAbort(retain=True):
    raise Exception("Not supported when running outside of Excel")

def xlSheetNm(sheet_id):
    raise Exception("Not supported when running outside of Excel")

def xlSheetId(sheet_name):
    raise Exception("Not supported when running outside of Excel")

def xlfVolatile(volatile):
    # has no effect when running outside of Excel
    pass

class XLAsyncHandle(object):
    caller = None
    function_name = None

    def __init__(self, *args, **kwargs):
        raise Exception("Not supported when running outside of Excel")

    def set_value(self, value):
        raise Exception("Not supported when running outside of Excel")

    def set_error(self,
                  exc_type,  # type: Type[BaseException]
                  exc_value,  # type: BaseException
                  exc_traceback  # type: types.TracebackType
                  ):
        raise Exception("Not supported when running outside of Excel")

if sys.version_info[:3] >= (3, 5, 1):
    import asyncio

    def get_event_loop():
        # type: () -> asyncio.BaseEventLoop
        """
        Get the async event loop used by PyXLL for scheduling async tasks.

        If called in Excel and the event loop is not already running it is
        started in a background thread.

        If called outside of Excel then the event loop is returned
        without starting it.

        :return: asyncio.AbstractEventLoop
        """
        return asyncio.get_event_loop()

class RTD(object):
    def __init__(self, value=None):
        self.__value = value
        self.__error = None

    def __get_value(self):
        return self.__value

    def __set_value(self, value):
        self.__value = value
        self.__error = None

    value = property(__get_value, __set_value)

    def connect(self):
        """Called when Excel connects to this RTD instance, which occurs shortly after an
        Excel function has returned an RTD object.

        May be overridden in the sub-class.

        Since PyXLL 4.2.0: May be an async method.
        """
        pass

    def disconnect(self):
        """Called when Excel no longer needs the RTD instance. This is usually because there are no longer
        any cells that need it or because Excel is shutting down.

        May be overridden in the sub-class.

        Since PyXLL 4.2.0: May be an async method.
        """
        pass

    def connected(self):
        return False
    connected = property(connected)

    def disconnected(self):
        return False
    disconnected = property(disconnected)

    def set_error(self,
                  exc_type,  # type: Type[BaseException]
                  exc_value,  # type: BaseException
                  exc_traceback  # type: types.TracebackType
                  ):
        """Update Excel with an error. E.g.::

            def update(self):
                try:
                    self.value = get_new_value()
                except:
                    self.set_error(*sys.exc_info())
        """
        self.__error = (exc_type, exc_value, exc_traceback)

class XLCell(object):
    def __init__(self, *args, **kwargs):
        raise Exception("Not supported when running outside of Excel")

    def from_range(range):
        # type: (_ExcelRange) -> XLCell
        raise Exception("Not supported when running outside of Excel")
    from_range = staticmethod(from_range)

    def to_range(self, com_package=None):
        # type: (str) -> _ExcelRange
        """Return an Excel.Range object using the COM package specified.
        :param com_package: COM package to use to return the COM Range object.
                            May be any of:
                              - win32com
                              - comtypes
                              - xlwings
        """
        raise Exception("Not supported when running outside of Excel")

    def options(self,
                type=None,  # type: typing.Union[str, typing.Type]
                auto_resize=None,  # type: bool
                type_kwargs=None,  # type: typing.Dict[str, typing.Any]
                formatter=None  # type: BaseFormatter
                ):  # type: () -> XLCell
        """Set options that control how values are retrieved and set.

        :param type: Type to convert values to when getting.
        :param auto_resize: If True, auto-resize when setting arrays.
        :param type_kwargs: Options for type converter.
        :param formatter: Formatter to apply when setting value.
        :return: Return self so this method can easily be chained.
        """
        return self

    def rows(self):
        # type: () -> int
        """Return the number of rows in the range."""
        raise Exception("Not supported when running outside of Excel")
    rows = property(rows)

    def columns(self):
        # type: () -> int
        """Return the number of columns in the range."""
        raise Exception("Not supported when running outside of Excel")
    columns = property(columns)

    def row(self, i):
        # type: (int) -> XLCell
        """Return a new XLCell for a row of this instance.

        :param i: Index from 0 for the row to return.
        """
        raise Exception("Not supported when running outside of Excel")

    def column(self, i):
        # type: (int) -> XLCell
        """Return a new XLCell for a column of this instance.

        :param i: Index from 0 for the column to return.
        """
        raise Exception("Not supported when running outside of Excel")

    def cell(self, row, column):
        # type: (int, int) -> XLCell
        """Return a new XLCell for an individual cell of this instance.

        :param row: Index from 0 for the row to select.
        :param column: Index from 0 for the column to select.
        """
        raise Exception("Not supported when running outside of Excel")

    def resize(self, rows, columns):
        # type: (int, int) -> XLCell
        """Resize the range.
        The object is updated in-place.

        :param rows: Number of rows to resize to.
        :param columns: Number of columns to resize to.
        """
        raise Exception("Not supported when running outside of Excel")

_pd_pandas = None
_pd_numpy = None
def _pandas_get_imports():
    """Convenience function to lazily import pandas and numpy."""
    global _pd_pandas, _pd_numpy
    if _pd_pandas is None:
        import pandas as pandas_module
        _pd_pandas = pandas_module
    if _pd_numpy is None:
        import numpy as numpy_module
        _pd_numpy = numpy_module
    return _pd_pandas, _pd_numpy

class ObjectCacheKeyError(KeyError):
    """Key not found in object cache"""
    pass

#
# API functions / decorators
#

def get_config():
    # type: () -> configparser.ConfigParser
    """returns the PyXLL config as a ConfigParser.RawConfigParser instance"""
    raise Exception("Not supported when running outside of Excel")

def xl_version():
    # type: () -> float
    """
    returns the version of Excel the addin is running in as a float.

    8.0  => Excel 97
    9.0  => Excel 2000
    10.0 => Excel 2002
    11.0 => Excel 2003
    12.0 => Excel 2007
    14.0 => Excel 2010
    """
    raise Exception("Not supported when running outside of Excel")

def xl_func(signature=None,  # type: str
            category=None,  # type: str
            help_topic="",  # type: str
            thread_safe=False,  # type: bool
            macro=False,  # type: bool
            allow_abort=None,  # type: bool
            volatile=None,  # type: bool
            disable_function_wizard_calc=False,  # type: bool
            disable_replace_calc=False,  # type: bool
            arg_descriptions=None,  # type: typing.Dict[str, str]
            name=None,  # type: str
            auto_resize=None,  # type: bool
            hidden=False,  # type: bool
            transpose=False,  # type: bool
            recalc_on_open=None,  # type: bool
            formatter=None  # type: BaseFormatter
            ):  # type: () -> _Decorator
    """
    Decorator for exposing functions to excel, e.g.:

    @xl_func
    def my_xl_function(a, b, c):
        '''docstrings appear as helptext in excel'''
        return "%s %s %s" % (a, b, c)

    A signature may be provided to give type information for the
    arguments and return type, e.g.:

    @xl_func("string a, int b, float c: string")
    def my_xl_function(a, b, c)
        return "%s %d %f" % (a, b, c)

    Valid types are:
        str, string, int, bool, float, float[], var or types registered
        with xl_arg_type.

    The return type is optional, it will default to var.

    Or where available, type hints may be used:

    @xl_func
    def strlen(x: str) -> int:
        return len(x)

    """
    # xl_func may be called with no arguments as a plain decorator, in which
    # case the first argument will be the function it's applied to.
    if signature is not None and callable(signature):
        return signature

    # or it will eturn a dectorator.
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_arg_doc(arg_name,  # type: str
               docstring  # type: str
               ):  # type: () -> _Decorator
    """
    Decorator for documenting a function's named parameters.
    Must be applied before xl_func.

    eg:

    @xl_func("int a, int b: int")
    @xl_arg_doc("a", "this is the docstring for a")
    @xl_arg_doc("b", "this is the docstring for b")
    def my_xl_function(a, b):
        return a + b

    Alternatively if no docstrings are explicitly supplied
    and the function has a docstring, PyXLL will try and
    find parameter documentation in the docstring.

    @xl_func("int a, int b: int")
    def my_xl_function(a, b):
        '''
        return a + b

        a : this is the docstring for a
        b : this is the docstring for b
        '''
        return a + b

    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_macro(signature=None,  # type: str
             allow_abort=None,  # type: bool
             arg_descriptions=None,  # type: typing.Dict[str, str]
             name=None,  # type: str
             shortcut=None,  # type: str
             transpose=False  # type: bool
             ):  # type: () -> _Decorator
    """
    Decorator for exposing python functions as macros.

    Macros are used like VBA macros and can be assigned to buttons.
    They take no arguments the return value is not used.

    Macros may call macro sheet functions and may call back
    into Excel like menu items.

    eg:
    @xl_macro
    def my_macro():
        win32api.MessageBox(0, "my_macro", "my_macro")

    A signature may be applied to the function, e.g.:

    @xl_macro("string x: int")
    def strlen(x):
        return len(x)

    Or where possible, type hints may be used:

    @xl_macro
    def strlen(x: str) -> int:
        return len(x)

    """
    # xl_macro may be called with no arguments as a plain decorator, in which
    # case the first argument will be the function it's applied to.
    if signature is not None and callable(signature):
        return signature

    # or it will eturn a dectorator.
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_menu(name,  # type: str
            menu=None,  # type: str
            sub_menu=None,  # type: str
            order=None,  # type: int
            sub_order=None,  # type: int
            menu_order=None,  # type: int
            allow_abort=None,  # type: bool
            shortcut=None  # type: str
            ):  # type: () -> _Decorator
    """
    Decorator for creating custom menu items.

    eg.

    @xl_menu("My menu item")
    def my_menu_item():
        print "my menu item was called"

    Adds a menu item 'My menu item' to the default menu (PyXLL or addin
    name).

    @xl_menu("My menu item", menu="My Menu")
    def my_menu_item():
        print "my menu item was called"

    Creates a new menu "My Menu" and adds "My menu item" to it.

    @xl_menu("Mysub-menu item", menu="My Menu", sub_menu="My Sub Menu")
    def my_menu_item():
        print "my menu item was called"

    Creates a new sub-menu "My Sub Menu" and adds "My sub-menu item"
    to it.
    If the menu My Menu didn't already exist, it would create it too.
    """
    def dummy_decorator(func):
        return func
    return dummy_decorator

def xl_license_notifier(func):
    # type: (_Function) -> _Function
    """
    Decorator for callbacks to notify user code of the current state of
    the license.

    The decorated function must be of the form:
    def callback(string name, datetime.date expdate, int days_left, bool is_perpetual)

    All registered callbacks are called only once when the license is
    checked at the time pyxll is first loaded.

    If the license is perpetual, expdate will be end date of the maintenance contract
    and days_left will be the days between the pyxll build date and expdate.
    """
    return func

def xl_on_close(func):
    # type: (_Function) -> _Function
    """
    Decorator for callbacks that should be called when Excel is about
    to be closed.

    Even after this function has been called, it's possible Excel won't
    actually close as the user may veto it.

    The function should take no arguments.
    """
    return func

def xl_on_reload(func):
    # type: (_Function) -> _Function
    """
    Decorator for callbacks that should be called after a reload is
    attempted.

    The callback takes a list of tuples of three three items:
    (modulename, module, exc_info)

    When a module has been loaded successfully, exc_info is None.
    When a module has failed to load, module is None and exc_info
    is the exception information (exc_type, exc_value, exc_traceback).
    """
    return func

def xl_on_open(func):
    # type: (_Function) -> _Function
    """
    Decorator for callbacks that should be called after PyXLL has
    been opened and the user modules have been imported.

    The callback takes a list of tuples of three three items:
    (modulename, module, exc_info)

    When a module has been loaded successfully, exc_info is None.
    When a module has failed to load, module is None and exc_info
    is the exception information (exc_type, exc_value, exc_traceback).
    """
    return func

_async_call_warning_enabled = True
def async_call(func, *args, **kwargs):
    """
    Schedule a function to be called after the current Excel
    calculation cycle has completed.

    The function is called in an Excel macro context with automatic
    calculation disabled, so it is safe to use :py:func:`xl_app` and
    other COM and macro functions.

    This can be used by worksheet functions that need to modify the worksheet
    where calling back into Excel would fail or cause a deadlock.

    NOTE: In the stubs version (not embedded in PyXLL) the function
    is called immediately.

    :param func: Function or callable object to call in an Excel macro context
                 at some time in the near future.
    """
    global _async_call_warning_enabled
    if _async_call_warning_enabled:
        _log.warning("pyxll.async_call is deprecated and will be removed in a future release. "
                     "Use pyxll.schedule_call instead.")
        _async_call_warning_enabled = False
    func(*args, **kwargs)

def schedule_call(func, *args, **kwargs):
    """
    Schedule a function to be called after the current Excel
    calculation cycle has completed.

    The function is called in an Excel macro context with automatic
    calculation disabled, so it is safe to use :py:func:`xl_app` and
    other COM and macro functions.

    This can be used by worksheet functions that need to modify the worksheet
    where calling back into Excel would fail or cause a deadlock.

    From Python 3.7 onwards when called from the PyXLL asyncio event loop and
    'nowait' is not set this function returns an asyncio.Future. This future
    can be awaited on to get the result of the call.

    NOTE: In the stubs version (not embedded in PyXLL) the function
    is called immediately.

    :param func: Function or callable object to call in an Excel macro context
                 at some time in the near future.

    :param *args: Arguments to be passed to the the function.

    :param delay: Delay in seconds to wait before calling the function.

    :param nowait: Do not return a Future even if called from the asyncio event loop.

    :param retries: Integer number of times to retry.

    :param retry_delay: Time in seconds to wait between retries.

    :param retry_backoff: Multiplier to apply to 'retry_delay' after each retry. This
                          can be used to increase the time between each retry by setting
                          'retry_backoff' to > 1.0.

    :param retry_filter: Callable that received the exception value in the case of an
                         error. It should return True if a retry should be attempted
                         or False otherwise.

    :param disable_calculation: Disable automatic calculations while the callback is being called.
                                This switches the Excel calculation mode to manual and restores it
                                to its previous mode after the call is complete.

    :param disable_screen_updating: Disable Excel's screen updating while the callback is being called.
                                    Screen updating is restored to its previous mode after the call is
                                    complete.

    .. warning::

        This function doesn't allow passing keyword arguments to the schedule function.
        To do that, use functools.partial().::

            # Will schedule "print("Hello", flush=True)"
            schedule_call(functools.partial(print, "Hello", flush=True))
    """

    # In the stubs package the function gets called immediately, regardless
    # of the delay passed in or what thread we might be running in.
    result = func(*args)

    if not nowait:
        # Check to see if we are running in an asyncio event loop
        try:
            import asyncio
            loop = asyncio.get_running_loop()
        except (ImportError, AttributeError, RuntimeError):
            return

        # We are so return the result in a Future
        future = loop.create_future()
        future.set_result(result)
        return future

_ribbon_xml = None

_default_ribbon_xml = """<?xml version="1.0" ?>
<customUI xmlns="http://schemas.microsoft.com/office/2006/01/customui" loadImage="pyxll.load_image">
<ribbon><tabs/></ribbon>
</customUI>
"""

def _xml_to_dom(xml):
    """Takes xml as a string or dom and returns a document object"""
    if not isinstance(xml, minidom.Document):
        return minidom.parseString(xml)
    return xml

def _validate_ribbon_xml(xml):
    """Tests the ribbon xml to make sure it looks reasonable.
    Returns validated xml as text.
    """

    xml = _xml_to_dom(xml)

    if not xml.documentElement:
        raise AssertionError("Ribbon XML is missing a root document element")

    if not xml.documentElement.tagName == u"customUI":
        raise AssertionError("Ribbon XML document element is expected to be 'customUI' "
                             "(not '%s'" % xml.documentElement.tagName)

    def _assert_unique_attr(element, attr, error, values={}):
        elements = [element]
        while elements:
            element = elements[0]
            elements = elements[1:] + list(element.childNodes or [])
            attributes = element.attributes or {}
            value = getattr(attributes.get(attr, None), "value", None)
            if value:
                if value in values:
                    raise AssertionError(error % {"attr": attr, "value": value})
                values[value] = None

    _assert_unique_attr(xml.documentElement,
                        "id",
                        "Duplicate %(attr)s attribute '%(value)s' found.")

    def _assert_at_most_one(element, tag_name, error):
        children = {}
        for child in element.childNodes:
            if child.nodeType != child.ELEMENT_NODE:
                continue
            children.setdefault(child.tagName, [])
            children[child.tagName].append(child)
        tag_children = children.get(tag_name, [])
        if len(tag_children) > 1:
            raise AssertionError(error)
        if tag_children:
            return tag_children[0]

    ribbon = _assert_at_most_one(xml.documentElement,
                                 "ribbon",
                                 "'customUI' element in ribbon XML should have a single ribbon node")

    if ribbon:
        _assert_at_most_one(ribbon,
                            "tabs",
                            "'ribbon' element in ribbon XML should have a single tabs node)")

    return xml.toxml()

def set_ribbon_tab(xml, tab_id=None, reload=True):
    # type: (Union[str, minidom.Document], str, bool) -> None
    """
    Sets a tab in the ribbon using an xml fragment.

    :param xml: Ribbon xml as a string containing at least one tab element.
    :param tab_id: Id of tab to add if multiple tabs exist in the xml.
    :param reload: If true the ribbon will be refreshed immediately.
    """
    xml = _xml_to_dom(xml)

    if tab_id:
        tab_id = str(tab_id)
        for new_tab in xml.getElementsByTagName("tab"):
            if str(new_tab.getAttribute("id")) == tab_id:
                break
        else:
            raise KeyError("Tab '%s' not found" % tab_id)
    else:
        new_tabs = xml.getElementsByTagName("tab")
        if not new_tabs:
            raise RuntimeError("No 'tab' elements found")
        new_tab = new_tabs[0]
        tab_id = str(new_tab.getAttribute("id") or "")

    new_xml = get_ribbon_xml()
    if not new_xml:
        new_xml = _default_ribbon_xml
    new_xml = _xml_to_dom(new_xml)

    tabs = new_xml.getElementsByTagName("tabs")
    if tabs:
        tabs = tabs[0]
    else:
        ribbon = new_xml.getElementsByTagName("ribbon")
        if ribbon:
            ribbon = ribbon[0]
        else:
            ribbon = new_xml.createElement("ribbon")
            new_xml.documentElement.appendChild(ribbon)
        tabs = new_xml.createElement("tabs")
        ribbon.appendChild(tabs)

    if tab_id:
        for tab in tabs.childNodes:
            if tab.nodeType == tab.ELEMENT_NODE \
            and str(tab.tagName) == "tab" \
            and str(tab.getAttribute("id")) == tab_id:
                tabs.replaceChild(new_tab, tab)
                break
        else:
            tabs.appendChild(new_tab)
    else:
        tabs.appendChild(new_tab)

    set_ribbon_xml(new_xml, reload=reload)

def remove_ribbon_tab(tab_id, reload=True):
    # type: (str, bool) -> None
    """
    Removes a tab previously added to the ribbon.

    :param tab_id: Id of tab to remove
    :param reload: If true the ribbon will be refreshed immediately.
    :return: True if a tab was removed, False otherwise.
    """
    new_xml = get_ribbon_xml()
    if not new_xml:
        return False

    new_xml = minidom.parseString(new_xml)
    tabs = new_xml.getElementsByTagName("tab")
    if not tabs:
        return False

    updated = False
    tab_id = str(tab_id)
    for tab in tabs:
        if str(tab.getAttribute("id")) == tab_id:
            tab.parentNode.removeChild(tab)
            updated = True

    if not updated:
        return False

    set_ribbon_xml(new_xml, reload=reload)

def get_ribbon_xml():
    # type: () -> str
    """Returns the ribbon XML currenly in use by PyXLL."""
    return _ribbon_xml

def set_ribbon_xml(xml, reload=True):
    # type: (Union[str, minidom.Document], bool) -> None
    """
    Sets the XML used by PyXLL for customizing the ribbon.

    :param xml: XML document to set as the current ribbon
    :param reload: If true the ribbon will be refreshed immediately.
    """
    global _ribbon_xml
    _ribbon_xml = _validate_ribbon_xml(xml)
    if reload:
        # com_reload only reloads the COM part of the addin, which is
        # responsible for the ribbon. This doesn't reload the rest of
        # the PyXLL addin so no functions will get re-registered.
        com_reload()

class ErrorContext:
    """Context object passed to the PyXLL error handler."""

    class Type:
        """Type to indicate the origination of the error."""
        UDF = "udf"
        MACRO = "macro"
        MENU = "menu"
        RIBBON = "ribbon"
        IMPORT = "import"

    def __init__(self, error_type, function_name=None, import_errors=None):
        self.error_type = error_type
        self.function_name = function_name
        self.import_errors = import_errors

def error_handler(context, exc_type, exc_value, exc_traceback):
    """Standard PyXLL error handler."""
    # For UDFs return a preview of the error as a single line
    if context.error_type in (ErrorContext.Type.UDF, ErrorContext.Type.MACRO):
        error = "##" + getattr(exc_type, "__name__", "Error")
        msg = str(exc_value)
        if msg:
            error += ": " + msg
        return error

    # For menus and ribbon functions display an error message.
    if context.error_type in (ErrorContext.Type.MENU, ErrorContext.Type.RIBBON):
        message = ""
        if context.function_name:
            message = "Error calling '%s'\n\n" % context.function_name
        elif context.error_type == ErrorContext.Type.RIBBON:
            message = "PyXLL Ribbon Error\n\n"
        exc_type_name = getattr(exc_type, "__name__", "Exception")
        message += str(exc_type_name) + (str(exc_value) and (": " + str(exc_value)) or "") + "\n\n"

        exc_instance = exc_value
        if not isinstance(exc_instance, BaseException):
            try:
                exc_instance = exc_type(exc_value)
            except:
                exc_instance = None

        message += "".join(traceback.format_exception(exc_type, exc_instance, exc_traceback))
        caption = "PyXLL: " + ((context.error_type == ErrorContext.Type.MENU and "Menu") or "Ribbon") + " Error"
        #                             MB_SETFOREGROUND | MB_ICONHAND | MB_HELP
        message_box(message, caption, 0x00010000 | 0x00000010 | 0x00004000)
        return

    if context.error_type == ErrorContext.Type.IMPORT:
        lines = ["Error importing Python modules"]
        if context.import_errors:
            lines.append("")
            for modulename, exc_info in context.import_errors:
                exc_type, exc_value, exc_traceback = exc_info
                lines.append("Error importing '%s': %s" % (modulename, exc_value))
        message = "\n".join(lines)
        #                                                             MB_SETFOREGROUND | MB_ICONHAND | MB_HELP
        message_box(message, "PyXLL: Error importing Python modules", 0x00010000 | 0x00000010 | 0x00004000)
        return

def error_handler_quiet(context, exc_type, exc_value, exc_traceback):
    """PyXLL error handler that doesn't display any error dialogs"""
    # For UDFs return a preview of the error as a single line
    if context.error_type in (ErrorContext.Type.UDF, ErrorContext.Type.MACRO):
        error = "##" + getattr(exc_type, "__name__", "Error")
        msg = str(exc_value)
        if msg:
            error += ": " + msg
        return error

# for backwards compatibility with older pyxll.cfg files
error_to_string = error_handler

def _wrap_iunknown(unk, no_dynamic_dispatch=False):
    """Wrap a pythoncom PyIUnknown object into a win32com.Dispatch"""
    # Get the PyIDispatch object
    import pythoncom
    disp = unk.QueryInterface(pythoncom.IID_IDispatch)

    # Try to wrap using the existing wrapper classes (or generate them if
    # they don't exist)
    try:
        from win32com.client.gencache import EnsureDispatch
        return EnsureDispatch(disp)
    except:
        if no_dynamic_dispatch:
            raise
        pass

    # If we can't use a generated wrapper then use a dynamic Dispatch wrapper.
    # This will work but won't add constants to win32com.client.constants.
    import win32com
    _log.warning("win32com.client.Dispatch failed. win32com.client.dynamic.Dispatch will be used instead.")
    _log.warning("Delete your gen_py folder '%s' as it may have become corrupted" % win32com.__gen_path__)
    from win32com.client.dynamic import Dispatch as DynamicDispatch
    return DynamicDispatch(disp)

class BaseFormatter(object):
    """Base class used for formatting Excel ranges.
    """
    def __get_numpy(cls):
        try:
            return cls.__np
        except AttributeError:
            try:
                import numpy
                cls.__np = numpy
            except ImportError:
                cls.__np = None
        return cls.__np
    __get_numpy = classmethod(__get_numpy)

    def __is_sequence(cls, x):
        np = cls.__get_numpy()
        if np:
            return isinstance(x, (list, tuple, np.ndarray))
        return isinstance(x, (list, tuple))
    __is_sequence = classmethod(__is_sequence)

    def __resize_array(cls, value, cell, datatype, datatype_ndim, transpose):
        # If the data type is object and it's not an array, don't check if the object
        # is a sequence just convert it to a 1x1 array.
        if datatype == "object" and datatype_ndim == 0:
            value = [[value]]

        # If the data type is a 1d array convert it to 1xN row array
        if datatype_ndim == 1:
            value = [value]

        # Make sure the value is a 2d array
        if not cls.__is_sequence(value):
            value = [value]
        if len(value) == 0:
            value = [[None]]
        if not cls.__is_sequence(value[0]):
            value = [value]

        # Transpose the array before matching it to the cell range
        if transpose:
            value = list(zip(*value))

        # Pad or trim the array to match the cell range
        num_rows = cell.rows
        num_cols = cell.columns
        new_value = [None] * num_rows
        for r in range(num_rows):
            row = []
            if r < len(value):
                row = value[r]
            if len(row) > num_cols:
                row = row[:num_cols]
            if len(row) < num_cols:
                row = list(row) + ([None] * (num_cols - len(row)))
            new_value[r] = row

        return new_value
    __resize_array = classmethod(__resize_array)

    def apply(self, cell, value=None, datatype=None, datatype_ndim=0, datatype_kwargs={}, transpose=False):
        """Apply formatting to a cell or range of cells.

        :param cell: XLCell instance to by formatted.
        :param value: Value being set on the cell(s).
        :param datatype: Data-type as specified as the return type when using @xl_func.
        :param datatype_ndim: Number of dimensions if the datatype is an array.
        :param datatype_kwargs: Data-type keyword arguments.
        :param transpose: True if the value should be transposed before styling.
        """
        if self.apply_cell is not BaseFormatter.apply_cell:
            value = self.__resize_array(value, cell, datatype, datatype_ndim, transpose)
            for i, row_value in enumerate(value):
                    for j, cell_value in enumerate(row_value):
                        self.apply_cell(cell.cell(i, j),
                                        cell_value,
                                        datatype=datatype,
                                        datatype_kwargs=datatype_kwargs)

    def apply_cell(cell, value=None, datatype=None, datatype_kwargs={}):
        """Called for each cell to apply any formatting.

        For most Formatter classes this is the only method that needs to
        be overridden.

        :param cell: XLCell instance to by formatted.
        :param value: Value being set on the cell(s).
        :param datatype: Data-type as specified as the return type when using @xl_func.
        :param datatype_kwargs: Data-type keyword arguments.
        """
        pass
    apply_cell = staticmethod(apply_cell)

    def clear(cell):
        """Clears any formatting from a cell or range of cells."""
        r = cell.to_range()
        r.Style = "Normal"
    clear = staticmethod(clear)

    def rgb(red, green, blue):
        """Return a color number from RGB values.
        Note Excel uses 'BGR' instead of the more usual RGB.
        """
        return (red & 0xff) | ((green & 0xff) << 8) | ((blue & 0xff) << 16)
    rgb = staticmethod(rgb)

    def apply_style(cell, style):
        """Apply a formatting style dictionary to a cell."""
        if not style:
            return

        r = cell.to_range()
        interior_color = style.get("interior_color", None)
        if interior_color is not None:
            r.Interior.Color = interior_color

        text_color = style.get("text_color", None)
        if text_color is not None:
            r.Font.Color = text_color

        bold = style.get("bold", None)
        if bold is not None:
            r.Font.Bold = bold

        italic = style.get("italic", None)
        if italic is not None:
            r.Font.Italic = italic

        font_size = style.get("font_size", None)
        if font_size is not None:
            r.Font.Size = font_size

        number_format = style.get("number_format", None)
        if number_format is not None:
            r.NumberFormat = number_format

        auto_fit = style.get("auto_fit", False)
        if auto_fit:
            r.AutoFit()
    apply_style = staticmethod(apply_style)

class FormatterCollection(BaseFormatter):

    def __init__(self, formatters=[]):
        self.__formatters = formatters

    def apply(self, cell, value=None, datatype=None, datatype_ndim=0, datatype_kwargs={}, transpose=False):
        for formatter in self.__formatters:
            formatter.apply(cell,
                            value,
                            datatype=datatype,
                            datatype_ndim=datatype_ndim,
                            datatype_kwargs=datatype_kwargs,
                            transpose=transpose)

    def clear(self, cell):
        # Only call clear once unless implemented differently from the base class
        cleared = False
        for formatter in self.__formatters:
            if not cleared or formatter.clear is not BaseFormatter.clear:
                formatter.clear(cell)
                cleared = True

    def __add__(self, other):
        if isinstance(other, dict):
            other = Formatter(**other)
        if not isinstance(other, BaseFormatter):
            raise TypeError("Can't add non-formatter object to a formatter.")
        return FormatterCollection(self.__formatters + [other])

    def __iadd__(self, other):
        if isinstance(other, dict):
            other = Formatter(**other)
        if not isinstance(other, BaseFormatter):
            raise TypeError("Can't add non-formatter object to a formatter.")
        self.__formatters.append(other)
        return self

class Formatter(BaseFormatter):
    """Formatter for formatting values returned via xl_func, or using XLCell.options.

    Use Formatter.rgb(red, green, blue) for constructing color values.

    Formatters may be combined by adding them together.

    :param interior_color: Value to set the interior color to.
    :param text_color: Value to set the text color to.
    :param bold: If true, sent the text style to bold.
    :param italic: If true, sent the text style to italic.
    :param font_size: Value to set the font size to.
    :param number_format: Excel number format to use.
    :param auto_fit: Auto-fit to the content of the cells. May be True (fit column width),
                     False (don't fit), 'columns' (fit column width), 'rows' (fit row width),
                     'both' (fit column and row width).
    """

    def __init__(self,
                 interior_color=None,
                 text_color=None,
                 bold=None,
                 italic=None,
                 font_size=None,
                 number_format=None,
                 auto_fit=None):
        BaseFormatter.__init__(self)
        self.__style = {}
        if interior_color is not None:
            self.__style["interior_color"] = interior_color
        if text_color is not None:
            self.__style["text_color"] = text_color
        if bold is not None:
            self.__style["bold"] = bold
        if italic is not None:
            self.__style["italic"] = italic
        if font_size is not None:
            self.__style["font_size"] = font_size
        if number_format is not None:
            self.__style["number_format"] = number_format
        if auto_fit is not None:
            self.__style["auto_fit"] = auto_fit

    def __add__(self, other):
        if type(self) == type(other) == Formatter:
            style = dict(self.__style)
            style.update(other.__style)
            return Formatter(**style)
        elif isinstance(other, dict):
            return self + Formatter(**other)
        elif not isinstance(other, BaseFormatter):
            raise TypeError("Can't add non-formatter object to a formatter.")
        return FormatterCollection([self, other])

    def apply(self, cell, value=None, datatype=None, datatype_ndim=0, datatype_kwargs={}, transpose=False):
        # Update the style to the range
        self.apply_style(cell, self.__style)

        # Apply any styles from the base class (this handles calling apply_cell if necessary
        # and so should be done after applying the main style to the whold range).
        BaseFormatter.apply(self,
                            cell,
                            value,
                            datatype=datatype,
                            datatype_ndim=datatype_ndim,
                            datatype_kwargs=datatype_kwargs,
                            transpose=transpose)

class DateFormatter(Formatter):
    """Formatter for dates, times and datetimes.

    All formats are in the standard Python datetime format.

    This formatter tests the values and applies the relevant
    number format according to the type.

    :param date_format: Format used for date values.
    :param time_format: Format used for time values.
    :param datetime_format: Format used for datetime values.
    """

    def __init__(self,
                 date_format="%Y-%m-%d",
                 time_format="%H:%M:%S",
                 datetime_format=None,
                 **kwargs):
        Formatter.__init__(self, **kwargs)

        # Convert the Python date format to an Excel number format
        if not datetime_format:
            datetime_format = "%s %s" % (date_format, time_format)
        self.__date_number_format = self.__to_number_format(date_format)
        self.__time_number_formmat = self.__to_number_format(time_format)
        self.__datetimetime_number_formmat = self.__to_number_format(datetime_format)

    def __to_number_format(date_format):
        """Convert a Python date format to an Excel number format."""
        number_format = date_format.replace("%Y", "yyyy")
        number_format = number_format.replace("%y", "yy")
        number_format = number_format.replace("%m", "mm")
        number_format = number_format.replace("%b", "mmm")
        number_format = number_format.replace("%d", "dd")
        number_format = number_format.replace("%H", "hh")
        number_format = number_format.replace("%M", "mm")
        number_format = number_format.replace("%S", "ss")
        return number_format
    __to_number_format = staticmethod(__to_number_format)

    def apply_cell(self, cell, value=None, datatype=None, datatype_kwargs={}):
        """Apply the relevant formatting."""
        if datatype is None or "var":
            if isinstance(value, datetime.datetime):
                datatype = "datetime"
            elif isinstance(value, datetime.date):
                datatype = "date"
            elif isinstance(value, datetime.time):
                datatype = "time"

        number_format = None
        if datatype == "datetime":
            number_format = self.__datetimetime_number_formmat
        elif datatype == "date":
            number_format = self.__date_number_format
        elif datatype == "time":
            number_format = self.__time_number_formmat

        if number_format is not None:
            self.apply_style(cell, {"number_format": number_format})

class ConditionalFormatterBase:

    def get_formatters(self, df):
        """Return a DataFrame the same dimensions as 'df' with the values
        set to a 'Formatter' where formatting should be applied and False
        or None otherwise.
        """
        raise NotImplementedError()

class ConditionalFormatter(ConditionalFormatterBase):

    def __init__(self, expr, formatter, columns=None, **kwargs):
        """
        A ConditionalFormatter for use with DataFrameFormatter.

        :param expr: Boolean expression for selecting rows to which the formatter will apply.
        :param formatter: Formatter that will be applied to the selected cells.
        :param columns: Column name or list of columns that the formatter will be applied to.
                        May also be a callable, in which case it should accept a DataFrame and
                        return a column or list of columns.
        :param kwargs: Additional arguments passed to DataFrame.eval when selecting the rows
                       to apply the formatter to.
        """
        if "inplace" in kwargs:
            raise TypeError("inplace is an invalid keyword argument for ConditionalFormatter.")
        self.__expr = expr
        self.__columns = columns
        self.__kwargs = kwargs

        if isinstance(formatter, dict):
            formatter = Formatter(**formatter)
        self.__formatter = formatter

    def get_formatters(self, df):
        """See ConditionalFormatterBase.get_formatters"""
        # Create an empty DataFrame the same size as the source
        pd, np = _pandas_get_imports()
        formatters_df = pd.DataFrame(False, index=df.index, columns=df.columns, dtype=object)

        # Query which rows should be included
        row_mask = df.eval(self.__expr, **self.__kwargs)
        if not row_mask.any():
            return None

        col_mask = None
        if self.__columns:
            def _update_col_mask(col, col_mask):
                if callable(col):
                    col = col(df)
                    _update_col_mask(col, col_mask)
                elif isinstance(col, (list, tuple)):
                    for c in col:
                        _update_col_mask(c, col_mask)
                else:
                    if col not in col_mask.index:
                        raise RuntimeError("Invalid column '%s' found when applying conditional formatting." % str(col))
                    col_mask[col] = True

            col_mask = pd.Series(False, index=df.columns)
            _update_col_mask(self.__columns, col_mask)

        if col_mask is None:
            formatters_df.loc[row_mask] = self.__formatter
            return formatters_df

        formatters_df.loc[row_mask, col_mask] = self.__formatter
        return formatters_df

class DataFrameFormatter(Formatter):
    """Formatter for DataFrames.

    For each argument expecting a Formatter, a dict may also be provided.

    When a list of formatters is used (e.g. for the row or index formatters)
    the formatters will cycle through the list and repeat. For example, to
    format a table with striped rows only two row formatters are needed.

    :param rows: Formatter or list of formatters to be applied to the rows.
    :param header: Formatter to use for the header column names.
    :param index: Formatter or list of formatters to be applied to the index.
    :param columns: Dict of column name to formatter or list of formatters to
                    be applied for specific columns (in addition to the any
                    row formatters).
    :param conditional_formatters: A list of ConditionalFormatters to be applied
                                   in order after any other formatting has
                                   been applied.
    :param kwargs: Additional Formatter kwargs that will affect the entire
                   formatted range.
    """

    default_header_formatter = Formatter(interior_color=0x8ED0A9)

    default_index_formatter = Formatter(interior_color=0x8ED0A9)

    default_row_formatters = [
        Formatter(interior_color=0xDBF1E4),
        Formatter(interior_color=0xF1F9F4),
    ]

    def __init__(self,
                 rows=default_row_formatters,
                 header=default_header_formatter,
                 index=default_index_formatter,
                 columns=None,
                 conditional_formatters=None,
                 **kwargs):
        Formatter.__init__(self, **kwargs)

        # row is a list of formatters to be used for each row in the DataFrame
        self.__row_formatters = None
        if rows:
            if not isinstance(rows, (list, tuple)):
                rows = [rows]
            self.__row_formatters = []
            for formatter in rows:
                formatter = self.__to_formatter(formatter)
                self.__row_formatters.append(formatter)

        self.__header_formatter = None
        if header:
            self.__header_formatter = self.__to_formatter(header)

        # index is a list of formatters to be used for each row in the index
        self.__index_formatters = None
        if index:
            if not isinstance(index, (list, tuple)):
                index = [index]
            self.__index_formatters = []
            for formatter in index:
                formatter = self.__to_formatter(formatter)
                self.__index_formatters.append(formatter)

        # columns is a dict of columns to formatters or list of formatters
        self.__column_formatters = None
        if columns:
            if not isinstance(columns, dict):
                raise TypeError("Expected 'columns' to be a dict of formatters")

            self.__column_formatters = {}
            for key, formatters in columns.items():
                if not isinstance(formatters, list):
                    formatters = [formatters]
                self.__column_formatters[key] = []
                for formatter in formatters:
                    formatter = self.__to_formatter(formatter)
                    self.__column_formatters[key].append(formatter)

        # Conditional formatters is a list of formatters to be applied in order
        self.__conditional_formatters = []
        if conditional_formatters is not None and not isinstance(conditional_formatters, (list, tuple)):
            raise TypeError("Expected 'conditional_formatters' to be a list of ConditionalFormatters")
        if conditional_formatters:
            for formatter in conditional_formatters:
                if isinstance(formatter, tuple):
                    formatter = ConditionalFormatter(*formatter)
                elif isinstance(formatter, dict):
                    formatter = ConditionalFormatter(**formatter)
                if not isinstance(formatter, ConditionalFormatterBase):
                    raise TypeError("Expected 'conditional_formatters' to be a list of ConditionalFormatters")
                self.__conditional_formatters.append(formatter)

    def __to_formatter(formatter):
        """helper to convert dict to formatter"""
        if isinstance(formatter, dict):
            formatter = Formatter(**formatter)
        return formatter
    __to_formatter = staticmethod(__to_formatter)

    def apply(self, cell, value=None, datatype=None, datatype_ndim=0, datatype_kwargs={}, transpose=False):
        Formatter.apply(self,
                        cell,
                        value=value,
                        datatype=datatype,
                        datatype_ndim=datatype_ndim,
                        datatype_kwargs=datatype_kwargs,
                        transpose=transpose)

        if datatype != "dataframe" or datatype_ndim != 0:
            _log.warning("DataFrameFormatter applied to a function without return type 'dataframe': %s" % type(datatype))
            return

        pd, np = _pandas_get_imports()
        if not isinstance(value, pd.DataFrame):
            _log.warning("DataFrameFormatter applied to a non-DataFrame result: %s" % type(value))
            return

        df = value
        df_to_array = get_type_converter(datatype, "__internal__", src_kwargs=datatype_kwargs)
        df_array = df_to_array(value)

        header_rows = 0
        if datatype_kwargs.get("columns", True):
            header_rows = 1
            if isinstance(df.columns, pd.MultiIndex):
                header_rows = len(df.columns.levels)

        index_cols = 0
        if datatype_kwargs.get("index", False):
            index_cols = 1
            if isinstance(df.index, pd.MultiIndex):
                index_cols = len(df.index.levels)

        num_rows = len(df.index)
        num_cols = len(df.columns)

        # Make sure the area we format is within the original range
        if transpose:
            max_rows = cell.columns
            max_cols = cell.rows
        else:
            max_rows = cell.rows
            max_cols = cell.columns

        if (num_rows + header_rows) > max_rows:
            diff = (num_rows + header_rows) - max_rows
            deleted_rows = min(num_rows, diff)
            num_rows -= deleted_rows
            diff -= deleted_rows
            header_rows -= min(header_rows, diff)

        if (num_cols + index_cols) > max_cols:
            diff = (num_cols + index_cols) - max_cols
            deleted_cols = min(diff, num_cols)
            num_cols -= deleted_cols
            diff -= deleted_cols
            index_cols -= min(index_cols, diff)

        # Helper for transposing a range relative to the root range
        def _transpose(range, transpose):
            if not transpose:
                return range
            r = range.rect.first_row - cell.rect.first_row
            c = range.rect.first_col - cell.rect.first_col
            return cell.offset(c, r).resize(range.columns, range.rows)

        if self.__header_formatter and header_rows and (num_cols or index_cols):
            header_range = cell.resize(header_rows, num_cols + index_cols)
            self.__header_formatter.apply(_transpose(header_range, transpose),
                                          df_array[:header_rows],
                                          datatype="var",
                                          datatype_ndim=2,
                                          transpose=transpose)

        if self.__row_formatters and num_rows and (num_cols or index_cols):
            if len(self.__row_formatters) == 1:
                rows_range = cell.offset(header_rows, 0).resize(num_rows, num_cols + index_cols)
                formatter = self.__row_formatters[0]
                formatter.apply(_transpose(rows_range, transpose),
                                df_array[header_rows:num_rows+header_rows],
                                datatype="var",
                                datatype_ndim=2,
                                transpose=transpose)
            else:
                for i, row in enumerate(df_array[header_rows:num_rows+header_rows]):
                    row_range = cell.offset(i + header_rows, 0).resize(1, num_cols + index_cols)
                    formatter = self.__row_formatters[i % len(self.__row_formatters)]
                    formatter.apply(_transpose(row_range, transpose),
                                    df_array[i+header_rows],
                                    datatype="var",
                                    datatype_ndim=1,
                                    transpose=transpose)

        if self.__index_formatters and index_cols and num_rows:
            if len(self.__index_formatters) == 1:
                index_range = cell.offset(header_rows, 0).resize(num_rows, index_cols)
                formatter = self.__index_formatters[0]
                formatter.apply(_transpose(index_range, transpose),
                                [x[:index_cols] for x in df_array[header_rows:num_rows+header_rows]],
                                datatype="var",
                                datatype_ndim=2,
                                transpose=transpose)
            else:
                for i, row in enumerate(df_array[header_rows:num_rows+header_rows]):
                    index_range = cell.offset(i + header_rows, 0).resize(1, index_cols)
                    formatter = self.__index_formatters[i % len(self.__index_formatters)]
                    formatter.apply(_transpose(index_range, transpose),
                                    df_array[i+header_rows][:index_cols],
                                    datatype="var",
                                    datatype_ndim=1,
                                    transpose=transpose)

        if self.__column_formatters and num_rows:
            for col, formatters in self.__column_formatters.items():
                try:
                    col_idx = df.columns.get_loc(col)
                except KeyError:
                    continue

                if col_idx >= num_cols:
                    continue

                if len(formatters) == 1:
                    col_range = cell.offset(header_rows, col_idx + index_cols).resize(num_rows, 1)
                    formatter = formatters[0]
                    formatter.apply(_transpose(col_range, transpose),
                                    [[x[col_idx+index_cols]] for x in df_array[header_rows:num_rows+header_rows]],
                                    datatype="var",
                                    datatype_ndim=2,
                                    transpose=transpose)
                else:
                    for i, row in enumerate(df_array[header_rows:num_rows+header_rows]):
                        cel_range = cell.offset(i + header_rows, col_idx + index_cols)
                        formatter = formatters[i % len(formatters)]
                        formatter.apply(_transpose(cel_range, transpose),
                                        df_array[header_rows+i][col_idx+index_cols],
                                        datatype="var",
                                        datatype_ndim=0,
                                        transpose=transpose)

        # Apply the conditional formatters if there are any
        if self.__conditional_formatters and num_rows:
            to_array = get_type_converter("dataframe", "__internal__", src_kwargs={"index": False, "columns": False})
            for conditional_formatter in self.__conditional_formatters:
                formatter_df = conditional_formatter.get_formatters(df)
                if formatter_df is None:
                    continue

                if df.shape != formatter_df.shape:
                    raise RuntimeError("A ConditionalFormatter returned a DataFrame of the wrong shape.")

                formatter_array = to_array(formatter_df)
                for r, row in enumerate(formatter_array[:num_rows]):
                    for c, formatter in enumerate(row[:num_cols]):
                        if not formatter or pd.isnull(formatter):
                            continue

                        formatter = self.__to_formatter(formatter)
                        cell_to_format = cell.offset(header_rows + r, index_cols + c)
                        formatter.apply(_transpose(cell_to_format, transpose),
                                        df_array[header_rows + r][index_cols + c],
                                        datatype="var",
                                        datatype_ndim=0,
                                        transpose=transpose)

CTPDockPositionLeft = 0
CTPDockPositionTop = 1
CTPDockPositionRight = 2
CTPDockPositionBottom = 3
CTPDockPositionFloating = 4

class CTPBridgeBase:
    """Base class of bridges between the Python UI toolkits
    and PyXLL's Custom Task Panes.
    """

    def __init__(self, control):
        self.__timer_interval = 0.1
        self.__has_focus = False
        self.control = control

    def close(self):
        pass

    def get_hwnd(self):
        raise NotImplemented()

    def get_title(self):
        pass

    def pre_attach(self, hwnd):
        pass

    def post_attach(self, hwnd):
        pass

    def on_close(self):
        pass

    def on_window_closed(self):
        pass

    def on_window_destroyed(self):
        pass

    def process_message(self, hwnd, msg, wparam, lparam):
        pass

    def translate_accelerator(self, hwnd, msg, wparam, lparam, modifier):
        pass

    def __set_has_focus(self, has_focus):
        self.__has_focus = has_focus

    def __get_has_focus(self):
        return self.__has_focus

    has_focus = property(__get_has_focus, __set_has_focus)

    def __set_timer_interval(self, interval):
        self.__timer_interval = interval

    def __get_timer_interval(self):
        return self.__timer_interval

    timer_interval = property(__get_timer_interval, __set_timer_interval)

    def on_timer(self):
        pass

def create_ctp(control,
               title=None,
               width=None,
               height=None,
               position=CTPDockPositionRight,
               top=None,
               left=None,
               timer_interval=0.1,
               bridge_cls=None):
    """Creates a Custom Task Pane from a UI control object.

    The control object can be any of the following:
    - tkinter.Toplevel
    - PyQt5.QtWidgets.QWidget
    - PySide2.QtWidgets.QWidget
    - wx.Frame

    :param control: UI control of one of the supported types.
    :param title: Title of the custom task pane to be created.
    :param width: Initial width of the custom task pane.
    :param height: Initial height of the custom task pane.
    :param position: Where to display the custom task pane. Can be any of:
                     - CTPDockPositionLeft
                     - CTPDockPositionTop
                     - CTPDockPositionRight
                     - CTPDockPositionBottom
                     - CTPDockPositionFloating
    :param top: Initial top position of custom task pane (only used if floating).
    :param left: Initial left position of custom task pane (only used if floating).
    :param timer_interval: The interval in seconds between calls to :py:meth:`CTPBridgeBase.on_timer`.
    :param bridge_cls: Subclass of :py:class:`CTPBridgeBase` to use. For supported widget types this
                       is chosen automatically.
    """
    raise Exception("Not supported when running outside of Excel")

class PlotBridgeBase:

    def __init__(self, figure):
        self.figure = figure

    def can_export(self, format):
        """Return True if the figure can be exported in a specific format.
        Formats are svg and png.
        """
        return False

    def get_size_hint(self, dpi):
        """Return (width, height) tuple the figure should be exported as
        or None. Width and height are in points (72th of an inch)."""
        return None

    def export(self, width, height, dpi, format, filename, **kwargs):
        """Export the figure to a file as a given size and format."""
        raise NotImplementedError()

def plot(figure=None,
         name=None,
         width=None,
         height=None,
         top=None,
         left=None,
         sheet=None,
         allow_svg=True,
         alt_text=None,
         reset=False,
         bridge_cls=None,
         **kwargs):
    """Plots a figure to Excel as an embedded image.

    The figure can be any of the following:

    - A matplotlib Figure object

    :param figure: Figure to plot. This can be an instance of any of the following:

                   - matplotlib.figure.Figure
                   - plotly.graph_objects.Figure
                   - bokeh.models.plots.Plot

                   If none, the active matplotlib.pyplot figure is used.

    :param name: Name of Picture object in Excel. If this is None then
                 a name will be chosen, and if called from a UDF then
                 repeated calls with re-use the same name.

    :param width: Width of the picture in Excel, in points.
                  If set then height must also be set.
                  If None the width will be taken from the figure.

    :param height: Height of the picture in Excel, in points.
                   If set then width must also be set.
                   If None the height will be taken from the figure.

    :param top: Location of the top of the plot in Excel, in points.
                If set then left must also be set.
                If None, the picture will be placed below the current or selected cell.

    :param left: Location of the left of the plot in Excel, in points.
                 If set then top must also be set.
                 If None, the picture will be placed below the current or selected cell.

    :param sheet: Name of the sheet to add the picture to. If none, the current sheet is used.

    :param allow_svg: Some figures may be rendered as SVG, if the version of Excel allows.
                      This can be disabled by setting this option to False.

    :param alt_text: Alternative (descriptive) text to use for the picture object in Excel. This can
                     be displayed instead of the shape object if the Excel document is saved to a web page,
                     or when the mouse hovers over the image (if supported by the browser).

    :param reset: Reset the size and position of the image.

    :param kwargs: Additional arguments will be called to the implementation specific
                   method for exporting the figure to an image.
    """
    raise Exception("Not supported when running outside of Excel")
