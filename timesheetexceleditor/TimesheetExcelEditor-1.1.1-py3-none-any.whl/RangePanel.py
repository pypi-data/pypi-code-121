import wx
from . import config
from datetime import datetime as dt, timedelta


class RangePanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        rangeBox = wx.BoxSizer(wx.HORIZONTAL)
        minLabel = wx.StaticText(self, label="Data Min:")
        rangeBox.Add(minLabel, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL ^ wx.BOTTOM, border=10)
        self.dataMin = wx.TextCtrl(self)
        self.dataMin.SetHint("gg/mm/aaaa")
        rangeBox.Add(self.dataMin, proportion=1, flag=wx.EXPAND | wx.ALL ^ wx.LEFT, border=10)
        maxLabel = wx.StaticText(self, label="Data Max:")
        rangeBox.Add(maxLabel, proportion=0, flag=wx.ALL, border=10)
        self.dataMax = wx.TextCtrl(self)
        self.dataMax.SetHint("gg/mm/aaaa")
        rangeBox.Add(self.dataMax, proportion=1, flag=wx.EXPAND | wx.ALL ^ wx.LEFT, border=10)
        config.rangeModifyButton = wx.Button(self, label='Modifica')
        config.rangeModifyButton.Bind(wx.EVT_BUTTON, self.__range_modify_button_press)
        config.rangeModifyButton.Disable()
        rangeBox.Add(config.rangeModifyButton, proportion=0, flag=wx.ALL, border=10)
        self.saveButton = wx.Button(self, label="Salva")
        self.saveButton.Bind(wx.EVT_BUTTON, self.__save_button_press)
        self.saveButton.Disable()
        rangeBox.Add(self.saveButton, proportion=0, flag=wx.ALL ^ wx.LEFT, border=10)
        vbox.Add(rangeBox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        mondayBox = wx.BoxSizer(wx.HORIZONTAL)
        mLabel = wx.StaticText(self, label="Lunedì")
        mondayBox.Add(mLabel, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL ^ wx.TOP, border=10)
        self.mondayHours = wx.TextCtrl(self)
        self.mondayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        self.mondayHours.SetHint("Num ore")
        mondayBox.Add(self.mondayHours, proportion=0, flag=wx.ALL ^ wx.TOP ^ wx.BOTTOM, border=10)
        vbox.Add(mondayBox, proportion=0, flag=wx.ALL, border=5)

        tuesdayBox = wx.BoxSizer(wx.HORIZONTAL)
        tLabel = wx.StaticText(self, label="Martedì")
        tuesdayBox.Add(tLabel, proportion=0, flag=wx.ALL ^ wx.TOP, border=10)
        self.tuesdayHours = wx.TextCtrl(self)
        self.tuesdayHours.SetHint("Num ore")
        self.tuesdayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        tuesdayBox.Add(self.tuesdayHours, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        vbox.Add(tuesdayBox, proportion=0, flag=wx.ALL, border=5)

        wednesdayBox = wx.BoxSizer(wx.HORIZONTAL)
        mLabel = wx.StaticText(self, label="Mercoledì")
        wednesdayBox.Add(mLabel, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        self.wednesdayHours = wx.TextCtrl(self)
        self.wednesdayHours.SetHint("Num ore")
        self.wednesdayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        wednesdayBox.Add(self.wednesdayHours, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        vbox.Add(wednesdayBox, proportion=0, flag=wx.ALL, border=5)

        thursdayBox = wx.BoxSizer(wx.HORIZONTAL)
        mLabel = wx.StaticText(self, label="Giovedì")
        thursdayBox.Add(mLabel, proportion=0, flag=wx.ALL ^ wx.TOP, border=10)
        self.thursdayHours = wx.TextCtrl(self)
        self.thursdayHours.SetHint("Num ore")
        self.thursdayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        thursdayBox.Add(self.thursdayHours, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        vbox.Add(thursdayBox, proportion=0, flag=wx.ALL, border=5)

        fridayBox = wx.BoxSizer(wx.HORIZONTAL)
        fLabel = wx.StaticText(self, label="Venerdi")
        fridayBox.Add(fLabel, proportion=0, flag=wx.ALL ^ wx.TOP, border=10)
        self.fridayHours = wx.TextCtrl(self)
        self.fridayHours.SetHint("Num ore")
        self.fridayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        fridayBox.Add(self.fridayHours, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        vbox.Add(fridayBox, proportion=0, flag=wx.ALL, border=5)

        saturdayBox = wx.BoxSizer(wx.HORIZONTAL)
        sLabel = wx.StaticText(self, label="Sabato")
        fridayBox.Add(sLabel, proportion=0, flag=wx.ALIGN_TOP | wx.ALL ^ wx.TOP, border=10)
        self.saturdayHours = wx.TextCtrl(self)
        self.saturdayHours.SetHint("Num ore")
        self.saturdayHours.Bind(wx.EVT_CHAR, self.__handle_keypress)
        fridayBox.Add(self.saturdayHours, proportion=0, flag=wx.ALL ^ wx.TOP, border=5)
        vbox.Add(saturdayBox, proportion=0, flag=wx.ALL, border=5)

        self.SetSizer(vbox)

    def __handle_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isnumeric() or keycode == 8:
                # Valid numeric character
                event.Skip()

    def __range_modify_button_press(self, event):
        activity = config.acSelect.GetStringSelection()
        multiplier = config.multiplier.GetStringSelection()
        if not self.dataMin.IsEmpty() and config.checkDate(self.dataMin.GetValue()):
            if not self.dataMax.IsEmpty() and config.checkDate(self.dataMin.GetValue()):
                monday = tuesday = wednesday = thursday = friday = saturday = None
                rangeStart = dt.strptime(self.dataMin.GetValue(), "%d/%m/%Y")
                rangeEnd = dt.strptime(self.dataMax.GetValue(), "%d/%m/%Y")
                if not self.mondayHours.IsEmpty():
                    monday = self.mondayHours.GetValue()
                if not self.tuesdayHours.IsEmpty():
                    tuesday = self.tuesdayHours.GetValue()
                if not self.wednesdayHours.IsEmpty():
                    wednesday = self.wednesdayHours.GetValue()
                if not self.thursdayHours.IsEmpty():
                    thursday = self.thursdayHours.GetValue()
                if not self.fridayHours.IsEmpty():
                    friday = self.fridayHours.GetValue()
                if not self.saturdayHours.IsEmpty():
                    saturday = self.saturdayHours.GetValue()
                while rangeEnd >= rangeStart:
                    if monday is not None:
                        if rangeStart.strftime("%A") == "Monday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(monday), float(multiplier))
                    if tuesday is not None:
                        if rangeStart.strftime("%A") == "Tuesday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(tuesday), float(multiplier))
                    if wednesday is not None:
                        if rangeStart.strftime("%A") == "Wednesday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(wednesday), float(multiplier))
                    if thursday is not None:
                        if rangeStart.strftime("%A") == "Thursday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(thursday), float(multiplier))
                    if friday is not None:
                        if rangeStart.strftime("%A") == "Friday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(friday), float(multiplier))
                    if saturday is not None:
                        if rangeStart.strftime("%A") == "Saturday":
                            d = rangeStart.strftime("%d/%m/%Y")
                            config.file.modify(activity, d, int(saturday), float(multiplier))
                    rangeStart = rangeStart + timedelta(days=1)
                modified = wx.MessageDialog(None, "File modificato", caption="Info",
                                            style=wx.OK, pos=wx.DefaultPosition)
                if modified.ShowModal() == wx.OK:
                    return
                if config.file.checkMissing():
                    message = config.file.getMissing()
                    config.log.AppendText(message + "\n")
                self.saveButton.Enable()
            else:
                missDateMax = wx.MessageDialog(None, "Inserire data massima", caption="Errore",
                                               style=wx.OK, pos=wx.DefaultPosition)
                if missDateMax.ShowModal() == wx.OK:
                    return
        else:
            missDateMin = wx.MessageDialog(None, "Inserire data minima", caption="Errore",
                                         style=wx.OK, pos=wx.DefaultPosition)
            if missDateMin.ShowModal() == wx.OK:
                return

    def __save_button_press(self, event):
        file = config.file
        saveFileDialog = wx.FileDialog(self, "Save", "", config.file.getFileName(), "Exel files (*.xlsx)|*.xlsx",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        file.save(saveFileDialog.GetPath())
