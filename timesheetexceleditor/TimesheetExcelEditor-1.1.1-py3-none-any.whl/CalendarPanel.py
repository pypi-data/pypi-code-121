import wx
import re
import validators
from icalendar import Calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.rrule as rrule
from urllib.request import Request, urlopen
from . import config


class CalendarPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        svbox = wx.BoxSizer(wx.HORIZONTAL)

        leftpanel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        linkhbox = wx.BoxSizer(wx.HORIZONTAL)
        linklabel = wx.StaticText(leftpanel, label="Link")
        linkhbox.Add(linklabel, proportion=0, flag=wx.ALIGN_LEFT | wx.RIGHT, border=10)
        self.link = wx.TextCtrl(leftpanel)
        linkhbox.Add(self.link, proportion=1, flag=wx.LEFT | wx.RIGHT, border=10)
        vbox.Add(linkhbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

        filterBox = wx.BoxSizer(wx.HORIZONTAL)
        filterLabel = wx.StaticText(leftpanel, label="Filtri")
        filterBox.Add(filterLabel, proportion=0, flag=wx.ALIGN_LEFT | wx.RIGHT, border=15)
        self.nameFilter = wx.TextCtrl(leftpanel)
        self.nameFilter.SetHint("Nome...")
        self.dataMin = wx.TextCtrl(leftpanel)
        self.dataMin.SetHint("Data Min...")
        self.dataMax = wx.TextCtrl(leftpanel)
        self.dataMax.SetHint("Data Max...")
        self.numOre = wx.TextCtrl(leftpanel)
        self.numOre.SetHint("Num ore...")
        self.numOre.Bind(wx.EVT_CHAR, self.__handle_keypress)
        filterBox.Add(self.nameFilter, proportion=1, flag=wx.LEFT | wx.RIGHT, border=4)
        filterBox.Add(self.dataMin, proportion=1, flag=wx.LEFT | wx.RIGHT, border=4)
        filterBox.Add(self.dataMax, proportion=1, flag=wx.LEFT | wx.RIGHT, border=4)
        filterBox.Add(self.numOre, proportion=1, flag=wx.LEFT | wx.RIGHT, border=5)
        vbox.Add(filterBox, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

        eventHBox = wx.BoxSizer(wx.HORIZONTAL)
        eventLabel = wx.StaticText(leftpanel, label="Eventi")
        eventHBox.Add(eventLabel, proportion=0, flag=wx.ALIGN_LEFT | wx.RIGHT, border=5)
        self.eventList = wx.ListCtrl(leftpanel, style=wx.LC_REPORT | wx.LC_HRULES)
        self.eventList.EnableCheckBoxes()
        self.eventList.InsertColumn(0, "Nome", width=150)
        self.eventList.InsertColumn(1, "Data", width=80)
        self.eventList.InsertColumn(2, "Ora", width=50)
        self.eventList.InsertColumn(3, "Numero ore", width=80)
        eventHBox.Add(self.eventList, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        vbox.Add(eventHBox, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)
        leftpanel.SetSizer(vbox, wx.EXPAND)
        svbox.Add(leftpanel, 1, wx.EXPAND)

        rightPanel = wx.Panel(self)

        buttonbox = wx.BoxSizer(wx.VERTICAL)
        self.calButton = wx.Button(rightPanel, label='Carica')
        self.calButton.Bind(wx.EVT_BUTTON, self.__load_button_press)
        buttonbox.Add(self.calButton, proportion=0, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        self.filterButton = wx.Button(rightPanel, label="Filtra")
        buttonbox.Add(self.filterButton, proportion=0, flag=wx.TOP | wx.BOTTOM, border=10)
        self.filterButton.Bind(wx.EVT_BUTTON, self.__filter_button_press)
        self.filterButton.Disable()
        config.calModifyButton = wx.Button(rightPanel, label='Modifica')
        config.calModifyButton.Bind(wx.EVT_BUTTON, self.__cal_modify_button_press)
        config.calModifyButton.Disable()
        buttonbox.Add(config.calModifyButton, proportion=0, flag=wx.TOP | wx.BOTTOM, border=10)
        self.saveButton = wx.Button(rightPanel, label="Salva")
        self.saveButton.Bind(wx.EVT_BUTTON, self.__save_button_press)
        self.saveButton.Disable()
        buttonbox.Add(self.saveButton, proportion=0, flag=wx.TOP | wx.BOTTOM, border=10)
        self.selectAll = wx.Button(rightPanel, label="Seleziona Tutti")
        self.selectAll.Bind(wx.EVT_BUTTON, self.__checkAll)
        self.selectAll.Disable()
        buttonbox.Add(self.selectAll, proportion=0, flag=wx.TOP | wx.BOTTOM, border=10)
        self.deselectall = wx.Button(rightPanel, label="Deseleziona Tutti")
        self.deselectall.Bind(wx.EVT_BUTTON, self.__uncheckAll)
        self.deselectall.Disable()
        buttonbox.Add(self.deselectall, proportion=0, flag=wx.TOP | wx.BOTTOM, border=10)

        rightPanel.SetSizer(buttonbox, wx.EXPAND)
        svbox.Add(rightPanel, 0, wx.EXPAND)

        self.SetSizer(svbox)

    def __handle_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isnumeric() or keycode == 8:
                # Valid numeric character
                event.Skip()

    def __load_button_press(self, event):
        if self.link.IsEmpty() is not True and validators.url(self.link.GetValue()):
            url = self.link.GetValue()
            req = Request(url)
            response = urlopen(req)
            data = response.read()
            self.cal = Calendar.from_ical(data)
            index = 0
            key_events = {}
            if not self.eventList.IsEmpty():
                self.eventList.DeleteAllItems()
            for event in self.cal.walk('vevent'):
                if event.get('rrule') is not None:
                    evName = str(event.get('summary'))
                    start_date = event.get('dtstart').dt.strftime("%d/%m/%Y")
                    start_hour = event.get('dtstart').dt.strftime("%H:%M")
                    delta = relativedelta(event.get('dtend').dt, event.get('dtstart').dt)
                    key_events[event.get('dtstart').dt] = (evName, start_date, start_hour, str(delta.hours))
                    reoccur = event.get('rrule').to_ical().decode('utf-8')
                    startR = None
                    nTimes = int(re.search("\d+", reoccur).group())
                    for i in range(0, nTimes - 1):
                        rule = rrule.rrulestr(reoccur, dtstart=event.get('dtstart').dt)
                        if i == 0:
                            startR = rule.after(event.get('dtstart').dt)
                        else:
                            startR = rule.after(startR)

                        start_date = startR.strftime("%d/%m/%Y")
                        start_hour = startR.strftime("%H:%M")
                        key_events[startR] = (evName, start_date, start_hour, str(delta.hours))
                else:
                    evName = str(event.get('summary'))
                    start_date = event.get('dtstart').dt.strftime("%d/%m/%Y")
                    start_hour = event.get('dtstart').dt.strftime("%H:%M")
                    delta = relativedelta(event.get('dtend').dt, event.get('dtstart').dt)
                    key_events[event.get('dtstart').dt] = (evName, start_date, start_hour, str(delta.hours))
            for i in sorted(key_events):
                for j in range(len(key_events[i])):
                    if j == 0:
                        self.eventList.InsertItem(index, key_events[i][j])
                    if j == 1:
                        self.eventList.SetItem(index, 1, key_events[i][j])
                    if j == 2:
                        self.eventList.SetItem(index, 2, key_events[i][j])
                    if j == 3:
                        self.eventList.SetItem(index, 3, key_events[i][j])
                index += 1
            config.log.AppendText("Calendar caricato.\n")
            self.filterButton.Enable()
            self.selectAll.Enable()
            self.deselectall.Enable()
        else:
            missLink = wx.MessageDialog(None, "Link calendar assente/errato", caption="Errore",
                                        style=wx.OK, pos=wx.DefaultPosition)
            if missLink.ShowModal() == wx.OK:
                return

    def __checkAll(self, event):
        for i in range(self.eventList.GetItemCount()):
            if not self.eventList.IsItemChecked(i):
                self.eventList.CheckItem(i)

    def __uncheckAll(self, event):
        for i in range(self.eventList.GetItemCount()):
            if self.eventList.IsItemChecked(i):
                self.eventList.CheckItem(i, False)

    def __filter_button_press(self, event):
        if not self.eventList.IsEmpty():
            itemsNum = self.eventList.GetItemCount() - 1
            name = dateMin = dateMax = hours = None
            if not self.nameFilter.IsEmpty():
                name = self.nameFilter.GetValue()
            if not self.numOre.IsEmpty() and self.numOre.GetValue().isnumeric():
                hours = self.numOre.GetValue()
            if not self.dataMin.IsEmpty() and config.checkDate(self.dataMin.GetValue()):
                dateMin = datetime.strptime(self.dataMin.GetValue(), "%d/%m/%Y")
            if not self.dataMax.IsEmpty() and config.checkDate(self.dataMax.GetValue()):
                dateMax = datetime.strptime(self.dataMax.GetValue(), "%d/%m/%Y")
            while itemsNum >= 0:
                eliminate = False
                if name is not None:
                    if re.search(name, self.eventList.GetItemText(itemsNum, 0), re.IGNORECASE) is None:
                        eliminate = True
                if dateMin is not None:
                    listDate = datetime.strptime(self.eventList.GetItemText(itemsNum, 1), "%d/%m/%Y")
                    if listDate < dateMin:
                        eliminate = True
                if dateMax is not None:
                    listDate = datetime.strptime(self.eventList.GetItemText(itemsNum, 1), "%d/%m/%Y")
                    if listDate > dateMax:
                        eliminate = True
                if hours is not None:
                    if self.eventList.GetItemText(itemsNum, 3) != hours:
                        eliminate = True
                if eliminate:
                    self.eventList.DeleteItem(itemsNum)
                itemsNum -= 1
        else:
            missCal = wx.MessageDialog(None, "Caricare calendar", caption="Errore",
                                       style=wx.OK, pos=wx.DefaultPosition)
            if missCal.ShowModal() == wx.OK:
                return

    def __cal_modify_button_press(self, event):
        activity = config.acSelect.GetStringSelection()
        multiplier = config.multiplier.GetStringSelection()
        if not self.eventList.IsEmpty():
            checked = False
            for i in range(self.eventList.GetItemCount()):
                if self.eventList.IsItemChecked(i):
                    checked = True
                    break
            if checked:
                for i in range(self.eventList.GetItemCount()):
                    if self.eventList.IsItemChecked(i):
                        date = self.eventList.GetItemText(i, 1)
                        hours = self.eventList.GetItemText(i, 3)
                        config.file.modify(activity, date, int(hours), float(multiplier))
                modified = wx.MessageDialog(None, "File modificato", caption="Info",
                                            style=wx.OK, pos=wx.DefaultPosition)
                if modified.ShowModal() == wx.OK:
                    return
                if config.file.checkMissing():
                    message = config.file.getMissing()
                    config.log.AppendText(message + "\n")
                self.saveButton.Enable()
            else:
                missCal = wx.MessageDialog(None, "Selezionare 1 o più eventi", caption="Errore",
                                           style=wx.OK, pos=wx.DefaultPosition)
                if missCal.ShowModal() == wx.OK:
                    return
        else:
            missCal = wx.MessageDialog(None, "Caricare calendar", caption="Errore",
                                       style=wx.OK, pos=wx.DefaultPosition)
            if missCal.ShowModal() == wx.OK:
                return

    def __save_button_press(self, event):
        file = config.file
        saveFileDialog = wx.FileDialog(self, "Save", "", config.file.getFileName(), "Exel files (*.xlsx)|*.xlsx",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        file.save(saveFileDialog.GetPath())
