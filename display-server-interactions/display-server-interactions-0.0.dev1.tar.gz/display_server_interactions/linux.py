#!/usr/bin/python3
# -*- coding: utf-8 -*-

from operator import le

from .base import DSIBase
from .window import WindowBase
from .image import Image

# built-in modules
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

# load libX11.so.6
x11 = ctypes.util.find_library("X11")
if not x11:
    raise Exception("X11 library not found!")
xlib = ctypes.cdll.LoadLibrary(x11)


# Setup Xlib Structures
class Display(Structure):
    pass


class XImage(Structure):
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
    _fields_ = [
        ('type', ctypes.c_int),
        ('xkey', XKeyEvent),
        ('xbutton', XButtonEvent),
        ('pad', ctypes.c_long*24),
    ]

# Setup Xlib Variables


class Masks(object):
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
    ShiftMask = 1
    LockMask = 2
    ControlMask = 4
    Mod1Mask = 8
    Mod2Mask = 16
    Mod3Mask = 32
    Mod4Mask = 64
    Mod5Mask = 128


class ButtonCodes(object):
    AnyButton = 0
    Button1 = 1
    Button2 = 2
    Button3 = 3
    Button4 = 4
    Button5 = 5


# Setup Xlib functions
xlib.XGetImage.argtypes = [
    POINTER(Display),
    c_ulong,  # Drawable (XID)
    c_int,
    c_int,
    c_uint,
    c_uint,
    c_ulong,
    c_int,
]
xlib.XGetImage.restype = POINTER(XImage)

xlib.XGetWindowAttributes.argtypes = [
    POINTER(Display),
    c_ulong,  # Window (XID)
    POINTER(XWindowAttributes)
]
xlib.XOpenDisplay.restype = POINTER(Display)
xlib.XGetWindowProperty.argtypes = [
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

# main
display = xlib.XOpenDisplay(None)
root_window = xlib.XRootWindow(display, 0)


def get_window_property(window_xid: int, property: str, type: _SimpleCData):
    actual_type_return = c_ulong()
    actual_format_return = c_int()
    nitems_return = c_ulong()
    bytes_after_return = c_ulong()
    prop_return = POINTER(c_ubyte)()

    # https://tronche.com/gui/x/xlib/window-information/XGetWindowProperty.html
    xlib.XGetWindowProperty(
        display,
        window_xid,
        xlib.XInternAtom(display, c_char_p(property.encode('utf-8')), False),
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
    def __init__(self, xid: int) -> None:
        self.xid = xid

    @property
    def name(self) -> str:
        name = get_window_property(self.xid, "_NET_WM_NAME", c_char * 1024)
        if name:
            return name.decode('utf-8')
        else:
            return None

    @property
    def pid(self) -> int:
        return get_window_property(self.xid, "_NET_WM_PID", c_long)

    @property
    def active(self) -> bool:
        return self.xid == get_active_window_xid()

    @property
    def geometry(self) -> tuple:
        gwa = XWindowAttributes()
        xlib.XGetWindowAttributes(display, self.xid, byref(gwa))
        return (gwa.x, gwa.y, gwa.width, gwa.height)

    def get_image(self, geometry: tuple = None) -> Image:
        if geometry is None:
            geometry = self.geometry

        ximage = xlib.XGetImage(
            display,  # Display
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
        xlib.XDestroyImage(ximage)

        return data

    def send_chr(self, chr: chr) -> None:
        """Send a character to the window

        Args:
            char (str): The character to send
        """
        # https://tronche.com/gui/x/xlib/event-handling/XSendEvent.html

        key = XEvent(type=EventTypes.KeyPress).xkey  # KeyPress
        key.keycode = xlib.XKeysymToKeycode(
            display,
            xlib.XStringToKeysym(chr)
        )  # https://github.com/python-xlib/python-xlib/blob/master/Xlib/keysymdef/latin1.py
        key.window = key.root = self.xid
        key.state = KeyMasks.ShiftMask if chr.isupper() else 0

        xlib.XSendEvent(
            display,  # Display *display
            key.window,  # Window w
            True,  # Bool propagate
            Masks.KeyPressMask,  # long event_mask
            ctypes.byref(key)  # XEvent *event_send
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        xlib.XFlush(display)

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
        xlib.XWarpPointer(
            display,
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
        xlib.XFlush(display)

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

        xlib.XSendEvent(
            display,
            event.window,
            True,
            Masks.ButtonPressMask,
            ctypes.byref(event)
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        xlib.XFlush(display)

        event.type = EventTypes.ButtonRelease

        xlib.XSendEvent(
            display,
            event.window,
            True,
            Masks.ButtonReleaseMask,
            ctypes.byref(event)
        )

        # flush display or events will run delayed cus thai'r only called on the next update
        xlib.XFlush(display)


def get_active_window_xid() -> int:
    return get_window_property(
        root_window,
        "_NET_ACTIVE_WINDOW",
        c_long
    )


def get_connected_xids(window):
    root_return = c_ulong()
    parent_return = c_ulong()
    children_return = POINTER(c_ulong)()
    nitems_return = c_uint()

    xlib.XQueryTree(
        display,  # Display *display
        window,  # Window window
        byref(root_return),  # Window *root_return
        byref(parent_return),  # Window *parent_return
        byref(children_return),  # Window **children_return
        byref(nitems_return)  # unsigned int *nitems_return
    )

    xids = []

    for xid in range(nitems_return.value):
        xids.append(children_return[xid])

    return xids


def get_all_windows() -> list:
    final = get_connected_xids(root_window)
    next = final.copy()

    run = True
    while run:
        run = False
        next_temp = []
        for xid in next:
            xids = get_connected_xids(xid)
            if len(xids) > 0:
                run = True
            next_temp += xids

        next = next_temp
        final += next

    final_windows = []

    for xid in final:
        final_windows.append(Window(xid))

    return final_windows


class DSI(DSIBase):
    def get_active_window() -> WindowBase:
        return Window(get_active_window_xid())

    def get_all_windows() -> list:
        return get_all_windows()
