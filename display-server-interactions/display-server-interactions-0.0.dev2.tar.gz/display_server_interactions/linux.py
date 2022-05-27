#!/usr/bin/python3
# -*- coding: utf-8 -*-

# local modules
from .base import DSIBase
from .window import WindowBase
from .image import Image

# built-in modules
import logging
import ctypes.util
from ctypes import (
    POINTER,
    byref,
    cast,
    c_char_p,
    c_int,
    c_long,
    c_ubyte,
    c_ulong,
    c_char,
    Structure,
    c_int32,
    c_uint,
    c_void_p,
    c_uint32,
    _SimpleCData
)

# Setup Xlib Structures


class Display(Structure):
    """
    https://tronche.com/gui/x/xlib/display/opening.html#Display\n
    /usr/include/X11/Xlib.h: 487
    """


class XImage(Structure):
    """
    https://tronche.com/gui/x/xlib/graphics/images.html#XImage\n
    /usr/include/X11/Xlib.h: 360-394
    """

    _fields_ = [
        ('width', c_int),
        ('height', c_int),
        ('xoffset', c_int),
        ('format', c_int),
        ('data', c_void_p),
        ('byte_order', c_int),
        ('bitmap_unit', c_int),
        ('bitmap_bit_order', c_int),
        ('bitmap_pad', c_int),
        ('depth', c_int),
        ('bytes_per_line', c_int),
        ('bits_per_pixel', c_int),
        ('red_mask', c_ulong),
        ('green_mask', c_ulong),
        ('blue_mask', c_ulong)
    ]


class XWindowAttributes(Structure):
    """
    https://tronche.com/gui/x/xlib/window-information/XGetWindowAttributes.html\n
    /usr/include/X11/Xlib.h: 308-334
    """

    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),
        ("width", c_int32),
        ("height", c_int32),
        ("border_width", c_int32),
        ("depth", c_int32),
        ("visual", c_ulong),
        ("root", c_ulong),
        ("class", c_int32),
        ("bit_gravity", c_int32),
        ("win_gravity", c_int32),
        ("backing_store", c_int32),
        ("backing_planes", c_ulong),
        ("backing_pixel", c_ulong),
        ("save_under", c_int32),
        ("colourmap", c_ulong),
        ("mapinstalled", c_uint32),
        ("map_state", c_uint32),
        ("all_event_masks", c_ulong),
        ("your_event_mask", c_ulong),
        ("do_not_propagate_mask", c_ulong),
        ("override_redirect", c_int32),
        ("screen", c_ulong)
    ]


class XKeyEvent(Structure):
    """
    https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html#XKeyEvent\n
    /usr/include/X11/Xlib.h: 557-571
    """

    _fields_ = [
        ('type', c_int),
        ('serial', c_ulong),
        ('send_event', c_int),
        ('display', POINTER(Display)),
        ('window', c_ulong),  # Window / XID
        ('root', c_ulong),  # Window / XID
        ('subwindow', c_ulong),  # Window / XID
        ('time', c_ulong),  # Time
        ('x', c_int),
        ('y', c_int),
        ('x_root', c_int),
        ('y_root', c_int),
        ('state', c_uint),
        ('keycode', c_uint),
        ('same_screen', c_int),
    ]


class XButtonEvent(ctypes.Structure):
    """
    https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html#XButtonEvent\n
    /usr/include/X11/Xlib.h: 575-589
    """

    _fields_ = [
        ('type', ctypes.c_int),
        ('serial', ctypes.c_ulong),
        ('send_event', ctypes.c_int),
        ('display', ctypes.POINTER(Display)),
        ('window', ctypes.c_ulong),  # Window (XID)
        ('root', ctypes.c_ulong),  # Window (XID)
        ('subwindow', ctypes.c_ulong),  # Window (XID)
        ('time', ctypes.c_ulong),  # Time
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('x_root', ctypes.c_int),
        ('y_root', ctypes.c_int),
        ('state', ctypes.c_uint),
        ('button', ctypes.c_uint),
        ('same_screen', ctypes.c_int),
    ]


class XEvent(ctypes.Union):
    """
    https://tronche.com/gui/x/xlib/events/structures.html#XEvent\n
    /usr/include/X11/Xlib.h: 973-1009
    """
    _fields_ = [
        ('type', ctypes.c_int),
        ('xkey', XKeyEvent),
        ('xbutton', XButtonEvent),
        ('pad', ctypes.c_long*24),
    ]


class XErrorEvent(Structure):
    """
    https://tronche.com/gui/x/xlib/event-handling/protocol-errors/default-handlers.html#XErrorEvent\n
    /usr/include/X11/Xlib.h: 924-932
    """

    def __repr__(self) -> str:
        return f"XErrorEvent(type={self.type}, serial={self.serial}, error_code={self.error_code}, request_code={self.request_code}, minor_code={self.minor_code})"

    _fields_ = [
        ("type", c_int),
        ("display", POINTER(Display)),
        ("serial", c_ulong),
        ("error_code", c_ubyte),
        ("request_code", c_ubyte),
        ("minor_code", c_ubyte),
        ("resourceid", c_void_p),
    ]


logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


@ctypes.CFUNCTYPE(c_int, POINTER(Display), POINTER(XErrorEvent))
def error_handler(_, event):
    logger.error("%s", event.contents)
    return 0


def get_logger() -> logging.Logger:
    """
    Returns a logger that is responsible for logging XErrorEvents.
    The logger is set to CRITICAL. So it will not log anything.
    To make it log something, set the log level at least to ERROR.
    You can archive this with "logger.setLevel(logging.ERROR)".
    """
    return logger

# Setup Xlib Variables


class Masks(object):
    """
    https://tronche.com/gui/x/xlib/events/mask.html\n
    /usr/include/X11/X.h: 150-175
    """
    NoEventMask = 0
    KeyPressMask = 1
    KeyReleaseMask = 2
    ButtonPressMask = 4
    ButtonReleaseMask = 8
    EnterWindowMask = 16
    LeaveWindowMask = 32
    PointerMotionMask = 64
    PointerMotionHintMask = 128
    Button1MotionMask = 256
    Button2MotionMask = 512
    Button3MotionMask = 1024
    Button4MotionMask = 2048
    Button5MotionMask = 4096
    ButtonMotionMask = 8192
    KeymapStateMask = 16384
    ExposureMask = 32768
    VisibilityChangeMask = 65536
    StructureNotifyMask = 131072
    ResizeRedirectMask = 262144
    SubstructureNotifyMask = 524288
    SubstructureRedirectMask = 1048576
    FocusChangeMask = 2097152
    PropertyChangeMask = 4194304
    ColormapChangeMask = 8388608
    OwnerGrabButtonMask = 16777216


class EventTypes(object):
    """
    https://tronche.com/gui/x/xlib/events/types.html\n
    /usr/include/X11/X.h: 181-215
    """
    KeyPress = 2
    KeyRelease = 3
    ButtonPress = 4
    ButtonRelease = 5
    MotionNotify = 6
    EnterNotify = 7
    LeaveNotify = 8
    FocusIn = 9
    FocusOut = 10
    KeymapNotify = 11
    Expose = 12
    GraphicsExpose = 13
    NoExpose = 14
    VisibilityNotify = 15
    CreateNotify = 16
    DestroyNotify = 17
    UnmapNotify = 18
    MapNotify = 19
    MapRequest = 20
    ReparentNotify = 21
    ConfigureNotify = 22
    ConfigureRequest = 23
    GravityNotify = 24
    ResizeRequest = 25
    CirculateNotify = 26
    CirculateRequest = 27
    PropertyNotify = 28
    SelectionClear = 29
    SelectionRequest = 30
    SelectionNotify = 31
    ColormapNotify = 32
    ClientMessage = 33
    MappingNotify = 34
    GenericEvent = 35
    LASTEvent = 36


class KeyMasks(object):
    """
    https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html\n
    /usr/include/X11/X.h: 221-228
    """
    ShiftMask = 1
    LockMask = 2
    ControlMask = 4
    Mod1Mask = 8
    Mod2Mask = 16
    Mod3Mask = 32
    Mod4Mask = 64
    Mod5Mask = 128


class ButtonCodes(object):
    """
    https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html\n
    /usr/include/X11/X.h: 259-263
    """
    AnyButton = 0
    Button1 = 1
    Button2 = 2
    Button3 = 3
    Button4 = 4
    Button5 = 5


class Xlib(object):
    def __init__(self):
        # load libX11.so.6
        x11 = ctypes.util.find_library("X11")
        if not x11:
            raise Exception("X11 library not found!")
        self.xlib = ctypes.cdll.LoadLibrary(x11)

        self.xlib.XSetErrorHandler(error_handler)

        # Setup Xlib functions
        self.xlib.XGetImage.argtypes = [
            POINTER(Display),
            c_ulong,  # Drawable (XID)
            c_int,
            c_int,
            c_uint,
            c_uint,
            c_ulong,
            c_int,
        ]
        self.xlib.XGetImage.restype = POINTER(XImage)

        self.xlib.XGetWindowAttributes.argtypes = [
            POINTER(Display),
            c_ulong,  # Window (XID)
            POINTER(XWindowAttributes)
        ]
        self.xlib.XOpenDisplay.restype = POINTER(Display)
        self.xlib.XGetWindowProperty.argtypes = [
            POINTER(Display),
            c_ulong,  # Window
            c_ulong,  # Atom
            c_long,
            c_long,
            c_int,
            c_ulong,  # Atom
            POINTER(c_ulong),  # Atom
            POINTER(c_int),
            POINTER(c_ulong),
            POINTER(c_ulong),
            POINTER(POINTER(c_ubyte))
        ]
        self.xlib.XInternAtom.argtypes = [POINTER(Display), c_char_p, c_int]
        self.xlib.XFree.argtypes = [c_void_p]
        self.xlib.XDestroyImage.argtypes = [POINTER(XImage)]
        self.xlib.XWarpPointer.argtypes = [
            POINTER(Display),
            c_ulong,
            c_ulong,
            c_int,
            c_int,
            c_uint,
            c_uint,
            c_int,
            c_int
        ]
        self.xlib.XFlush.argtypes = [POINTER(Display)]
        self.xlib.XKeysymToKeycode.argtypes = [POINTER(Display), c_ulong]
        self.xlib.XStringToKeysym.argtypes = [c_char_p]
        self.xlib.XSendEvent.argtypes = [
            POINTER(Display), c_ulong, c_int, c_long, c_void_p]
        self.xlib.XQueryTree.argtypes = [
            POINTER(Display),
            c_ulong,
            POINTER(c_ulong),
            POINTER(c_ulong),
            POINTER(POINTER(c_ulong)),
            POINTER(c_uint)
        ]

        # main
        self.display = self.xlib.XOpenDisplay(None)
        self.root_window = self.xlib.XRootWindow(self.display, 0)

    def __getattribute__(self, __name: str):
        if __name in ["xlib", "display", "root_window"]:
            return super().__getattribute__(__name)
        else:
            return self.xlib.__getattribute__(__name)


def get_window_property(xlib: Xlib, window_xid: int, property: str, type: _SimpleCData):
    """
    https://tronche.com/gui/x/xlib/window-information/XGetWindowProperty.html
    """
    actual_type_return = c_ulong()
    actual_format_return = c_int()
    nitems_return = c_ulong()
    bytes_after_return = c_ulong()
    prop_return = POINTER(c_ubyte)()

    xlib.XGetWindowProperty(
        xlib.display,
        window_xid,
        xlib.XInternAtom(
            xlib.display, c_char_p(property.encode('utf-8')),
            False
        ),
        0,
        1000,
        False,
        0,  # AnyPropertyType
        byref(actual_type_return),
        byref(actual_format_return),
        byref(nitems_return),
        byref(bytes_after_return),
        byref(prop_return)
    )

    if prop_return:
        data = cast(
            prop_return,
            POINTER(type)
        ).contents.value
    else:
        data = None

    # don't forget to free the memory or you will be fucked
    xlib.XFree(prop_return)

    return data


class Window(WindowBase):
    def __init__(self, xid: int, xlib: Xlib) -> None:
        self.xid = xid
        self.xlib = xlib

    @property
    def name(self) -> str:
        name = get_window_property(
            self.xlib,
            self.xid,
            "_NET_WM_NAME",
            c_char * 1024
        )
        if name:
            return name.decode('utf-8')
        else:
            return None

    @property
    def pid(self) -> int:
        return get_window_property(self.xlib, self.xid, "_NET_WM_PID", c_long)

    @property
    def active(self) -> bool:
        return self.xid == get_active_window_xid(self.xlib)

    @property
    def geometry(self) -> tuple:
        gwa = XWindowAttributes()
        self.xlib.XGetWindowAttributes(self.xlib.display, self.xid, byref(gwa))
        return (gwa.x, gwa.y, gwa.width, gwa.height)

    def get_image(self, geometry: tuple = None) -> Image:
        if geometry is None:
            geometry = self.geometry

        ximage = self.xlib.XGetImage(
            self.xlib.display,  # Display
            self.xid,  # Drawable (Window XID)
            geometry[0],  # x
            geometry[1],  # y
            geometry[2],  # width
            geometry[3],  # height
            0x00FFFFFF,  # plane_mask
            2  # format = ZPixmap
        )

        raw_data = ctypes.cast(
            ximage.contents.data,
            POINTER(c_ubyte * geometry[3] * geometry[2] * 4)
        )

        data = bytearray(raw_data.contents)

        data = Image(data, geometry[2], geometry[3])

        # don't forget to free the memory or you will be fucked
        self.xlib.XDestroyImage(ximage)

        return data

    def send_chr(self, chr: chr) -> None:
        """Send a character to the window

        Args:
            char (str): The character to send
        """
        # https://tronche.com/gui/x/xlib/event-handling/XSendEvent.html

        key = XEvent(type=EventTypes.KeyPress).xkey  # KeyPress
        key.keycode = self.xlib.XKeysymToKeycode(
            self.xlib.display,
            self.xlib.XStringToKeysym(c_char_p(chr.encode('utf-8')))
        )  # https://github.com/python-xlib/python-xlib/blob/master/Xlib/keysymdef/latin1.py
        key.window = key.root = self.xid
        key.state = KeyMasks.ShiftMask if chr.isupper() else 0

        self.xlib.XSendEvent(
            self.xlib.display,  # Display *display
            key.window,  # Window w
            True,  # Bool propagate
            Masks.KeyPressMask,  # long event_mask
            ctypes.byref(key)  # XEvent *event_send
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        self.xlib.XFlush(self.xlib.display)

    def send_str(self, str: str) -> None:
        """Send a string to the window

        Args:
            str (str): The string to send
        """
        for chr in str:
            self.send_chr(chr)

    def warp_pointer(self, x: int, y: int, geometry: tuple = None) -> None:
        if geometry is None:
            geometry = self.geometry

        # https://tronche.com/gui/x/xlib/input/XWarpPointer.html
        self.xlib.XWarpPointer(
            self.xlib.display,
            self.xid,  # src_w
            self.xid,  # dest_w
            geometry[0],
            geometry[1],
            geometry[2],
            geometry[3],
            x,
            y
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        self.xlib.XFlush(self.xlib.display)

    def send_mouse_click(self, x: int, y: int, button: ButtonCodes = ButtonCodes.Button1) -> None:
        """
        Send a mouse click to the window at the given coordinates without moving the pointer.
        Some applications may not respond to the click so it is recommended to also move the pointer with `warp_pointer`.
        """
        event = XEvent(type=EventTypes.ButtonPress).xbutton
        event.window = event.root = self.xid
        event.button = button
        event.x_root = 0
        event.y_root = 0
        event.x = x
        event.y = y

        self.xlib.XSendEvent(
            self.xlib.display,
            event.window,
            True,
            Masks.ButtonPressMask,
            ctypes.byref(event)
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        self.xlib.XFlush(self.xlib.display)

        event.type = EventTypes.ButtonRelease

        self.xlib.XSendEvent(
            self.xlib.display,
            event.window,
            True,
            Masks.ButtonReleaseMask,
            ctypes.byref(event)
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        self.xlib.XFlush(self.xlib.display)


def get_active_window_xid(xlib: Xlib) -> int:
    """
    Returns the XID of the active window.
    """
    return get_window_property(
        xlib,
        xlib.root_window,
        "_NET_ACTIVE_WINDOW",
        c_long
    )


def get_connected_xids(xlib: Xlib, window: int):
    """
    https://tronche.com/gui/x/xlib/window-information/XQueryTree.html\n
    Uses XQueryTree to get the XIDs of connected windows.
    """
    root_return = c_ulong()
    parent_return = c_ulong()
    children_return = POINTER(c_ulong)()
    nitems_return = c_uint()

    xlib.XQueryTree(
        xlib.display,  # Display *display
        window,  # Window window
        byref(root_return),  # Window *root_return
        byref(parent_return),  # Window *parent_return
        byref(children_return),  # Window **children_return
        byref(nitems_return)  # unsigned int *nitems_return
    )

    xids = []

    for xid in range(nitems_return.value):
        xids.append(children_return[xid])

    # don't forget to free the memory or you will be fucked
    xlib.XFree(children_return)

    return xids


def get_all_windows(xlib: Xlib) -> list:
    """
    Get all window XIDs. By recursively getting all connected windows.
    """
    final = get_connected_xids(xlib, xlib.root_window)
    next = final.copy()

    run = True
    while run:
        run = False
        next_temp = []
        for xid in next:
            xids = get_connected_xids(xlib, xid)
            if len(xids) > 0:
                run = True
            next_temp += xids

        next = next_temp
        final += next

    final_windows = []

    for xid in final:
        final_windows.append(Window(xid, xlib))

    return final_windows


class DSI(DSIBase):
    def __init__(self):
        self.xlib = Xlib()

    def get_active_window(self) -> WindowBase:
        return Window(get_active_window_xid(self.xlib), self.xlib)

    def get_all_windows(self) -> list:
        return get_all_windows(self.xlib)
