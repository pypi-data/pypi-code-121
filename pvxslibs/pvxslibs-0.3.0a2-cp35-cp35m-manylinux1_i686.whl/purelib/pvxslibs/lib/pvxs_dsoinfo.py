
# generated by setuptools_dso
import os

dsoname = 'pvxslibs.lib.pvxs'
libname = 'libpvxs.so'
soname = 'libpvxs.so.0.3'
depends = ['epicscorelibs.lib.Com', 'pvxslibs.lib.event_core', 'pvxslibs.lib.event_pthread']
dir = os.path.dirname(__file__)
filename = os.path.join(dir, libname)
sofilename = os.path.join(dir, soname)
del dir
del os
__all__ = ("dsoname", "libname", "soname", "filename", "sofilename")
