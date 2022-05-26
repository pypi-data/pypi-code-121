import wx
from . import config
from TimesheetExcelEditor.Excel import Excel


class CreatePanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        createBox = wx.BoxSizer(wx.HORIZONTAL)
        minLabel = wx.StaticText(self, label="Anno Min:")
        createBox.Add(minLabel, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL ^ wx.BOTTOM, border=10)
        self.yearMin = wx.TextCtrl(self)
        self.yearMin.SetHint("AAAA")
        self.yearMin.Bind(wx.EVT_CHAR, self.__handle_keypress)
        createBox.Add(self.yearMin, proportion=1, flag=wx.ALL ^ wx.LEFT, border=10)
        addLabel = wx.StaticText(self, label="Aggiungi:")
        createBox.Add(addLabel, proportion=0, flag=wx.ALL, border=10)
        self.yearAdd = wx.ComboBox(self, choices=["1", "2", "3", "4", "5"],
                                   style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.yearAdd.SetSelection(0)
        createBox.Add(self.yearAdd, proportion=1, flag=wx.ALL ^ wx.LEFT, border=10)
        createButton = wx.Button(self, label='Crea')
        createButton.Bind(wx.EVT_BUTTON, self.__create_button_press)
        createBox.Add(createButton, proportion=0, flag=wx.ALL, border=10)
        vbox.Add(createBox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(vbox)

    def __handle_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isnumeric() or keycode == 8:
                # Valid numeric character
                event.Skip()

    def __create_button_press(self, event):
        if not self.yearMin.IsEmpty() and self.yearMin.GetValue().isnumeric():
            wb = Excel().createWorkbook(self.yearMin.GetValue(), int(self.yearAdd.GetValue()))
            saveFileDialog = wx.FileDialog(self, "Save", "", "*.xlsx", "Exel files (*.xlsx)|*.xlsx",
                                           wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if saveFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            wb.save(saveFileDialog.GetPath())
            config.log.AppendText("File "+saveFileDialog.GetFilename()+" creato e salvato in "+saveFileDialog.GetPath()+"\n")
        else:
            missYearMin = wx.MessageDialog(None, "Inserire anno minimo", caption="Errore",
                                           style=wx.OK, pos=wx.DefaultPosition)
            if missYearMin.ShowModal() == wx.OK:
                return
