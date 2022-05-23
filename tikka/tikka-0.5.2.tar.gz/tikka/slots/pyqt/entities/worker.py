# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Callable, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal


class QWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, call: Callable) -> None:
        """
        Init QWorker instance with function to call

        :param call: Function to call
        """
        super().__init__()
        self.call = call

    def run(self) -> None:
        """
        Run call function

        :return:
        """
        self.call()
        self.finished.emit()


class AsyncQWorker(QThread):
    def __init__(self, call: Callable, parent: Optional[QObject] = None) -> None:
        """
        Init QWorker instance with function to call

        :param call: Function to call
        """
        super().__init__(parent)
        self.worker = QWorker(call)
        self.worker.moveToThread(self)
        # run worker when thread is started
        self.started.connect(self.worker.run)
        # quit thread when worker is finished
        self.worker.finished.connect(self.quit)
