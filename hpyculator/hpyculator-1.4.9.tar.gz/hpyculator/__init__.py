"""默认导入hpycore的所有属性和函数，易于使用"""
from .hpycore import *

name = "hpyculator"
__all__ = ["hpy" + body for body in "core,signal,decorator".split(",")]
__version__ = "1.4.8"
