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
import sys
import uuid
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.entry_point import EntryPoint
from tikka.domains.entities.events import EntryPointsEvent
from tikka.domains.entities.node import Node


class NodePopupMenu(QMenu):
    """
    NodePopupMenu class
    """

    def __init__(
        self,
        application: Application,
        node: Node,
        is_current_node: bool,
        parent: Optional[QWidget] = None,
    ):
        """
        Init NodePopupMenu instance

        :param application: Application instance
        :param node: Node instance
        :param is_current_node: True if node is the node of the current selected entry point
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)

        self.application = application
        self.node = node
        self.is_current_node = is_current_node
        self._ = self.application.translator.gettext

        # menu actions
        copy_peer_id_to_clipboard_action = self.addAction(
            self._("Copy peer ID to clipboard")
        )
        copy_peer_id_to_clipboard_action.triggered.connect(
            self.copy_entry_points_to_clipboard
        )
        if not self.is_current_node:
            forget_node_action = self.addAction(self._("Forget entry point"))
            forget_node_action.triggered.connect(self.delete_node)

    def copy_entry_points_to_clipboard(self):
        """
        Copy peer ID to clipboard

        :return:
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.node.peer_id)

    def delete_node(self):
        """
        Delete selected node and its entry point

        :return:
        """
        entry_points = self.application.entry_points.list(
            offset=0, limit=1, node_id=self.node.id
        )
        if len(entry_points) > 0:
            entry_point = entry_points[0]
            response_button = self.confirm_delete_node(entry_point)
            if response_button == QMessageBox.Yes:
                self.application.entry_points.delete(entry_point.url)
                self.application.nodes.delete(self.node.id)
                self.application.event_dispatcher.dispatch_event(
                    EntryPointsEvent(EntryPointsEvent.EVENT_TYPE_LIST_CHANGED)
                )

    def confirm_delete_node(
        self, entry_point: EntryPoint
    ) -> QMessageBox.StandardButton:
        """
        Display confirm dialog and return response

        :param entry_point: EntryPoint instance
        :return:
        """
        # display confirm dialog and get response
        custom_question = self._("Forget entry point {}?")
        return QMessageBox.question(
            self,
            self._("Forget entry point"),
            custom_question.format(entry_point.url),
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    node_ = Node(
        uuid.uuid4(),
        "732SSfuwjB7jkt9th1zerGhphs6nknaCBCTozxUcPWPU",
        999,
        "duniter",
        "1.8.1",
    )

    menu = NodePopupMenu(application_, node_, False)
    menu.exec_()

    sys.exit(qapp.exec_())
