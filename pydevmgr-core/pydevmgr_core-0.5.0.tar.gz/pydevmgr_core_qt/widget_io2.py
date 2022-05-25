""" The idea here is to create interface between a data value and a widget 



Three type of interfaces :
    - input : The widget is a text, checkbox, button, etc .. and the data is an input of the application
            It has the methods:
                 set_input(val) :  update the input widget with given value
                 get_input()    :  retrieve the value with the right data type
                 
    - output: The widget is a representation of a value, e.g. QLabel the data is an output of the application 
            It has the methods:
                set_output(val) : update the output widget (e.g. QLabel) with the value of dtype
     
    - input output: Two widgets represent input and output if they differ the output is hilighted in red 
                    This is to be used in a config pannel for instance
            t has the methods:
                 set_input(val)   
                 set_output(val) 
                 get_input()  
                 
    Each of the interface has a variable number of argument and keyword depending on the nature of 
    the data value. 
    For performance purpose The update_* methods are created at frontend in the __init__ 
    function to widgets types. This is to avoid things like isinstance(widget, QLabel) at run time 
    The init shall handle how to update and get widget. So far only used case are set, one can increase 
    the diversity of used widget used.
"""

from collections import OrderedDict
from pydantic import BaseModel
from typing import Callable

def output(cond, func=None):
    if func is None:
        return Output(cond).funcsetter
    else:
        return Output(cond, func)
        
class Output:
    def __init__(self, cond, func=None):
        self.func = func
        self.cond = cond
    
    def funcsetter(self, func):
        self.func = func
        return self
    
    def build(self, output_widget, config):
        return self.func(output_widget, config)
    
    def check(self, output_widget):
        return self.cond(output_widget)    
            
class OutputType(type):
    def __new__(cls, name, bases, d):
        
        _outputs = []
        
        for k,v in d.items():
            if isinstance(v, Output):
                _outputs.append(v) 
        d ['__outputs__'] = _outputs        
        return type.__new__(cls, name, bases, d)
    
class OutputVal(metaclass=OutputType):
    class Config(BaseModel):
        pass
        
    def __init__(self, output_widget, config=None, **kwargs):        
        self.config = self.parse_config(config, **kwargs)
        for fout in self.__outputs__:
            if fout.check(output_widget):
                set = fout.build( output_widget, self.config)
                break
        else:
            raise ValueError(f"Cannot found suitable output for class {self.__class__.__name__} and widget {type(output_widget)}")
        
        self.set = set 
        
            
        
    @classmethod
    def parse_config(cls, __config__=None, **kwargs):
        if __config__ is None:
            return cls.Config(**kwargs)
        if isinstance(__config__ , cls.Config):
            return __config__
        if isinstance(__config__, dict):
            return cls.Config( **{**__config__, **kwargs} )
        raise ValueError(f"got an unexpected object for config : {type(__config__)}")


class BoolVal_O(OutputVal):
    class Config(OutputVal.Config):
        fmt: Callable  = staticmethod(lambda v: "[X]" if v else "[ ]")
    
    @output(lambda w: hasattr(w, "setText"))
    def _text_output_builder(w, c):
        def set_output(b):
            t = c.fmt(b)                
            w.setText(t)     
        return set_output
    
            
    
    
        
