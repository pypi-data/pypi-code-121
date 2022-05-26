import wx
import re
from . import config


class ListPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        listlabel = wx.StaticText(self, label="Elenco")
        hbox.Add(listlabel, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        self.elenco = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        hbox.Add(self.elenco, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        config.listModifyButton = wx.Button(self, label='Modifica')
        config.listModifyButton.Bind(wx.EVT_BUTTON, self.__list_modify_button_press)
        config.listModifyButton.Disable()
        hbox.Add(config.listModifyButton, proportion=0, flag=wx.ALL, border=10)
        self.saveButton = wx.Button(self, label="Salva")
        self.saveButton.Bind(wx.EVT_BUTTON, self.__save_button_press)
        self.saveButton.Disable()
        hbox.Add(self.saveButton, proportion=0, flag=wx.ALL, border=10)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(vbox)

    def __checkList(self):
        num = self.elenco.GetNumberOfLines()
        for i in range(num):
            line = self.elenco.GetLineText(i)
            if not re.match("\d{1,2}/\d{2}/\d{4} \d+", line):
                return False
            date, hours = line.split(" ")
            if not config.checkDate(date):
                return False
        return True

    def __list_modify_button_press(self, event):
        activity = config.acSelect.GetStringSelection()
        multiplier = config.multiplier.GetStringSelection()
        if not self.elenco.IsEmpty() and self.__checkList():
            num = self.elenco.GetNumberOfLines()
            for i in range(num):
                line = self.elenco.GetLineText(i)
                date, hours = line.split(" ")
                config.file.modify(activity, date, int(hours), float(multiplier))
            modified = wx.MessageDialog(None, "File modificato", caption="Info",
                                        style=wx.OK, pos=wx.DefaultPosition)
            if modified.ShowModal() == wx.OK:
                return
            if config.file.checkMissing():
                message = config.file.getMissing()
                config.log.AppendText(message+"\n")
            self.saveButton.Enable()
        else:
            missList = wx.MessageDialog(None, "Inserire elenco formato:data nOre", caption="Errore",
                                        style=wx.OK, pos=wx.DefaultPosition)
            if missList.ShowModal() == wx.OK:
                return

    def __save_button_press(self, event):
        file = config.file
        saveFileDialog = wx.FileDialog(self, "Save", "", config.file.getFileName(), "Exel files (*.xlsx)|*.xlsx",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        file.save(saveFileDialog.GetPath())
