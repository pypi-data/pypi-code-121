from pydevmgr_core_qt import Outputs, get_style

class CodeVal_O(Outputs.Base):
    """ widget output for a trio of (code, txt, group) 
    
    e.g. for a substate we get the substate code, its text representation and the group which will 
          be used to color the label. Note that group is a pydevmgr thing only.
    """
    def __init__(self, output, fmt="%s: %s"):
        if isinstance(fmt, str):
            fmt = lambda x,y, fmt=fmt: fmt%(x,y)
        
        if hasattr(output, "setText") and hasattr(output, "setStyleSheet") :                            
            def set_output(ctg): # code, text, group 
                c,t,g = ctg
                output.setText(fmt(c,t))
                output.setStyleSheet(get_style(g))                       
        else:
            raise ValueError("Invalid input output combination")            
        super().__init__(set_output)
Outputs.Code = CodeVal_O 