from enum import Enum 

class _S(str):
    def __init__(self, s, style=""):
        super().__init__(s)
        self.style = style
        
class STYLE(str, Enum):
    """ A collection of style IDs derived from GROUPs in pydevmgr + extra stuff """
    IDL       = "IDL"
    WARNING   = "WARNING"
    ERROR     = "ERROR"
    OK        = "OK"
    NOK       = "NOK"
    BUZY      = "BUZY"
    UNKNOWN   = "UNKNOWN"
    NORMAL    = "NORMAL"
    ODD       = "ODD"
    EVEN      = "EVEN"
    ERROR_TXT = "ERROR_TXT"
    OK_TXT    = "OK_TXT"
    DIFFERENT = "DIFFERENT"
    SIMILAR   = "SMILAR"

    
""" Associate STYLE IDs to qt stylSheet """
_qt_style_loockup = {
    STYLE.NORMAL  : "background-color: white;",
    STYLE.IDL     : "background-color: white;",
    STYLE.WARNING : "background-color: #ff9966;",
    STYLE.ERROR   : "background-color: #cc3300;",
    STYLE.OK      : "background-color: #99cc33;",
    STYLE.NOK     : "background-color: #ff9966;",
    STYLE.BUZY    : "background-color: #ffcc00;",
    STYLE.UNKNOWN : "",
    STYLE.ODD     : "background-color: #E0E0E0;",
    STYLE.EVEN    : "background-color: #F8F8F8;",
    STYLE.ERROR_TXT : "color: #cc3300;",
    STYLE.OK_TXT : "color: black;",
    STYLE.DIFFERENT : "color: #cc3300;",
    STYLE.SIMILAR: "color: black;",
}
class STYLE_DEF:
    pass

for _N, _S in _qt_style_loockup.items():
    setattr(STYLE_DEF, _N, _S)
del _N, _S, _qt_style_loockup
    
def get_style(style):
    """ return the style of a given style name """
    return getattr(STYLE_DEF, style, "")
