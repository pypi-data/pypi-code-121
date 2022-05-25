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



class WidgetLink:
    def __init__(self, widget, config):
        self._widget = widget
        self._config = config
    
    def set(self, value):
        raise NotImplementedError("set")
    
    @classmethod
    def accept(cls, widget):
        raise NotImplementedError("accept") 

class Input:
    def __init__(self, widget, config):
        self._widget = widget
        self._config = config
    
    def set(self, value):
        raise NotImplementedError("set")
    
    @classmethod
    def accept(cls, widget):
        raise NotImplementedError("accept") 



def _found_handler(cls, widget):
    for sub in cls.__mro__:
        for key, Obj in sub.__dict__.items():
            if isinstance(Obj, type) and issubclass(Obj, Output):
                if Obj.accept(widget):
                    return Obj
                    
    raise ValueError(f"Cannot found suitable output for class {cls.__name__} and widget {type(widget)}")
            


class _BaseVal_:
    @classmethod
    def parse_config(cls, __config__=None, **kwargs):
        if __config__ is None:
            return cls.Config(**kwargs)
        if isinstance(__config__ , cls.Config):
            return __config__
        if isinstance(__config__, dict):
            return cls.Config( **{**__config__, **kwargs} )
        raise ValueError(f"got an unexpected object for config : {type(__config__)}")



    
class OutputVal(_BaseVal_):
    class Config(BaseModel):
        pass
        
    def __init__(self, output_widget, config=None, **kwargs):        
        self.config = self.parse_config(config, **kwargs)        
        self.set = _found_handler(self.__class__, output_widget)(output_widget, self.config).set
                

class InputVal(_BaseVal_):
    class Config(BaseModel):
        pass

    def __init__(self, input_widget, config=None, **kwargs):
        self.config = self.parse_config(config, **kwargs)
        wh = _found_handler(self.__class__, input_widget)(input_widget, self.config)
        self.set_input = wh.set
        self.get = wh.get
        

class BoolCheck(WidgetLink):
    @classmethod
    def accept(cls, w):
        return hasattr(w, "setChecked")
    def set(self, b):
        return self._widget.setChecked(b)
    def get(self):
        return self._widget.isChecked()
    
class BoolLabel(WidgetLink):
    @classmethod
    def accept(cls, w):
        return hasattr(w, "setText") 
    def set(self, b):
        self._widget.setText( self._config.fmt(b) )     

   



class BoolVal_O(OutputVal):
    class Config(OutputVal.Config):
        fmt: Callable  = staticmethod(lambda v: "[X]" if v else "[ ]")
    
    BoolCheck = BoolCheck
    BoolLabel = BoolLabel



class BoolVal_I(InputVal):
    BoolCheck


            
