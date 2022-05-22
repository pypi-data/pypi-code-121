# clipboard.py: functions for reading and writing to the clipboard
from xtlib import errors

win32clipboard = None

class Clipboard():

    def __init__(self): 
        global win32clipboard
        import win32clipboard
        
        win32clipboard.OpenClipboard(0)
        #self.CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        self.popular_val2str = {val: name for name, val in vars(win32clipboard).items() if name.startswith('CF_')}
        self.popular_str2val = {name: val for name, val in vars(win32clipboard).items() if name.startswith('CF_')}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32clipboard.CloseClipboard()

    def enum_formats(self):
        formats = {}

        xxx = 0
        while True:
            xxx = win32clipboard.EnumClipboardFormats(xxx)
            if xxx==0:
                break

            key = xxx
            if key in self.popular_val2str:
                value = self.popular_val2str[key]
            else:
                value = win32clipboard.GetClipboardFormatName(key)

            formats[key] = value
        
        return formats
    
    def get_contents(self, format, as_string=True):
        format = self.ensure_int_format(format)
        rt = win32clipboard.GetClipboardData(format)

        if as_string:
            rt = rt.decode("LATIN-1")
        return rt

    def ensure_int_format(self, format):
        if isinstance(format, str):
            if format in self.popular_str2val:
                format = self.popular_str2val[format]
            else:
                format = win32clipboard.RegisterClipboardFormat(format)

        return format

    def set_contents(self, format, data, clear_other_formats=True):
        if clear_other_formats:
            win32clipboard.EmptyClipboard()

        format = self.ensure_int_format(format)
        win32clipboard.SetClipboardData(format, data)    

def test_enum():
    with Clipboard() as cb:
        formats = cb.enum_formats()
        print("enum_formats:", formats)

def test_set():
    with Clipboard() as cb:
        cb.set_contents("CF_TEXT", "this is a test")
        formats = cb.enum_formats()
        print("test_set:", formats)

def test_get():
    with Clipboard() as cb:
        value = cb.get_contents("CF_TEXT")
        print("test_get:", value)

if __name__ == "__main__":
    test_enum()    
    test_set()    
    test_get()

