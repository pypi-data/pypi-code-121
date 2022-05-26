import wx
from TimesheetExcelEditor.MyPanel import MyPanel


class MyFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="Timesheet Excel Editor", size=(800, 600),
                         style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.CenterOnScreen()
        self.EnableMaximizeButton(False)
        panel = MyPanel(self)
        self.Show()


def main():
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
