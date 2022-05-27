import copy

from PyQt5 import QtCore
from PyQt5.QtCore import (
    QItemSelection,
    pyqtSlot,
    Qt,
    QItemSelectionModel,
    QAbstractTableModel,
)
from PyQt5.QtWidgets import QWidget

from kamzik3.constants import *
from kamzik3.gui.templates.modelTableTemplate import Ui_Form

# Here a new class attribute CopyRole is created, and mypy complains
Qt.CopyRole = Qt.UserRole + 1  # type: ignore


class ModelTableModel(QAbstractTableModel):
    def __init__(self, model_data, empty_row, parent=None):
        assert ROWS in model_data
        assert COLUMNS in model_data
        self.model_data = model_data
        self.empty_row = empty_row
        QAbstractTableModel.__init__(self, parent)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.model_data[COLUMNS])

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.model_data[ROWS])

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            return self.model_data[COLUMNS][p_int]
        elif role == Qt.DisplayRole and Qt_Orientation == Qt.Vertical:
            return p_int + 1

    def data(self, index, role):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self.model_data[ROWS][index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.model_data[ROWS][index.row()][index.column()] = value
        elif role == Qt.CopyRole:
            self.model_data[ROWS][index] = copy.deepcopy(self.model_data[ROWS][value])
            index = self.index(index, 0)
        self.dataChanged.emit(index, index, [role])
        return True

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self.model_data[ROWS].insert(row + i, copy.deepcopy(self.empty_row))
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            del self.model_data[ROWS][row + i]
        self.endRemoveRows()
        return True

    def moveRows(
        self, sourceParent, sourceRow, count, destinationParent, destinationChild
    ):
        self.beginMoveRows(
            sourceParent,
            sourceRow,
            sourceRow + count - 1,
            destinationParent,
            destinationChild,
        )
        for i in range(count):
            self.model_data[ROWS].insert(
                destinationChild + i, self.model_data[ROWS].pop(sourceRow + i)
            )
        self.endMoveRows()
        return True

    def setHeaderData(self, section, orientation, data, role):
        if role == Qt.EditRole and orientation == Qt.Horizontal:
            self.model_data[COLUMNS][section] = data
        self.headerDataChanged.emit(orientation, section, section)

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
        )

    def get_neighbour_steps(self, ref_profile_index, ref_profile_step_index):
        return None, None


class ModelTable(QWidget, Ui_Form):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

    def setupUi(self, Form):
        super().setupUi(Form)
        self.slot_selection_changed(QItemSelection(), QItemSelection())

    def set_model(self, model):
        assert isinstance(model, ModelTableModel)
        self.input_table_view.setModel(model)
        self.input_table_view.selectionModel().selectionChanged.disconnect()
        self.input_table_view.selectionModel().selectionChanged.connect(
            self.slot_selection_changed
        )

    def get_model(self):
        return self.input_table_view.model()

    @pyqtSlot(QItemSelection, QItemSelection)
    def slot_selection_changed(self, selected, deselected):
        selected = selected.indexes()
        for w in (
            self.button_copy_item,
            self.button_move_item_top,
            self.button_move_item_up,
            self.button_remove_item,
            self.button_move_item_down,
            self.button_move_item_bottom,
        ):
            w.setDisabled(len(selected) == 0)
        if len(selected) == 0:
            return

        if selected[-1].row() == self.input_table_view.model().rowCount() - 1:
            for w in (self.button_move_item_down, self.button_move_item_bottom):
                w.setDisabled(True)
        if selected[-1].row() == 0:
            for w in (self.button_move_item_up, self.button_move_item_top):
                w.setDisabled(True)

    @pyqtSlot()
    def slot_add_item(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = 0 if len(selection) == 0 else selection[-1].row() + 1
        data_model = self.input_table_view.model()
        data_model.insertRow(row)
        self._select_item_row(row)
        return row

    @pyqtSlot()
    def slot_copy_item(self):
        new_row = self.slot_add_item()
        model = self.get_model()
        model.setData(new_row, new_row - 1, Qt.CopyRole)

    @pyqtSlot()
    def slot_remove_item(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = selection[-1].row()
        data_model = self.input_table_view.model()
        data_model.removeRow(row)

        # Select first column of added row
        row_count = self.input_table_view.model().rowCount()
        if row_count <= row:
            row = row_count - 1
        self._select_item_row(row)
        return row

    @pyqtSlot()
    def slot_move_item_top(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = selection[-1].row()
        data_model = self.input_table_view.model()
        data_model.moveRow(
            selection[-1], row, self.input_table_view.model().index(0, 0), 0
        )
        self._select_item_row(0)
        return 0

    @pyqtSlot()
    def slot_move_item_up(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = selection[-1].row()
        data_model = self.input_table_view.model()
        data_model.moveRow(
            selection[-1], row, self.input_table_view.model().index(row - 1, 0), row - 1
        )
        self._select_item_row(row - 1)
        return row - 1

    @pyqtSlot()
    def slot_move_item_down(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = selection[-1].row()
        data_model = self.input_table_view.model()
        data_model.moveRow(
            selection[-1], row, self.input_table_view.model().index(row + 1, 0), row + 1
        )
        self._select_item_row(row + 1)
        return row + 1

    @pyqtSlot()
    def slot_move_item_bottom(self):
        selection = self.input_table_view.selectionModel().selectedIndexes()
        row = selection[-1].row()
        data_model = self.input_table_view.model()
        row_count = data_model.rowCount()
        data_model.moveRow(
            selection[-1],
            row,
            self.input_table_view.model().index(row_count, 0),
            row_count,
        )
        self._select_item_row(row_count - 1)
        return row_count - 1

    def _select_item_row(self, row):
        selection = self.input_table_view.model().index(row, 0)
        self.input_table_view.selectionModel().clearSelection()
        self.input_table_view.selectionModel().setCurrentIndex(
            selection, QItemSelectionModel.Select
        )
        self.input_table_view.setFocus()

    def hideEvent(self, event):
        self.input_table_view.clearSelection()
        self.slot_selection_changed(QItemSelection(), QItemSelection())
