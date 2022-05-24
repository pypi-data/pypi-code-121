_ffi, _cjudy = None, None


def _load():
    global _ffi, _cjudy
    import ctypes.util
    from ._judy_cffi import ffi

    cjudy = ffi.dlopen(ctypes.util.find_library("Judy"))
    _ffi, _cjudy = ffi, cjudy
