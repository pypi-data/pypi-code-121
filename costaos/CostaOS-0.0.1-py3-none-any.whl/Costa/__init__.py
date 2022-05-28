import win32gui
from tkinterweb import HtmlFrame

class Enbed():
    def __init__(self):
        self.pid = None
    def window(self,id):
        try:
            win32gui.SetParent(self.pid,id)
            return True
        except:
            return WindowsError("Please use the getpid() module first")
    def get_pid(self,name):
        self.pid = win32gui.FindWindow(None, name)
    def html(self,html,window,noscript=False):
        if noscript:
            frame = HtmlFrame(window)
            frame.load_website(html)
            return frame