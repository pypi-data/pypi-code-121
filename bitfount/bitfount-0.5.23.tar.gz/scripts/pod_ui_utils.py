"""Main Components for our pod runner UI."""
import logging
import sys
from typing import Any

# Only installed on some platforms
import wx
import wxasync

from bitfount.__version__ import __version__
from bitfount.runners.pod_runner import setup_pod_from_config_file

logger = logging.getLogger("bitfount")


class WxTextCtrlHandler(logging.Handler):
    """Loging handler for showing logs in the UI."""

    def __init__(self, ctrl: Any):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record: logging.LogRecord) -> None:
        """Emits and formats a record."""
        s = self.format(record) + "\n"
        wx.CallAfter(self.ctrl.WriteText, s)


class Frame(wx.Frame):
    """Main Class for the pod runner UI."""

    def __init__(self) -> None:
        TITLE = "Bitfount Pod Runner"
        wx.Frame.__init__(self, None, wx.ID_ANY, TITLE, size=(500, 400))

        # Create the panel.
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Create the text box that will host the logs.
        log = wx.TextCtrl(
            self.panel,
            wx.ID_ANY,
            size=(200, 2000),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )

        # Create linebreaks (used for styling purposes only).
        linebreak = wx.StaticText(self.panel, label="")
        linebreak2 = wx.StaticText(self.panel, label="")

        # Create the button for the FileOpen Dialog box.
        self.load_btn = wx.Button(
            self.panel, wx.ID_ANY, "Select pod configuration file"
        )
        # Placeholder for user-provided filename.
        self.NewText = wx.StaticText(self.panel, label="")
        self.NewText.Hide()

        # Create `Start pod` and `Exit` buttons.
        self.start_btn = wx.Button(self.panel, wx.ID_ANY, "Start pod", size=(120, 20))
        self.stop_btn = wx.Button(self.panel, wx.ID_ANY, "Exit", size=(120, 20))

        # Disable `Start pod` until user specifies a file.
        self.start_btn.Disable()

        # Bind the created buttons to event functions.
        wxasync.AsyncBind(wx.EVT_BUTTON, self.onStartButton, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.onLoadButton, self.load_btn)
        self.Bind(wx.EVT_BUTTON, self.onStopButton, self.stop_btn)

        # Create the main sizer panel that will host everything.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create the sizer for the file chooser and filename.
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        file_sizer.Add(linebreak, 0, wx.ALL | wx.CENTER, 5)
        file_sizer.Add(self.load_btn, 0, wx.ALL | wx.CENTER, 5)
        file_sizer.Add(self.NewText, flag=wx.CENTER, border=5)
        file_sizer.Add(linebreak2, 0, wx.ALL | wx.CENTER, 5)

        # Create the sizer for the buttons.
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_sizer.Add(self.start_btn, 0, wx.ALL | wx.LEFT, 5)
        self.btn_sizer.Add(self.stop_btn, 0, wx.ALL | wx.RIGHT, 5)

        # Add the sizers and the log text box to our main sizer.
        self.main_sizer.Add(file_sizer, 0, wx.ALL | wx.CENTER)
        self.main_sizer.Add(self.btn_sizer, 0, wx.ALL | wx.CENTER)
        self.main_sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(self.main_sizer)

        # Add the new log handler to our logger.
        handler = WxTextCtrlHandler(log)
        logger.addHandler(handler)

        # Log the running bitfount version.
        logger.log(logging.INFO, f"Running Bitfount version {__version__}")
        FORMAT = "%(asctime)s %(levelname)s %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT))

        logger.setLevel(logging.INFO)

    def onLoadButton(self, event: Any) -> None:
        """Event config for the load file button."""
        cfgFrame = wx.Frame(None, -1)
        dlg = wx.FileDialog(
            cfgFrame,
            "Choose Pod config file.",
            "",
            "",
            "YAML Files (*.yaml; *.yml)|*.yaml; *.yml",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )

        # Check that the user did not cancel the file selection.
        if dlg.ShowModal() != wx.ID_CANCEL:
            # Get filename path and display it.
            self.filename = dlg.GetPath()
            self.NewText.SetLabel(self.filename)
            self.NewText.Show()
            # Refresh and update the text field.
            self.NewText.Refresh()
            self.NewText.Update()
            # Update layout.
            self.main_sizer.Layout()
            # Enable `Start pod` button once a file is chosen.
            self.start_btn.Enable()
            self.panel.Refresh()
            self.panel.Update()

    async def onStartButton(self, event: Any) -> None:
        """Event config for the `Start pod` button."""
        # Disable the button once it is pressed.
        self.start_btn.Disable()
        # Run pod and send logs.
        try:
            pod = setup_pod_from_config_file(self.filename)
            # Change the label for the `Exit` button once pod starts.
            self.stop_btn.SetLabel("Stop pod and exit")
            self.btn_sizer.Layout()
            await pod.start_async()

        except Exception as e:
            # Catch Exceptions and log them.
            logger.log(logging.ERROR, e)

    def onStopButton(self, event: Any) -> None:
        """Event config for the `Start pod` button.

        This button will just stop pod (if any pod is running) and exit the app.
        """
        # TODO: [BIT-299] Add pod shutdown signal here.
        sys.exit(0)
