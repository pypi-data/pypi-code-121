import wx
from . import config
from TimesheetExcelEditor.RangePanel import RangePanel
from TimesheetExcelEditor.ListPanel import ListPanel
from TimesheetExcelEditor.FormPanel import FormPanel
from TimesheetExcelEditor.CalendarPanel import CalendarPanel
from TimesheetExcelEditor.CreatePanel import CreatePanel
from TimesheetExcelEditor.Excel import Excel


class MyPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        filebox = wx.BoxSizer(wx.HORIZONTAL)
        excel = wx.StaticText(self, label="File Excel")
        filebox.Add(excel, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.fPath = wx.TextCtrl(self, style=wx.TE_READONLY)
        filebox.Add(self.fPath, proportion=1, flag=wx.ALIGN_TOP | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.loadButton = wx.Button(self, label='Scegli file')
        self.loadButton.Bind(wx.EVT_BUTTON, self.__load_button_press)
        filebox.Add(self.loadButton, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.vbox.Add(filebox, proportion=0, flag=wx.EXPAND | wx.TOP, border=5)

        activityBox = wx.BoxSizer(wx.HORIZONTAL)
        acl = wx.StaticText(self, label="Attività")
        activityBox.Add(acl, proportion=0, flag=wx.LEFT, border=15)
        config.acSelect = wx.ComboBox(self, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        activityBox.Add(config.acSelect, proportion=1, flag=wx.EXPAND | wx.LEFT, border=10)
        config.acSelect.Disable()
        ml = wx.StaticText(self, label="Moltiplicatore")
        activityBox.Add(ml, proportion=0, flag=wx.LEFT, border=10)
        config.multiplier = wx.ComboBox(self, choices=["1", "1.25", "1.5", "1.75", "2"],
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY)
        activityBox.Add(config.multiplier, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        config.multiplier.SetSelection(0)
        self.vbox.Add(activityBox, proportion=0, flag=wx.EXPAND | wx.TOP, border=10)

        tabBox = wx.BoxSizer(wx.HORIZONTAL)
        self.notebook = wx.Notebook(self)
        form = FormPanel(self.notebook)
        listTab = ListPanel(self.notebook)
        calTab = CalendarPanel(self.notebook)
        rangeTab = RangePanel(self.notebook)
        self.notebook.AddPage(form, "GIORNO")
        self.notebook.AddPage(listTab, "LISTA GIORNI")
        self.notebook.AddPage(rangeTab, "INTERVALLO")
        self.notebook.AddPage(calTab, "CALENDAR")
        self.notebook.AddPage(CreatePanel(self.notebook), "CREA")
        tabBox.Add(self.notebook, proportion=1, flag=wx.EXPAND | wx.TOP, border=5)
        self.vbox.Add(tabBox, proportion=1, flag=wx.EXPAND | wx.TOP, border=5)

        logBox = wx.BoxSizer(wx.HORIZONTAL)
        config.log = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        logBox.Add(config.log, proportion=1, flag=wx.EXPAND | wx.TOP, border=5)
        self.vbox.Add(logBox, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.vbox)

    def __load_button_press(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "", "Exel files (*.xlsx)|*.xlsx",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        directory, filename = openFileDialog.GetDirectory(), openFileDialog.GetFilename()
        config.file = Excel()
        config.file.load(directory, filename)
        self.fPath.SetValue(config.file.getPath())
        if not config.log.IsEmpty():
            config.log.Clear()
        config.log.AppendText("File "+config.file.getFileName()+" caricato.\n")
        config.formModifyButton.Enable()
        config.listModifyButton.Enable()
        config.calModifyButton.Enable()
        config.rangeModifyButton.Enable()
        lis = config.file.getHeaders()
        config.acSelect.Enable()
        for keys in lis:
            config.acSelect.Append(lis[keys])
        config.acSelect.SetSelection(0)
