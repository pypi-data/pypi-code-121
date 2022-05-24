"""
************************************************************
hdev_operator.py - HALCON HDevEngine dev operator support.
************************************************************

Project: HALCON/Python

Description:
Inside HDevelop, dev_* operators can be used for convenience.
When embedding an HDevelop program or procedure inside your
application, the potential dev_* operator calls have no
straightforward mapping. It might be desirable to for example
map dev_* operator calls to visualization within your
application.
Thus, HDevEngine/Python provides a base class, which you can
inherit from and overwrite with logic appropriate for your
application. Which can the be used to call
HDevEngine.set_hdev_operator_impl.

************************************************************

(c) 1996-2020 by MVTec Software GmbH

Software by: MVTec Software GmbH, www.mvtec.com
"""

import ctypes
import traceback

from typing import Sequence, Union

from .ffi import (
    _htuple_to_python,
    _python_to_htuple,
    H_MSG_FAIL,
    H_MSG_OK,
    Herror,
    Hkey,
    HTupleType,
    make_c_func_prototype,
)

from .util import MaybeSequence
from .hhandle import HHandle
from .hobject import HObject


__all__ = [
    '_NativeDevOperatorWrapper',
    'HDevOperatorBase',
]


# --- Exported Classes ---


class HDevOperatorBase(object):
    """
    HALCON dev operator base implementation.

    Intended for use with HDevEngine.set_hdev_operator_impl.

    This base implementation unconditionally raises an Exception.
    Inherit from this class and overwrite the functionality you want.
    All Python functionality is supported within the implementation functions.

    The derived functions MUST NOT change the signature of the base functions.
    """
    def __init__(self):
        pass

    @staticmethod
    def dev_clear_window() -> None:
        """
        Clear the contents of the active graphics window.
        """
        raise Exception('dev_clear_window is not implemented')

    @staticmethod
    def dev_close_window() -> None:
        """
        Close the active floating graphics window.

        Notes
        -----
        This operator only works for single floating graphics windows, i.e.,
        graphics windows that are neither docked nor tabbed.
        """
        raise Exception('dev_close_window is not implemented')

    @staticmethod
    def dev_set_window(window_handle: HHandle) -> None:
        """
        Activate a graphics window.

        Parameters
        ----------

        window_handle : HHandle
                        Window handle.
        """
        raise Exception('dev_set_window is not implemented')

    @staticmethod
    def dev_get_window() -> HHandle:
        """
        Return the handle of the active graphics window.

        Returns
        -------

        window_handle : HHandle
                        Window handle.
        """
        raise Exception('dev_get_window is not implemented')

    @staticmethod
    def dev_display(object: HObject) -> None:
        """
        Displays image objects in the current graphics window.

        Parameters
        ----------

        object : HObject
                 Image objects to be displayed.
        """
        raise Exception('dev_display is not implemented')

    @staticmethod
    def dev_disp_text(
        string: MaybeSequence[str],
        coord_system: str,
        row: MaybeSequence[Union[int, float, str]],
        column: MaybeSequence[Union[int, float, str]],
        color: MaybeSequence[str],
        gen_param_name: MaybeSequence[str],
        gen_param_value: MaybeSequence[Union[str, int, float]]
    ) -> None:
        """
        Display text in in the current graphics window.

        Parameters
        ----------

        string : MaybeSequence[str]
                 A tuple of strings containing the text message to be
                 displayed. Each value of the tuple will be displayed in a
                 single line.
                 Value Suggestion: hello

        coord_system : str
                       If set to 'window', the text position is given with
                       respect to the window coordinate system. If set to
                       'image', image coordinates are used (this may be useful
                       in zoomed images).
                       Value Suggestion: window

        row : MaybeSequence[Union[int, float, str]]
              The vertical text alignment or the row coordinate of the desired
              text position.
              Value Suggestion: 12

        column : MaybeSequence[Union[int, float, str]]
                 The horizontal text alignment or the column coordinate of the
                 desired text position.
                 Value Suggestion: 12

        color : MaybeSequence[str]
                A tuple of strings defining the colors of the texts.
                Value Suggestion: black

        gen_param_name : MaybeSequence[str]
                         Generic parameter names.
                         Value Suggestion: []

        gen_param_value : MaybeSequence[Union[str, int, float]]
                         Generic parameter values.
                         Value Suggestion: []
        """
        raise Exception('dev_disp_text is not implemented')

    @staticmethod
    def dev_set_window_extents(
        row: int,
        column: int,
        width: int,
        height: int
    ) -> None:
        """
        Change position and size of the active floating graphics window.

        Parameters
        ----------

        row : int
              Row index of upper left corner.
              Value Suggestion: 0
              Assertion: Row >= 0 || Row == -1

        column : int
                 Column index of upper left corner.
                 Value Suggestion: 0
                 Assertion: Column >= 0 || Column == -1

        width : int
                Width of the window.
                Value Suggestion: 256
                Assertion: Width > 0 || Width == -1

        height : int
                 Height of the window.
                 Value Suggestion: 256
                 Assertion: Height > 0 || Height == -1

        Notes
        -----
        This operator only works for single floating graphics windows, i.e.,
        graphics windows that are neither docked nor tabbed.
        Never use set_window_extents to change the size and position of an
        graphics window.  The operator dev_set_window_extents has to be used
        instead.
        """
        raise Exception('dev_set_window_extents is not implemented')

    @staticmethod
    def dev_set_draw(draw_mode: str) -> None:
        """
        Define the region fill mode.

        Parameters
        ----------

        draw_mode : str
                    Fill mode for region output.
                    Value Suggestion: fill
        """
        raise Exception('dev_set_draw is not implemented')

    @staticmethod
    def dev_set_contour_style(style: str) -> None:
        """
        Define the contour display fill style.

        Parameters
        ----------

        style : str
                Fill style for contour display.
                Value Suggestion: stroke
        """
        raise Exception('dev_set_contour_style is not implemented')

    @staticmethod
    def dev_set_shape(shape: str) -> None:
        """
        Define the region output shape.

        Parameters
        ----------

        shape : str
                Region output mode.
                Value Suggestion: original
        """
        raise Exception('dev_set_shape is not implemented')

    @staticmethod
    def dev_set_colored(num_colors: int) -> None:
        """
        Set multiple output colors.

        Parameters
        ----------

        num_colors : int
                     Number of output colors.
                     Value Suggestion: 6
        """
        raise Exception('dev_set_colored is not implemented')

    @staticmethod
    def dev_set_color(color_name: MaybeSequence[str]) -> None:
        """
        Set one or more output colors.

        Parameters
        ----------

        color_name : MaybeSequence[str]
                     Output color names.
                     Value Suggestion: white
        """
        raise Exception('dev_set_color is not implemented')

    @staticmethod
    def dev_set_lut(lut_name: str) -> None:
        """
        Set ``look-up-table'' (lut).

        Parameters
        ----------

        lut_name : str
                   Name of look-up-table, values of look-up-table (RGB) or
                   file name.
                   Value Suggestion: default
        """
        raise Exception('dev_set_lut is not implemented')

    @staticmethod
    def dev_set_paint(mode: Sequence[Union[int, str]]) -> None:
        """
        Define the gray value output mode.

        Parameters
        ----------

        mode : Sequence[Union[int, str]]
               Grayvalue output name. Additional parameters possible.
               Value Suggestion: default
        """
        raise Exception('dev_set_paint is not implemented')

    @staticmethod
    def dev_set_part(
        row_1: int,
        column_1: int,
        row_2: int,
        column_2: int
    ) -> None:
        """
        Modify the displayed image part.

        Parameters
        ----------

        row_1 : int
                Row of the upper left corner of the chosen image part.
                Value Suggestion: 0

        column_1 : int
                   Column of the upper left corner of the chosen image part.
                   Value Suggestion: 0

        row_2 : int
                Row of the lower right corner of the chosen image part.
                Value Suggestion: 128

        column_2 : int
                   Column of the lower right corner of the chosen image part.
                   Value Suggestion: 128
        """
        raise Exception('dev_set_part is not implemented')

    @staticmethod
    def dev_set_line_width(line_width: int) -> None:
        """
        Define the line width for region contour output.

        Parameters
        ----------

        line_width : int
                     Line width for region output in contour mode.
                     Value Suggestion: 1
                     Assertion: LineWidth >= 1
        """
        raise Exception('dev_set_line_width is not implemented')

    @staticmethod
    def dev_open_window(
        row: int,
        column: int,
        width: int,
        height: int,
        background: Union[int, str]
    ) -> HHandle:
        """
        Open a new graphics window.

        Parameters
        ----------

        row : int
              Row index of upper left corner.
              Value Suggestion: 0
              Assertion: Row >= 0

        column : int
                 Column index of upper left corner.
                 Value Suggestion: 0
                 Assertion: Column >= 0

        width : int
                Width of the window.
                Value Suggestion: 512
                Assertion: Width > 0 || Width == -1

        height : int
                 Height of the window.
                 Value Suggestion: 512
                 Assertion: Height > 0 || Height == -1

        background : Union[int, str]
                     Color of the background of the new window.
                     Value Suggestion: 'black'

        Returns
        -------

        window_handle : HHandle
                        Window handle.
        """
        raise Exception('dev_open_window is not implemented')


# --- Private Implementation Details ---


def _ptr_to_python_tuple(tuple_ptr: int) -> HTupleType:
    return _htuple_to_python(ctypes.c_ssize_t(tuple_ptr), as_list=True)


class _NativeDevOperatorWrapper(object):
    """
    Wraps C interface dev operator callbacks.
    """
    def __init__(self, dev_impl: HDevOperatorBase):
        # Assign to self is important for non Python checked lifetime.

        self.dev_impl = dev_impl

        self.dev_open_window = self._make_dev_open_window()
        self.dev_close_window = self._make_dev_close_window()
        self.dev_set_window = self._make_dev_set_window()
        self.dev_get_window = self._make_dev_get_window()
        self.dev_set_window_extents = self._make_dev_set_window_extents()
        self.dev_set_part = self._make_dev_set_part()
        self.dev_clear_window = self._make_dev_clear_window()
        self.dev_display = self._make_dev_display()
        self.dev_disp_text = self._make_dev_disp_text()
        self.dev_set_draw = self._make_dev_set_draw()
        self.dev_set_contour_style = self._make_dev_set_contour_style()
        self.dev_set_shape = self._make_dev_set_shape()
        self.dev_set_colored = self._make_dev_set_colored()
        self.dev_set_color = self._make_dev_set_color()
        self.dev_set_lut = self._make_dev_set_lut()
        self.dev_set_paint = self._make_dev_set_paint()
        self.dev_set_line_width = self._make_dev_set_line_width()

    def _make_dev_open_window(self):
        # Technically Htuple* on C side. But since we never intend to look at
        # or modify the value on Python side. We don't have access to the
        # Htuple type.
        prototype = make_c_func_prototype(
            Herror,  # return
            ctypes.c_void_p,  # in row
            ctypes.c_void_p,  # in col
            ctypes.c_void_p,  # in width
            ctypes.c_void_p,  # in height
            ctypes.c_void_p,  # in background
            ctypes.c_void_p   # out win_id
        )

        def wrapper(
            row: int,
            col: int,
            width: int,
            height: int,
            background: int,
            win_id: int
        ) -> Herror:
            window = self.dev_impl.dev_open_window(
                _ptr_to_python_tuple(row),
                _ptr_to_python_tuple(col),
                _ptr_to_python_tuple(width),
                _ptr_to_python_tuple(height),
                _ptr_to_python_tuple(background)
            )

            _python_to_htuple(ctypes.c_ssize_t(win_id), window)

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_close_window(self):
        prototype = make_c_func_prototype(Herror)

        def wrapper():
            self.dev_impl.dev_close_window()

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_window(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(win_id: int):
            self.dev_impl.dev_set_window(_ptr_to_python_tuple(win_id))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_get_window(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(win_id: int):
            window = self.dev_impl.dev_get_window()
            _python_to_htuple(ctypes.c_ssize_t(win_id), window)

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_window_extents(self):
        prototype = make_c_func_prototype(
            Herror,
            ctypes.c_void_p,  # in row
            ctypes.c_void_p,  # in col
            ctypes.c_void_p,  # in width
            ctypes.c_void_p   # in height
        )

        def wrapper(row: int, col: int, width: int, height: int):
            self.dev_impl.dev_set_window_extents(
                _ptr_to_python_tuple(row),
                _ptr_to_python_tuple(col),
                _ptr_to_python_tuple(width),
                _ptr_to_python_tuple(height)
            )

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_part(self):
        prototype = make_c_func_prototype(
            Herror,
            ctypes.c_void_p,  # in row1
            ctypes.c_void_p,  # in col1
            ctypes.c_void_p,  # in row2
            ctypes.c_void_p   # in col2
        )

        def wrapper(row1: int, col1: int, row2: int, col2: int):
            self.dev_impl.dev_set_part(
                _ptr_to_python_tuple(row1),
                _ptr_to_python_tuple(col1),
                _ptr_to_python_tuple(row2),
                _ptr_to_python_tuple(col2)
            )

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_clear_window(self):
        prototype = make_c_func_prototype(Herror)

        def wrapper():
            self.dev_impl.dev_clear_window()

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_display(self):
        prototype = make_c_func_prototype(Herror, Hkey)

        def wrapper(obj_ptr: int) -> Herror:
            obj = HObject._copy_from_key(Hkey(obj_ptr))
            self.dev_impl.dev_display(obj)

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_disp_text(self):
        prototype = make_c_func_prototype(
            Herror,
            ctypes.c_void_p,  # in string
            ctypes.c_void_p,  # in coord_system
            ctypes.c_void_p,  # in row
            ctypes.c_void_p,  # in column
            ctypes.c_void_p,  # in color
            ctypes.c_void_p,  # in genParamNames
            ctypes.c_void_p   # in genParamValues
        )

        def wrapper(
            string,
            coord_system,
            row,
            column,
            color,
            genParamNames,
            genParamValues
        ):
            self.dev_impl.dev_disp_text(
                _ptr_to_python_tuple(string),
                _ptr_to_python_tuple(coord_system),
                _ptr_to_python_tuple(row),
                _ptr_to_python_tuple(column),
                _ptr_to_python_tuple(color),
                _ptr_to_python_tuple(genParamNames),
                _ptr_to_python_tuple(genParamValues)
            )

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_draw(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(draw: int):
            self.dev_impl.dev_set_draw(_ptr_to_python_tuple(draw))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_contour_style(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(style: int):
            self.dev_impl.dev_set_contour_style(_ptr_to_python_tuple(style))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_shape(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(shape: int):
            self.dev_impl.dev_set_shape(_ptr_to_python_tuple(shape))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_colored(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(colored: int):
            self.dev_impl.dev_set_colored(_ptr_to_python_tuple(colored))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_color(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(color: int):
            self.dev_impl.dev_set_color(_ptr_to_python_tuple(color))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_lut(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(lut: int):
            self.dev_impl.dev_set_lut(_ptr_to_python_tuple(lut))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_paint(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(paint: int):
            self.dev_impl.dev_set_paint(_ptr_to_python_tuple(paint))

        return prototype(_exception_wrap_native_callback(wrapper))

    def _make_dev_set_line_width(self):
        prototype = make_c_func_prototype(Herror, ctypes.c_void_p)

        def wrapper(width: int):
            self.dev_impl.dev_set_line_width(_ptr_to_python_tuple(width))

        return prototype(_exception_wrap_native_callback(wrapper))


def _exception_wrap_native_callback(callback):
    # We can use *args here because the prototype knows the argument layout.
    def exception_wrapper(*args):
        try:
            callback(*args)

            return H_MSG_OK
        except:  # noqa: E722
            # Writing the traceback to stderr isn't ideal, but unwinding
            # Python exceptions across the FFI boundary would be extremely
            # complex and error prone.
            # This at least allows users to easily find bugs in their code.
            traceback.print_exc()

            # This translates into a HDevEngineError saying a custom error
            # occurred int the message string.
            return H_MSG_FAIL

    return exception_wrapper
