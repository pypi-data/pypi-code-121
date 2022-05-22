"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import importlib
import os
from pathlib import Path
import shutil
import sys
from typing import Optional

from PyQt5 import QtWidgets

import pyjamas.pjscore as pjscore
from pyjamas.rcallbacks.rcallback import RCallback


class RCBPlugins(RCallback):
    def cbLoadPlugins(self) -> True:
        """
        Load plugins into the plugins menu. Searches for plugins under pjs.plugin_path.

        :return: True.
        """
        plugin_files = list(Path(self.pjs.plugin_path).rglob("*.py"))

        for f in plugin_files:
            self.install_plugin(str(f))

        return True


    def cbInstallPlugin(self, filename: Optional[str] = None):
        """
        Install plugin: Copy plugin to the plugins folder (pjs.plugin_path) and load it into the plugins menu.

        :param filename: path and file name of the plugin to be installed; a dialog opens if the file name is empty or None.
        :return: True if the plugin was installed, False if the install was cancelled.
        """

        # Get file name.
        if filename is None or filename is False or filename == '': # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Install plugin ...', self.pjs.cwd,
                                                          filter='PyJAMAS plugin (*' + pjscore.PyJAMAS.plugin_extension + ')')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
        if filename == '':
            return False

        self.install_plugin(filename)

        return True

    def install_plugin(self, plugin_path: str) -> bool:
        if not os.path.exists(plugin_path):
            return False

        path, name = os.path.split(plugin_path)
        modulename, ext = os.path.splitext(name)

        # Copy plugin to plugins folder (which should be in sys.path). Remove path from sys.path.
        dest_folder: str = os.path.join(self.pjs.plugin_path, modulename)

        if path != dest_folder:
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copyfile(plugin_path, os.path.join(dest_folder, name))

        sys.path.append(dest_folder)

        PJSPlugin = importlib.import_module(modulename)

        # If plugin classes can only be called PJSPlugin:
        plugin = PJSPlugin.PJSPlugin(self.pjs)
        # If arbitrary class names are OK, import the inspect module above and:
        #thepluginclass = inspect.getmembers(sys.modules[PJSPlugin.__name__], inspect.isclass)[0][1]
        #plugin = thepluginclass(self.pjs)

        self.pjs.plugin_list.append(plugin)

        self.pjs.addMenuItem(self.pjs.menuPlugins, plugin.name(), None, plugin.run)

        return True
