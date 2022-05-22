#!/usr/bin/env python3

# Git Dashboard
# Copyright (C) 2022 Jung Ko <kojung@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Git Dashboard
"""

import os
import sys
import signal
from pathlib import Path
import argparse
import time
import json

from PySide6.QtCore import (
    Signal,
    QThread,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)

from git_dashboard.groups import GroupsView
from git_dashboard.config import (
    CONFIG,
    create_default_configuration,
    load_configuration,
)

class MainWindow(QMainWindow):
    """main window"""
    def __init__(self, groups_view, refresh_thread):
        """constructor"""
        super().__init__()
        self.refresh_thread = refresh_thread

        # status and refresh button packed horizontally
        self.status = QLabel("Welcome to git-dashboard")
        self.button = QPushButton("refresh now")
        self.button.clicked.connect(self.refresh_button)  # pylint: disable=no-member
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.status, 66)
        hlayout.addWidget(self.button, 33)

        # vertical layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(groups_view)
        vlayout.addLayout(hlayout)

        # dummy container widget
        widget = QWidget()
        widget.setLayout(vlayout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        """gracefully terminate the application by stopping refresh_thread"""
        self.refresh_thread.stop = True
        while not self.refresh_thread.isFinished():
            time.sleep(1)
        event.accept()  # let the window close

    def refresh_button(self):
        """refresh button action"""
        self.refresh_thread.force = True

class RefreshThread(QThread):
    """Separate thread used to query git repos in the background"""
    ready = Signal(object)   # Signal must be class, not instance member
    tick  = Signal(object)   # Signal must be class, not instance member
    def __init__(self, config, refresh):
        """constructor"""
        super().__init__()
        self.config  = config
        self.refresh = refresh
        self.stop    = False
        self.force   = False

    def run(self):
        """thread run method"""
        while True:
            groups = load_configuration(config=self.config, initial=False)
            self.ready.emit(groups)
            # wait for `refresh` seconds, or until stop is issued
            elapsed  = 0
            self.force = False
            num_repos  = sum(map(len, groups.values()))
            while not self.stop and not self.force and elapsed < self.refresh:
                time.sleep(1)
                elapsed += 1
                self.tick.emit((elapsed, num_repos))
            if self.stop:
                break

def parser():
    """argument parser"""
    par = argparse.ArgumentParser(description="Git dashboard")
    par.add_argument("-c", "--config",  default=CONFIG,
        help=f"Configuration file. Default={CONFIG}")
    par.add_argument("--no-gui",  default=False, action='store_true',
        help="No GUI. Show repo status in JSON format and exit")
    par.add_argument("-r", "--refresh",  type=int, default=60,
        help="Refresh interval in seconds. Default=60")
    par.add_argument("-s", "--font-scale", type=float, default=1.0,
        help="Font scale. Default=1.0")
    return par

def gui_mode(args):
    """start git-dashboard in GUI mode"""
    # start the app
    app = QApplication(sys.argv)

    # model and views
    groups = load_configuration(config=args.config, initial=True)
    groups_view = GroupsView(groups, args)

    def refresh_func(groups):
        """refresh repo status"""
        for name, model in groups_view.models.items():
            model.layoutAboutToBeChanged.emit()  # pylint: disable=no-member
            model.group = groups[name]
            model.layoutChanged.emit()           # pylint: disable=no-member

    # start refresh thread and connect it refresh_func
    refresh_thread = RefreshThread(args.config, args.refresh)
    refresh_thread.ready.connect(refresh_func)
    refresh_thread.start()

    def sigint_handler(*args): # pylint: disable=unused-argument
        """Handler for the SIGINT signal."""
        refresh_thread.stop = True
        while not refresh_thread.isFinished():
            time.sleep(1)
        QApplication.quit()

    # instantiate main window
    window = MainWindow(groups_view, refresh_thread)

    # update status bar
    def tick_func(elapsed_and_num_repos):
        """update status bar"""
        elapsed, num_repos = elapsed_and_num_repos
        window.status.setText(f"Tracking {num_repos} repos. Refresh in {args.refresh - elapsed} secs...")

    refresh_thread.tick.connect(tick_func)

    # capture ctrl-c signal so we can exit gracefully
    signal.signal(signal.SIGINT, sigint_handler)

    # resize primary window to 1/5 width + 1/2 height
    screen = app.primaryScreen()
    size   = screen.size()
    window.resize(size.width()//5, size.height()//2)

    window.show()
    app.exec()

def cmdline_mode(args):
    """command line mode"""
    groups = load_configuration(config=args.config, initial=True)
    print(json.dumps(groups, indent=2))

def main():
    """main routine for test purposes"""
    args = parser().parse_args()

    # create default configuration if needed
    if not os.path.exists(args.config):
        home = Path.home()
        create_default_configuration(home, 'home', args.config)

    if args.no_gui:
        cmdline_mode(args)
    else:
        gui_mode(args)

if __name__ == "__main__":
    main()
