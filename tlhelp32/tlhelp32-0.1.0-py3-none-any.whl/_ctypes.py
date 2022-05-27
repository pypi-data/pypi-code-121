"""Underlying Win32 API definitions and some helpers."""

import ctypes as c
from ctypes import wintypes as wt

kernel32 = c.windll["kernel32"]


class SizedStructure(c.Structure):
    def __init__(self, **kwargs):
        kwargs["dwSize"] = self._size_ = c.sizeof(type(self))
        super().__init__(**kwargs)

    def reset_size(self):
        self.dwSize = self._size_


def get_fptr(name, restype, *argtypes):
    return c.WINFUNCTYPE(restype, *argtypes, use_last_error=True)((name, kernel32))


ERROR_NO_MORE_FILES = 18
INVALID_HANDLE_VALUE = -1
CloseHandle = c.WINFUNCTYPE(wt.BOOL, wt.HANDLE)(("CloseHandle", kernel32))

MAX_MODULE_NAME32 = 255
TH32CS_INHERIT = 0x80000000
TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPALL = (
    TH32CS_SNAPHEAPLIST | TH32CS_SNAPMODULE | TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD
)


class HEAPENTRY32(SizedStructure):
    _fields_ = [
        ("dwSize", c.c_size_t),
        ("hHandle", wt.HANDLE),
        ("dwAddress", wt.PULONG),
        ("dwBlockSize", c.c_size_t),
        ("dwFlags", wt.DWORD),
        ("dwLockCount", wt.DWORD),
        ("dwResvd", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("th32HeapID", wt.PULONG),
    ]


class HEAPLIST32(SizedStructure):
    _fields_ = [
        ("dwSize", c.c_size_t),
        ("th32ProcessID", wt.DWORD),
        ("th32HeapID", wt.PULONG),
        ("dwFlags", wt.DWORD),
    ]


class MODULEENTRY32W(SizedStructure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("th32ModuleID", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("GlblcntUsage", wt.DWORD),
        ("ProccntUsage", wt.DWORD),
        ("modBaseAddr", wt.PBYTE),
        ("modBaseSize", wt.DWORD),
        ("hModule", wt.HMODULE),
        ("szModule", wt.WCHAR * (MAX_MODULE_NAME32 + 1)),
        ("szExePath", wt.WCHAR * wt.MAX_PATH),
    ]


class PROCESSENTRY32W(SizedStructure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("cntUsage", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("th32DefaultHeapID", wt.PULONG),
        ("th32ModuleID", wt.DWORD),
        ("cntThreads", wt.DWORD),
        ("th32ParentProcessID", wt.DWORD),
        ("pcPriClassBase", wt.LONG),
        ("dwFlags", wt.DWORD),
        ("szExeFile", wt.WCHAR * wt.MAX_PATH),
    ]


class THREADENTRY32(SizedStructure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("cntUsage", wt.DWORD),
        ("th32ThreadID", wt.DWORD),
        ("th32OwnerProcessID", wt.DWORD),
        ("tpBasePri", wt.LONG),
        ("tpDeltaPri", wt.LONG),
        ("dwFlags", wt.DWORD),
    ]


CreateToolhelp32Snapshot = get_fptr(
    "CreateToolhelp32Snapshot", wt.HANDLE, wt.DWORD, wt.DWORD
)
Heap32First = get_fptr(
    "Heap32First", wt.BOOL, c.POINTER(HEAPENTRY32), wt.DWORD, wt.PULONG
)
Heap32ListFirst = get_fptr("Heap32ListFirst", wt.BOOL, wt.HANDLE, c.POINTER(HEAPLIST32))
Heap32ListNext = get_fptr("Heap32ListNext", wt.BOOL, wt.HANDLE, c.POINTER(HEAPLIST32))
Heap32Next = get_fptr("Heap32Next", wt.BOOL, c.POINTER(HEAPENTRY32))
Module32FirstW = get_fptr(
    "Module32FirstW", wt.BOOL, wt.HANDLE, c.POINTER(MODULEENTRY32W)
)
Module32NextW = get_fptr("Module32NextW", wt.BOOL, wt.HANDLE, c.POINTER(MODULEENTRY32W))
Process32FirstW = get_fptr(
    "Process32FirstW", wt.BOOL, wt.HANDLE, c.POINTER(PROCESSENTRY32W)
)
Process32NextW = get_fptr(
    "Process32NextW", wt.BOOL, wt.HANDLE, c.POINTER(PROCESSENTRY32W)
)
Thread32First = get_fptr("Thread32First", wt.BOOL, wt.HANDLE, c.POINTER(THREADENTRY32))
Thread32Next = get_fptr("Thread32Next", wt.BOOL, wt.HANDLE, c.POINTER(THREADENTRY32))
Toolhelp32ReadProcessMemory = get_fptr(
    "Toolhelp32ReadProcessMemory",
    wt.BOOL,
    wt.DWORD,
    wt.LPCVOID,
    wt.LPVOID,
    c.c_size_t,
    c.POINTER(c.c_size_t),
)
