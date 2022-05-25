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
from PyQt5.QtWidgets import QLineEdit, QLabel, QCheckBox
from .style import get_style, STYLE
from .style import STYLE
from typing import Tuple, Any
import math

FLOAT_FMT = "%.3f"
FLOAT_DEFAULT = 0.0
INT_FMT = "%d"
INT_DEFAULT = 0
STR_FMT = "%s"
STR_DEFAULT = ""




def BOOL_FMT(b):
    """ CheckBox string representation"""
    return "[X]" if b else "[_]"
BOOL_DEFAULT = False

ENUM_FMT = "%s: %s"


def float_nan(t):
    """ return float(value) or None if value is a Nan """
    try:
        return float(t)
    except (ValueError, TypeError):
        return None

def int_nan(t):
    """ return int(value) or None if value is a Nan """
    try:
        return int(t)
    except (ValueError, TypeError):
        return None    


def switch_style(w,b):
    style = STYLE.SIMILAR if b else STYLE.DIFFERENT
    w.setStyleSheet(get_style(style))


def gattr(key):
    return lambda data: getattr(data, key)
    
def sattr(key):
    return lambda data, value: setattr(data, key, value)

def gsattr(key):
    return lambda data: getattr(data, key), lambda data, value: setattr(data, key, value)


def _dummy(data):
    pass

class BaseVal_IO:
    def __init__(self, set_input, set_output, get_input):
                        
        self.set_input  = set_input
        self.set = set_output
        self.get  = get_input        
        
    def disconnect(self):        
        self.set_input =  _dummy
        self.set = _dummy
        self.get = _dummy

class BaseVal_I:
    def __init__(self, set_input, get_input):
        self.set_input  = set_input        
        self.get  = get_input
    
    def set(self, data):
        raise ValueError("No widget output associated")
        
    def disconnect(self):        
        self.set_input =  _dummy        
        self.get = _dummy        

class BaseVal_O:
    def __init__(self, set_output):             
        self.set = set_output
    
    def set_input(self, data):
        raise ValueError("No widget input associated")
        
    def disconnect(self):          
        self.set = _dummy

class BoolVal_IO(BaseVal_IO):
    def __init__(self, input, output,  default=False, fmt=BOOL_FMT):            
        if hasattr(input, "setChecked") and hasattr(input, "isChecked"):
            def set_input(b):                
                input.setChecked(b)
            def get_input():
                return input.isChecked()                
        else:
            raise ValueError("expecting a QCheckBox as input  %s"%(type(input)))
        
        if hasattr(output, "setChecked"):
            def set_output(b):                           
                output.setChecked(b)
                switch_style(output, input.isChecked()==b)       
        
        elif  hasattr(output, "setText"):
            def set_output(b):
                t = fmt(b)                
                output.setText(t)
                switch_style(output, input.isChecked()==b)                
        else:
            raise ValueError("expecting a QLabel or QCheckbox as output got %s"%(type(output)))
                
        super().__init__(set_input, set_output, get_input)    
        if default is not None:        
            input.setChecked(default)

class BoolVal_O(BaseVal_O):
    def __init__(self, output, fmt=BOOL_FMT):   
        if hasattr(output, "setChecked"):
            def set_output(b):
                output.setChecked(b)
                switch_style(output, input.isChecked()==b)         
        elif hasattr(output, "setText"):
            def set_output(b):
                t = fmt(b)                
                output.setText(t)        
        else:
            raise ValueError("expecting a QCheckBox as input and QLabel as output got %s"%(type(output)))    
        super().__init__( set_output)

class BoolVal_I(BaseVal_I):    
    def __init__(self, input,  default=None):            
        if isinstance(input, QCheckBox):
            def set_input(b):                
                input.setChecked(b)
            
            def get_input():
                return input.isChecked()                
        else:
            raise ValueError("expecting a QCheckBox as input got %s"%(type(input)))    
        super().__init__(set_input, get_input)            
        if default is not None:
            input.setChecked(bool(default))


class NBoolVal_IO(BaseVal_IO):
    def __init__(self, input, output, default=False, fmt=BOOL_FMT):            
        if hasattr(input, "setChecked") and hasattr(input, "isChecked"):
            def set_input(b):                
                input.setChecked(not b)
            def get_input():
                return not input.isChecked()                
        else:
            raise ValueError("expecting a QCheckBox as input  %s, %s"%(type(input)))
        
        if hasattr(output, "setChecked"):
            def set_output(b):                           
                output.setChecked(not b)
                switch_style(output, input.isChecked()==(not b))       
        
        elif  hasattr(output, "setText"):
            def set_output(b):
                t = fmt(not b)                
                output.setText(t)
                switch_style(output, input.isChecked()==(not b))                
        else:
            raise ValueError("expecting a QLabel as output got %s, %s"%(type(output)))
                
        super().__init__(set_input, set_output, get_input)    
        if default is not None:        
            input.setChecked(bool(default))

class NBoolVal_O(BaseVal_O):
    def __init__(self, output, fmt=BOOL_FMT):   
        if hasattr(output, "setChecked"):
            def set_output(b):
                output.setChecked(not b)
                     
        elif hasattr(output, "setText"):
            def set_output(b):
                t = fmt(not b)                
                output.setText(t)        
        else:
            raise ValueError("expecting a QCheckBox as input and QLabel as output got %s"%(type(output)))    
        super().__init__(set_output)

class NBoolVal_I(BaseVal_I):    
    def __init__(self, input, default=False):            
        if isinstance(input, QCheckBox):
            def set_input(b):                
                input.setChecked(not b)
            
            def get_input():
                return not input.isChecked()                
        else:
            raise ValueError("expecting a QCheckBox as input and QLabel as output got %s"%(type(input)))    
        super().__init__(set_input, get_input)            
        input.setChecked(default)


class StrVal_IO(BaseVal_IO):
    def __init__(self, input, output,  fmt=STR_FMT, default=STR_DEFAULT):
        if isinstance(fmt, str):
            fmt = lambda x, fmt=fmt: fmt%x
        
        
        if hasattr(input, "setText") and hasattr(output, "setText"):
            def set_input(v):                    
                input.setText(fmt(v))
            def set_output(v):                
                t = fmt(v)                
                output.setText(t)
                switch_style(output, input.text()==t)
            def get_input():
                return input.text()                
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__( set_input,set_output,get_input)    
        if default is not None:
            input.setText(fmt(default))

class StrVal_I(BaseVal_I):
    def __init__(self, input, feedback=None, fmt=STR_FMT, default=STR_DEFAULT):    
        if isinstance(fmt, str):
            fmt = lambda x, fmt=fmt: fmt%x
            
        
        if hasattr(input, "setText"):
            def set_input(v):                   
                input.setText(fmt(v))            
            def get_input():
                return input.text()                
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input, get_input)    
        if default is not None:
            input.setText(fmt(default))
            

class StrVal_O(BaseVal_O):
    def __init__(self, output,  fmt=STR_FMT):
        if isinstance(fmt, str):
            fmt = lambda x,fmt=fmt: fmt%x
                
        if hasattr(output, "setText"):            
            def set_output(v):
                t = fmt(v)                
                output.setText(t)                            
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_output)        


class FloatVal_IO(BaseVal_IO):
    def __init__(self, input, output, feedback=None, fmt=FLOAT_FMT, default=FLOAT_DEFAULT):
        if isinstance(fmt, str):
            fmt = lambda x, fmt=fmt: fmt%x
        
        
        if hasattr(input, "setText") and hasattr(output, "setText"):
            def set_input(v):                        
                input.setText(fmt(v))
            
            def set_output(v):                
                t = fmt(v)                
                output.setText(t)
                switch_style(output, float_nan(input.text())==v)
                
            def get_input():
                try:
                    return float(input.text())  
                except ( TypeError, ValueError):
                    return math.nan

        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input, set_output, get_input)    
        if default is not None:
            input.setText(fmt(default))

class FloatVal_I(BaseVal_I):
    def __init__(self, input, fmt=FLOAT_FMT, default=FLOAT_DEFAULT):    
        if isinstance(fmt, str):
            fmt = lambda x, fmt=fmt: fmt%x
            
        
        if hasattr(input, "setText"):
            def set_input(v):                           
                input.setText(fmt(v))            
            def get_input():
                try:
                    return float(input.text())  
                except ( TypeError, ValueError):
                    return math.nan
                                    
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input,get_input)    
        if default is not None:
            input.setText(fmt(default))
            

class FloatVal_O(BaseVal_O):
    def __init__(self, output,  fmt=FLOAT_FMT):
        if isinstance(fmt, str):
            fmt = lambda x,fmt=fmt: fmt%x
                
        if hasattr(output, "setText"):            
            def set_output(v):                
                t = fmt(v)                
                output.setText(t)                            
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_output)        

class IntVal_IO(BaseVal_IO):
    def __init__(self,  input, output,fmt=INT_FMT, default=INT_DEFAULT):
        if isinstance(fmt, str):
            fmt = lambda x,fmt=fmt: fmt%x
                
        
        if hasattr(input, "setText") and hasattr(output, "setText"):
            def set_input(v):                            
                input.setText(fmt(v))
            def set_output(v):
                t = fmt(v)               
                output.setText(t)
                switch_style(output, int_nan(input.text())==v)
            def get_input():
                return int(input.text())                
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input, set_output, get_input)    
        if default is not None:
            input.setText(fmt(default))

class IntVal_I(BaseVal_I):
    def __init__(self, input,  fmt=INT_FMT, default=INT_DEFAULT):
        if isinstance(fmt, str):
            fmt = lambda x,fmt=fmt: fmt%x
                
        
        if hasattr(input, "setText"):
            def set_input(v):
                input.setText(fmt(v))            
            def get_input():
                return int(input.text())                
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input,get_input)    
        if default is not None:
            input.setText(fmt(default))

class IntVal_O(BaseVal_O):
    def __init__(self,  output,  fmt=INT_FMT):
        if isinstance(fmt, str):
            fmt = lambda x,fmt=fmt: fmt%x
                        
        if hasattr(output, "setText"):            
            def set_output(v):                
                t = fmt(v)               
                output.setText(t)            
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_output)        

        
class EnumVal_IO(BaseVal_IO):    
    def __init__(self,  enum, input, output,  fmt="%s: %s", default=None):
    
        num_to_index = {e.value:i for i,e in enumerate(enum)}
        index_to_num = {i:e.value for i,e in enumerate(enum)}
        
        if isinstance(fmt, str):
            fmt = lambda x,y,fmt=fmt: fmt%(x,y)
            
        if hasattr(input, "setCurrentIndex") and hasattr(output, "setText"):
            def set_input(v):                            
                input.setCurrentIndex( num_to_index[v] )
                
            def set_output(a):
                a =  enum(a)                                                
                output.setText( fmt(a.value, a.name))             
                switch_style(output, input.currentIndex()==num_to_index[a.value])
                
            def get_input():
                i = input.currentIndex()
                return index_to_num[i]                
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__( set_input, set_output, get_input)  
        input.clear()
        input.addItems( [a.name for a in enum] )
        if default is not None:
            input.setCurrentIndex( num_to_index[default] )    

class EnumVal_I(BaseVal_I):
    
    def __init__(self, enum, input, default=None):
        
        num_to_index = {e.value:i for i,e in enumerate(enum)}
        index_to_num = {i:e.value for i,e in enumerate(enum)}
        if hasattr(input, "setCurrentIndex"):
            def set_input(v):                             
                input.setCurrentIndex( num_to_index[v] )
                            
            def get_input():
                i = input.currentIndex()                
                return  index_to_num[i]
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_input,get_input)  
        input.clear()
        input.addItems( [a.name for a in enum] )
        if default is not None:
            input.setCurrentIndex( num_to_index[default] )    

        
class EnumVal_O(BaseVal_O):   
    def __init__(self, enum, output, fmt="%s: %s"):
        num_to_index = {e.value:i for i,e in enumerate(enum)}
        
        if isinstance(fmt, str):
            fmt = lambda x,y,fmt=fmt: fmt%(x,y)
        
        if hasattr(output, "setText"):                            
            def set_output(a):
                a =  enum(a)                                                
                output.setText( fmt(a.value, a.name))               
                switch_style(output, input.currentIndex()==num_to_index[a.value])                            
        else:
            raise ValueError("Invalid input output combination")    
        super().__init__(set_output)     


class Feedback_O(BaseVal_O):
    """ A feedback widget takes a couple of (er, msg) 
    
    if er the text msg is screened with an STYLE.ERROR  style 
    else  msg is screened with an STYLE.NORMAL  style 
    """
    def __init__(self, output):                
        if hasattr(output, "setText") and hasattr(output, "setStyleSheet") :                            
            def set_output(er_msg: Tuple[Any,str]) -> None:
                er,msg = er_msg
                if er:
                    output.setStyleSheet(get_style(STYLE.ERROR))    
                else:
                    output.setStyleSheet(get_style(STYLE.NORMAL))                        
                output.setText(msg)                                   
        else:
            raise ValueError("Invalid input output combination")            
        super().__init__(set_output)
        


class Inputs:
    Base = BaseVal_I
    Bool = BoolVal_I
    NBool = NBoolVal_I
    Str = StrVal_I
    Float = FloatVal_I
    Int = IntVal_I
    Enum = EnumVal_I

class Outputs:
    Base = BaseVal_O
    Bool = BoolVal_O
    NBool = NBoolVal_O
    Str = StrVal_O
    Float = FloatVal_O
    Int = IntVal_O
    Enum = EnumVal_O  
    Feedback = Feedback_O  

class InputOutputs:
    Base = BaseVal_IO
    Bool = BoolVal_IO
    NBool = NBoolVal_IO
    Str = StrVal_IO
    Float = FloatVal_IO
    Int = IntVal_IO
    Enum = EnumVal_IO    




        
