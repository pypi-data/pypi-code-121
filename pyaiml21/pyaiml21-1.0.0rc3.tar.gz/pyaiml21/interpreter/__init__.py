"""
The AIML Interpreter.

This package contains the implementation of AIML 2.1 compatible
interpreter for `pyaiml21`.

In addition to the interpreter, the module offers an interactive
debugger to check the AIML source code.
"""
from .walker import Interpreter, AIMLEvalFun
from .debugger import Debugger

__all__ = ["Interpreter", "Debugger", "AIMLEvalFun"]
