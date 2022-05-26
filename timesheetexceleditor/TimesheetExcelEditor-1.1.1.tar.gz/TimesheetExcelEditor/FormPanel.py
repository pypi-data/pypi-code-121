import wx
from . import config


class FormPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        dl = wx.StaticText(self, label="Data")
        hbox.Add(dl, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        self.data = wx.TextCtrl(self)
        self.data.SetHint("gg/mm/aaaa")
        hbox.Add(self.data, proportion=1, flag=wx.ALL, border=10)
        nol = wx.StaticText(self, label="Numero ore")
        hbox.Add(nol, proportion=0, flag=wx.ALL, border=10)
        self.numOre = wx.TextCtrl(self)
        self.numOre.Bind(wx.EVT_CHAR, self.__handle_keypress)
        hbox.Add(self.numOre, proportion=1, flag=wx.ALL, border=10)
        config.formModifyButton = wx.Button(self, label='Modifica')
        config.formModifyButton.Bind(wx.EVT_BUTTON, self.__form_modify_button_press)
        config.formModifyButton.Disable()
        hbox.Add(config.formModifyButton, proportion=0, flag=wx.ALL, border=10)
        self.saveButton = wx.Button(self, label="Salva")
        self.saveButton.Bind(wx.EVT_BUTTON, self.__save_button_press)
        self.saveButton.Disable()
        hbox.Add(self.saveButton, proportion=0, flag=wx.ALL, border=10)

        vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(vbox)

    def __handle_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isnumeric() or keycode == 8:
                # Valid numeric character
                event.Skip()

    def __form_modify_button_press(self, event):
        if not self.data.IsEmpty() and config.checkDate(self.data.GetValue()):
            if not self.numOre.IsEmpty():
                multiplier = config.multiplier.GetStringSelection()
                activity = config.acSelect.GetStringSelection()
                config.file.modify(activity, self.data.GetValue(), int(self.numOre.GetValue()), float(multiplier))
                modified = wx.MessageDialog(None, "Modificato", caption="Info",
                                            style=wx.OK, pos=wx.DefaultPosition)
                if modified.ShowModal() == wx.OK:
                    return
                self.saveButton.Enable()
                if config.file.checkMissing():
                    message = config.file.getMissing()
                    config.log.AppendText(message+"\n")
            else:
                missHours = wx.MessageDialog(None, "Inserire un numero di ore", caption="Errore",
                                             style=wx.OK, pos=wx.DefaultPosition)
                if missHours.ShowModal() == wx.OK:
                    return
        else:
            missDate = wx.MessageDialog(None, "Data mancante o non valida", caption="Errore",
                                        style=wx.OK, pos=wx.DefaultPosition)
            if missDate.ShowModal() == wx.OK:
                return

    def __save_button_press(self, event):
        file = config.file
        saveFileDialog = wx.FileDialog(self, "Save", "", config.file.getFileName(), "Exel files (*.xlsx)|*.xlsx",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        file.save(saveFileDialog.GetPath())
