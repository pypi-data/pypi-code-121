from PyQt5.QtCore import QAbstractListModel, Qt, QItemSelectionModel, QItemSelection


class LogViewHeaderModel(QAbstractListModel):
    def __init__(self, model_data):
        QAbstractListModel.__init__(self)
        self.model_data = model_data

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.model_data)

    def data(self, model_index, role=None):
        if role == Qt.DisplayRole:
            return self.model_data[model_index.row()]

    def flags(self, model_index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class LogHeaderSelectionModel(QItemSelectionModel):
    def __init__(self, model, max_selected_rows):
        QItemSelectionModel.__init__(self, model)
        self.max_selected_rows = max_selected_rows

    def select(self, selection_item, selection_flags):
        if (
            not isinstance(selection_item, QItemSelection)
            or len(selection_item.indexes()) > 1
        ):
            return
        if selection_flags & QItemSelectionModel.Select:
            selected = len(self.selectedRows(0))
            if selection_item.indexes()[0] not in self.selectedRows(0):
                selected += 1
            if selected > self.max_selected_rows:
                first_row = self.selectedRows(0)[0]
                self.select(
                    QItemSelection(first_row, first_row), QItemSelectionModel.Deselect
                )

        QItemSelectionModel.select(self, selection_item, selection_flags)
