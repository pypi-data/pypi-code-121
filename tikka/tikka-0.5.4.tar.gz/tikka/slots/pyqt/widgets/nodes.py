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
from typing import Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QMutex, QPoint
from PyQt5.QtGui import QKeyEvent, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.entry_point import EntryPoint
from tikka.domains.entities.events import (
    ConnectionsEvent,
    CurrencyEvent,
    EntryPointsEvent,
    NodesEvent,
)
from tikka.slots.pyqt.entities.constants import (
    ICON_NETWORK_CONNECTED,
    ICON_NETWORK_DISCONNECTED,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.models.nodes import NodesTableModel
from tikka.slots.pyqt.resources.gui.widgets.nodes_rc import Ui_NodesWidget
from tikka.slots.pyqt.widgets.node_menu import NodePopupMenu


class NodesWidget(QWidget, Ui_NodesWidget):
    """
    NodesWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init NodesWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: MainWindow instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.mutex = mutex
        self._ = self.application.translator.gettext

        self.connect_button_text_when_connected = self._("Reconnect")
        self.connect_button_text_when_disconnected = self._("Connect")

        self.init_entry_points()

        self.nodes_table_model = NodesTableModel(self.application)
        self.nodesTableView.setModel(self.nodes_table_model)
        self.nodesTableView.resizeColumnsToContents()
        self.nodesTableView.resizeRowsToContents()

        self.nodesTableView.customContextMenuRequested.connect(self.on_context_menu)

        if self.application.connections.is_connected():
            self._on_entry_point_connected()
        else:
            self._on_entry_point_disconnected()

        # events
        self.entryPointComboBox.keyPressEvent = (
            self.on_entry_point_combobox_key_press_event
        )
        self.entryPointComboBox.activated.connect(
            self.on_entry_point_combobox_index_changed
        )
        self.connectButton.clicked.connect(self._on_connect_button_clicked_event)
        self.refreshNodesButton.clicked.connect(
            self._on_refresh_nodes_button_clicked_event
        )

        # subscribe to application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self._on_currency_event
        )
        self.application.event_dispatcher.add_event_listener(
            EntryPointsEvent.EVENT_TYPE_LIST_CHANGED,
            lambda event: self.init_entry_points(),
        )
        self.application.event_dispatcher.add_event_listener(
            NodesEvent.EVENT_TYPE_LIST_CHANGED, self._on_node_list_changed_event
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_CONNECTED, self._on_entry_point_connected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_DISCONNECTED, self._on_entry_point_disconnected
        )

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.network_fetch_current_node_async_qworker = AsyncQWorker(
            self.application.entry_points.network_fetch_current_node,
            self.mutex,
        )
        self.network_fetch_current_node_async_qworker.finished.connect(
            lambda: self.refreshNodesButton.setEnabled(True)
        )

    def init_entry_points(self) -> None:
        """
        Init entry points combobox

        :return:
        """
        self.entryPointComboBox.clear()

        entry_point_urls = [
            entry_point.url for entry_point in self.application.entry_points.list()
        ]
        self.entryPointComboBox.addItems(entry_point_urls)
        # get current entry point url from domain
        current_entry_point_url = self.application.entry_points.get_current_url()
        self.entryPointComboBox.setCurrentIndex(
            entry_point_urls.index(current_entry_point_url)
        )

    def on_entry_point_combobox_key_press_event(self, event: QKeyEvent):
        """
        Triggered when enter is pressed to validate edit in entry point combobox

        :param event: QKeyEvent instance
        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:

            if self.entryPointComboBox.currentText() not in [
                self.entryPointComboBox.itemText(index)
                for index in range(0, self.entryPointComboBox.count())
            ]:
                self.application.entry_points.add(
                    EntryPoint(self.entryPointComboBox.currentText(), None)
                )

                self.application.event_dispatcher.dispatch_event(
                    EntryPointsEvent(EntryPointsEvent.EVENT_TYPE_LIST_CHANGED)
                )
        else:
            QtWidgets.QComboBox.keyPressEvent(self.entryPointComboBox, event)
            # if the key is not return, handle normally

    def on_entry_point_combobox_index_changed(self):
        """
        Triggered when entry point selection is changed

        :return:
        """
        url = self.entryPointComboBox.currentText()
        if url:
            entry_point = self.application.entry_points.get(url)
            if entry_point is None:
                # get the first one
                url = self.entryPointComboBox.itemText(0)
            self.application.entry_points.set_current_url(url)
            self.update_nodes()

    def _on_connect_button_clicked_event(self):
        """
        Triggered when user click on connect button

        :return:
        """
        if self.application.connections.is_connected():
            self.application.connections.disconnect()

        url = self.entryPointComboBox.currentText()
        if url:
            entry_point = self.application.entry_points.get(url)
            if entry_point is not None:
                self.application.connections.connect(entry_point)

    def _on_refresh_nodes_button_clicked_event(self):
        """
        Triggered when user click on refresh nodes button

        :return:
        """
        self.update_nodes()

    def update_nodes(self):
        """
        Update nodes from current entry point in table model and view

        :return:
        """
        # Disable button
        self.refreshNodesButton.setEnabled(False)
        # Start the thread
        self.network_fetch_current_node_async_qworker.start()

    def _on_currency_event(self, _):
        """
        When a currency event is triggered

        :param _: CurrencyEvent instance
        :return:
        """
        self.init_entry_points()

    def _on_node_list_changed_event(self, _):
        """
        When the node list has changed

        :param _: NodesEvent instance
        :return:
        """
        # update model
        self.nodesTableView.model().init_data()
        # resize view
        self.nodesTableView.resizeColumnsToContents()
        self.nodesTableView.resizeRowsToContents()

    def on_context_menu(self, position: QPoint):
        """
        When right button on table view

        :param position: QPoint instance
        :return:
        """
        index = self.nodesTableView.indexAt(position)
        if index.isValid():
            # get selected node
            row = index.row()
            node = self.nodes_table_model.nodes[row]
            # display popup menu at click position
            is_current_node = False
            if len(node.entry_points) > 0:
                entry_point = node.entry_points[0]
                is_current_node = (
                    entry_point.url == self.entryPointComboBox.currentText()
                )
            NodePopupMenu(self.application, node, is_current_node).exec_(
                self.nodesTableView.mapToGlobal(position)
            )

    def _on_entry_point_connected(self, _=None):
        """
        Triggered when entry point is connected

        :return:
        """
        self.connectButton.setText(self.connect_button_text_when_connected)
        self.connectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_CONNECTED))

    def _on_entry_point_disconnected(self, _=None):
        """
        Triggered when entry point is disconnected

        :return:
        """
        self.connectButton.setText(self.connect_button_text_when_disconnected)
        self.connectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_DISCONNECTED))


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(NodesWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
