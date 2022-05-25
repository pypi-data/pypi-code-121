from numpy.core.arrayprint import _TimelikeFormat
from pydevmgr_core.base.node import BaseNode
from typing import Callable
from datetime import datetime
import time

class MaxIteration:
    """ A callable object returning True n times then False 

    Args:
        n (int): number of Iteration
    """
    def __init__(self, n: int):
        self.inc = 0
        self.n = n
    def __call__(self):
        self.inc += 1
        return self.inc<=self.n
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.n})"
    
class NodeIsTrue:
    """ A callable object returning True if the input node is evaluated True 

    Args:
        node (BaseNode): A node returning a value which can be evaluated to a boolean 
    """
    def __init__(self, node: BaseNode):
        self.node = node 
    def __call__(self):
        return bool(self.node.get())
    def __str__(self):
        return f"{self.__class__.__name__}({self.node})"

class NodeIsFalse:
    """ A callable object returning: True if the input node is evaluated False 

    Args:
        node (BaseNode): A node returning a value which can be evaluated to a boolean 
    """
    def __init__(self, node: BaseNode):
        self.node = node 
    def __call__(self):
        return not bool(self.node.get())
    def __str__(self):
        return f"{self.__class__.__name__}({self.node})"


class Reversed:
    """ A callable reversing the logic of an input signal (an other callable) 
    
    Args:
        signal (callable): a callable object with signature f() and returning a boolean 
    """
    def __init__(self, signal: Callable):
        self.signal = signal
    
    def __call__(self):
        return not self.signal()
    def __str__(self):
        return f"{self.__class__.__name__}({self.signal})"


class During:
    """ A callable object retuning True until the given time is elapsed 
    
    By default the timer start at first call
    
    Args:
        duration_time (float): in second 
        start_at_init (bool): False by default, set it to True to start the timer right now instead of during the first
        call
    """
    def __init__(self, duration_time,  start_at_init=False):
        if duration_time<0.0:
            raise ValueError("duration_time  must be >0.0 ")
        self.duration_time = duration_time
        self.start_time = None

        if start_at_init:
            self.start_time = time.time()

    def __call__(self):
        if self.start_time is None:
            self.start_time = time.time()
        return  (time.time()-self.start_time) < self.duration_time
    def __str__(self):
        return f"{self.__class__.__name__}({self.duration_time})"


class All:
    def __init__(self, *signals):
        self.signals = signals
     
    def __call__(self):
        return all( s() for s in self.signals)
    
    def __str__(self):
        str_signals = ", ".join( str(s) for s in self.signals)
        return f"{self.__class__.__name__}({str_signals})"

class Any:
    def __init__(self, *signals):
        self.signals = signals
     
    def __call__(self):
        return any( s() for s in self.signals)
    
    def __str__(self):
        str_signals = ", ".join( str(s) for s in self.signals)
        return f"{self.__class__.__name__}({str_signals})"



class Timeout:
    """ A callable object retuning False until the given time is elapsed 
    
    This is the reverse behavior of :class:`pydevmgr_core.signals.During`
    
    By default the timer start at first call
    
    Args:
        duration_time (float): in second 
        start_at_init (bool): False by default, set it to True to start the timer right now instead of during the first
        call
    """
    def __init__(self, duration_time,  start_at_init=False):
        if duration_time<0.0:
            raise ValueError("duration_time  must be >0.0 ")
        self.duration_time = duration_time
        self.start_time = None

        if start_at_init:
            self.start_time = time.time()

    def __call__(self):
        if self.start_time is None:
            self.start_time = time.time()
        return  (time.time()-self.start_time) > self.duration_time
    def __str__(self):
        return f"{self.__class__.__name__}({self.duration_time})"



