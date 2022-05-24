"""
基础的异常处理逻辑
"""
import sys


def callback(*args, **kwargs):
    # 系统对于没有被捕获的异常，python统一用sys.excepthook 这个函数来处理，发生异常时，程序中断并输出很多异常信息。
    # python允许你重写这个方法，来实现你自己对异常的处理，
    sys.excepthook(*args, **kwargs)


def my_excepthook(exc_type, exc_value, tb):
    """
    该异常用于替换 sys.excepthook 也就是自定义全局异常处理逻辑
    :param exc_type:
    :param exc_value:
    :param tb:
    :return:
    """
    callback(exc_type, exc_value, tb)


class BaseExcept(object):
    """
    from billiard.einfo import Traceback
    self.tb : Traceback
    """

    def __init__(self):
        self.tb = None

    def set_tb(self, tb):
        self.tb = tb
        return self

    def tb_par(self):
        # 栈跟踪的下一级(朝发生异常的执行帧方向深入)
        tb_next = self.tb.tb_next
        # 当前级别的执行帧对象
        tb_frame = self.tb.tb_frame
        # 出现的行号
        lineno = self.tb.tb_lineno
        # 当前级别中正在执行的指令
        tb_lasti = self.tb.tb_lasti

    def tb_frame_par(self, tb_frame):
        """
        每个帧对象具有的属性
        :param tb_frame:
        :return:
        """
        # 上一个栈帧(对当前调用者而言)
        f_back = tb_frame.f_back
        # 正在执行的代码对象
        f_code = tb_frame.f_code  #
        # 局部变量字典
        f_locals = tb_frame.f_locals
        # 全局变量
        f_globals = tb_frame.f_globals
        # 内置名称的字典
        f_builtins = tb_frame.f_builtins
        # 行号
        f_lineno = tb_frame.f_lineno
        # 当前指令。这是f_code 字节码字符串的索引
        f_lasti = tb_frame.f_lasti
        # (可修改属性) 在每行源代码起始处调用的函数
        f_trace = tb_frame.f_trace

        f_restricted = tb_frame.f_restricted

        f_exc_traceback = tb_frame.f_exc_traceback
        f_exc_type = tb_frame.f_exc_type
        f_exc_value = tb_frame.f_exc_value

    def f_code_par(self, f_code):
        # 函数名称
        co_name = f_code.co_name
        # 位置参数个数(包含默认值)
        co_argcount = f_code.co_argcount
        # 函数使用的局部变量个数
        co_nlocals = f_code.co_nlocals
        # 字符串编码字节码相对于行号的偏移
        co_lnotab = f_code.co_lnotab
        # 被编译代码所在文件的名称
        co_filename = f_code.co_filename
        # 包含嵌套函数所引用的变量名称的元组
        co_cellvars = f_code.co_cellvars
        # 函数的首行行号
        co_firstlineno = f_code.co_firstlineno
        # 包含解释器标志的整数
        co_flags = f_code.co_flags
        # 包含嵌套函数所引用的自由变量名称的元组
        co_freevars = f_code.co_freevars
        # 表示原始字节码的字符串
        co_code = f_code.co_code
        # 包含字节码所用名称的元组
        co_names = f_code.co_names
        # 所需栈的大小（包括局部变量）
        co_stacksize = f_code.co_stacksize
        # 包含局部变量名称的元组
        co_varnames = f_code.co_varnames


def reraise(tp, value, tb=None):
    """Reraise exception."""
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value
