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

import os
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5 import QtCore, QtWidgets

from pyjamas.pjscore import undo_modes
from pyjamas.rcallbacks.rcallback import RCallback


class RCBOptions(RCallback):
    def cbUndo(self) -> bool:
        """
        Undo the most recent action: individual fiducials added or deleted; polylines added, deleted or moved; or multiple fiducials or polylines added or deleted simultaneously (e.g. after finding seeds, segmenting cells, or deleting all annotations). Also, image projections, gradient, registration, crop or kymograph.

        :return: True if undo finished correctly, False if there was an error.
        """

        undoInfo = self.pjs.undo_stack.pop()
        if undoInfo is None:
            return False

        changetype = undoInfo.get("changetype")
        frame = undoInfo.get("frame")
        index = undoInfo.get("index")
        details = undoInfo.get("details")

        try:
            if changetype == undo_modes.FIDUCIAL_ADDED:
                self.pjs.fiducials[frame].pop(index)
            elif changetype == undo_modes.FIDUCIAL_DELETED:
                self.pjs.fiducials[frame].insert(index, details)
            elif changetype == undo_modes.POLYLINE_ADDED:
                self.pjs.polylines[frame].pop(index)
            elif changetype == undo_modes.POLYLINE_DELETED:
                self.pjs.polylines[frame].insert(index, details)
            elif changetype == undo_modes.POLYLINE_MOVED:
                curcoords = self.pjs.polylines[frame][index][0]
                shift = QtCore.QPointF(details.x() - curcoords.x(), details.y() - curcoords.y())
                for i in range(self.pjs.polylines[frame][index].size()):
                    self.pjs.polylines[frame][index][i] += shift
            elif changetype == undo_modes.MULTI:
                if index[0]:
                    self.pjs.fiducials[frame[0]:frame[1]] = details[0]
                if index[1]:
                    self.pjs.polylines[frame[0]:frame[1]] = details[1]
            elif changetype == undo_modes.IMAGE:
                self.pjs.io.cbLoadArray(frame)
                self.pjs.fiducials = details[0]
                self.pjs.polylines = details[1]
                self.pjs.image.cbGoTo(index)

            if changetype == undo_modes.IMAGE or changetype == undo_modes.MULTI or frame == self.pjs.curslice:
                self.pjs.repaint()

        except Exception as an_exception:
            print(an_exception)
            self.pjs.undo_stack.clear()
            self.pjs.statusbar.showMessage("Something went wrong with the undo function. Undo stack cleared.")

            return False

        return True

    def cbSetBrushSize(self, sz: int=None) -> bool:
        """
        Set the size of the brush used to paint polygons.

        :param sz: brush size; if the value is None a dialog appears.
        :return: True if the brush size was changed, False otherwise.
        """

        brush_size: int = 0
        ok_flag: bool = None

        if sz not in [None, False]:
            brush_size = sz
            ok_flag = True
        else:
            # Read user input for brush size.
            brush_size, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set brush size: ', 'Enter new size: ',
                    self.pjs.brush_size, 1)


        if ok_flag and brush_size > 0:
            self.pjs.brush_size = brush_size
            self.pjs.repaint()

            return True

        else:
            return False

    def cbDisplayFiducialIDs(self) -> bool:
        """
        Toggle fiducial ids on/off.

        :return: True.
        """
        if self.pjs.display_fiducial_ids:
            self.pjs.display_fiducial_ids = False
        else:
            self.pjs.display_fiducial_ids = True

        self.pjs.repaint()

        return True

    def cbFramesPerSec(self, fps: Optional[int] = None) -> bool:
        """
        Set the number of frames per second to use when playing through the slices.

        :param fps: number of frames per second; if the value is None, a dialog appears.
        :return: True if the number of frames per second was changed, False otherwise.
        """

        thefps: int = 0
        ok_flag: bool = None

        if fps is not None and fps is not False:
            thefps = fps
            ok_flag = True
        else:
            # Read user input for fps.
            thefps, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set frames per second: ',
                                                            'Enter frames per second: ',
                                                            self.pjs.fps, 1)

        if ok_flag and thefps > 0:
            self.pjs.fps = thefps

            return True

        else:
            return False

    def cbSetCWD(self, folder_name: str = '') -> bool:
        """
        Set the current working directory.

        :param folder_name: absolute path to the current working directory; if the string is empty ('') or None, a dialog appears.
        :return: True if the directory was set (the selected directory must exist), False otherwise.
        """
        if folder_name == '' or folder_name is False or folder_name is None: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, 'Set working folder to ...', self.pjs.cwd)

        # If cancel ...
        if folder_name == '':
            return False

        if os.path.exists(folder_name):
            self.pjs.cwd = os.path.abspath(folder_name)
            self.pjs.statusbar.showMessage(f"Working folder set to {self.pjs.cwd}.")

            return True

        else:
            return False

    def cbSetMarginSize(self, margin_size: Optional[int] = None) -> bool:
        """
        Set the size of margins used for cropping.

        :param margin_size: size of margins in pixels.
        :return: True if margin size was changed, False otherwise.
        """
        themargin: int = 0
        ok_flag: bool = True

        if margin_size is None or not margin_size:
            # Read user input for margin size.
            themargin, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set margin size: ',
                                                               'Enter new size: ', self.pjs.margin_size, 0,
                                                               min(self.pjs.height, self.pjs.width))
        else:
            themargin = margin_size
            ok_flag = True

        if ok_flag and (themargin >= 0):
            self.pjs.margin_size = themargin
            return True
        else:
            return False

    def cbSetImageProcessingCropSize(self, crop_size: Optional[int] = None) -> bool:
        """
        Set the size of the image crop that will be used for expensive computational operations (e.g. balloons).

        :param crop_size: size of the cropped image.
        :return: True if crop size was changed, False otherwise.
        """
        thesize: int = 0
        ok_flag: bool = True

        if crop_size is None or not crop_size:
            # Read user input for margin size.
            thesize, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set crop size: ',
                                                             'Enter new size: ', self.pjs.balloon_crop_size * 2, 0,
                                                             min(self.pjs.height, self.pjs.width))
        else:
            thesize = crop_size
            ok_flag = True

        if ok_flag and (thesize >= 0):
            self.pjs.balloon_crop_size = int(thesize / 2)
            return True
        else:
            return False

    def cbCropTracked(self):
        """
        Toggles cropping with tracked polylines on or off.

        :return: True.
        """

        self.pjs.crop_tracked_polyline = not self.pjs.crop_tracked_polyline

        if self.pjs.crop_tracked_polyline:
            self.pjs.statusbar.showMessage('Crop tracked polyline turned ON.')
        else:
            self.pjs.statusbar.showMessage('Crop tracked polyline turned OFF.')

        return True

    def cbChangeDisplayTheme(self) -> bool:
        """
        Toggles display between light theme and dark theme.

        :return: True.
        """
        
        if self.pjs.darktheme is False:
            self.pjs.app.setStyleSheet("""
                QMainWindow{
                    background-color: #242424;
                }
                QMenuBar {
                    background-color: #242424;
                    color: white;
                }
                QMenuBar::item::selected {
                    background-color: #6e6e6e;
                    color: white;
                }
                QMenu {
                    background-color: #242424;
                    color: white;
                }
                QMenu::item::selected{
                    background-color: #6e6e6e;
                    color: white;
                }
                QWidget{
                    background: #242424;
                    color: white;
                }
                QPushButton{
                    background-color: #6e6e6e;
                }
                QPushButton:pressed{
                    background-color: #575757;
                }
                QLabel{
                    background-color: transparent;
                }
            """)
            plt.style.use('dark_background')
            mpl.rc('figure', facecolor = '#242424', edgecolor = 'white')
            mpl.rc('axes', facecolor = '#242424', edgecolor = 'white')
            self.pjs.darktheme = True

        else:
            self.pjs.app.setStyleSheet("")
            plt.style.use('default')
            mpl.rcdefaults()
            self.pjs.darktheme = False
        
        return True

    def cbCloseAllPolylines(self):
        """
        Toggles closing all polylines loaded from file ON/OFF.

        :return: True.
        """

        self.pjs.close_all_polylines = not self.pjs.close_all_polylines

        if self.pjs.close_all_polylines:
            self.pjs.statusbar.showMessage('Close all polylines turned ON.')
        else:
            self.pjs.statusbar.showMessage('Close all polylines turned OFF.')

        return True

