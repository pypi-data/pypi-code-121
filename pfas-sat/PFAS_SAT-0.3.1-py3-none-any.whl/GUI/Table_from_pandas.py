# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 21:40:11 2020

@author: msardar2
"""
from PySide2 import QtGui, QtCore


def f_n(x):
    """
    format number function
    If the input is string, it returns string but if the input in number, it will return it in sceintific format.
    """
    if (isinstance(x, float) or isinstance(x, int)) and len(str(x)) > 6:
        return("{:.4e}".format(x))
    else:
        return(str(x))


# Table: View Pandas Data Frame
class Table_from_pandas(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return f_n(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self._data.columns[col])
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[col]

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        """sort table by given column number column"""
        if order == QtCore.Qt.AscendingOrder:
            self._data = self._data.sort_values(self._data.columns[col], ascending=True)
        elif order == QtCore.Qt.DescendingOrder:
            self._data = self._data.sort_values(self._data.columns[col], ascending=False)
        """
        If the structure of the underlying data changes, the model can emit layoutChanged() to
        indicate to any attached views that they should redisplay any items shown, taking the
        new structure into account.
        """
        self.layoutChanged.emit()


# Table: View and edit Pandas Data Frame
class Table_from_pandas_editable(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None, pop_up=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.pop_up = pop_up
        self._data = data
        self._ColDict = {}
        for i, j in enumerate(self._data.columns):
            self._ColDict[i] = j

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return f_n(self._data.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[col]

    def format_value(self, x):
        try:
            return float(x)
        except Exception:
            return str(x)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            try:
                if self._ColDict[index.column()] in ['amount', 'loc', 'scale', 'shape', 'minimum', 'maximum']:
                    value = float(value)
                self._data.iloc[index.row(), index.column()] = self.format_value(value)
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                if self.pop_up:
                    self.pop_up('Update Data Warning!', e.__str__(), 'Warning')
                print(e)
                return False
        return False

    def flags(self, index):
        if self._ColDict[index.column()] in ['amount', 'uncertainty_type', 'loc',
                                             'scale', 'shape', 'minimum', 'maximum']:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        """sort table by given column number column"""
        if order == QtCore.Qt.AscendingOrder:
            self._data = self._data.sort_values(self._data.columns[col], ascending=True)
        elif order == QtCore.Qt.DescendingOrder:
            self._data = self._data.sort_values(self._data.columns[col], ascending=False)
        """
        If the structure of the underlying data changes, the model can emit layoutChanged() to
        indicate to any attached views that they should redisplay any items shown, taking the
        new structure into account.
        """
        self.layoutChanged.emit()


# TreeView
class TreeView(QtGui.QStandardItemModel):
    def __init__(self, data, pop_up=None):
        super().__init__()
        self.pop_up = pop_up
        self._data = data
        headers = ['Flows to processes', 'Fraction']
        self.setHorizontalHeaderLabels(headers)
        self.fill_model(self.invisibleRootItem())

    def fill_model(self, parent):
        self._key_dict = {}
        self._key_key_dict = {}
        self.Val_Col = []
        self.row_index = 0
        for k, v in self._data.items():
            self._key_dict[self.row_index] = k
            child = QtGui.QStandardItem(str(k))
            child.setEditable(False)
            empty_item = QtGui.QStandardItem(None)
            empty_item.setEditable(False)
            empty_item.setEnabled(False)
            parent.appendRow([child, empty_item])
            self.Val_Col.append(None)
            self.row_index += 1
            self._new_row_index = 0
            for key, val in v.items():
                self._key_key_dict[self._new_row_index] = key
                child_Child = QtGui.QStandardItem(str(key))
                child_Child.setEditable(False)
                val_item = QtGui.QStandardItem(str(val))
                val_item.setEditable(True)
                #val_item.setBackground(QtGui.QBrush(QtCore.Qt.green))
                child.appendRow([child_Child, val_item])
                self._new_row_index += 1


    def model_to_dict(self):
        d = dict()
        for i in range(self.rowCount()):
            ix = self.index(i, 0)
            self.fill_dict_from_model(ix, d)
        return d

    def fill_dict_from_model(self, parent_index, d):
        v = {}
        sum_param = 0
        for i in range(self.rowCount(parent_index)):
            ix = self.index(i, 0, parent_index)
            ixx = self.index(i, 1, parent_index)
            v[self.data(ix)] = float(self.data(ixx))
            sum_param += float(self.data(ixx))
            self.itemFromIndex(ixx).setForeground(QtGui.QBrush(QtCore.Qt.darkGreen))
        if sum_param != 1:
            for i in range(self.rowCount(parent_index)):
                ix = self.index(i, 0, parent_index)
                ixx = self.index(i, 1, parent_index)
                self.itemFromIndex(ixx).setForeground(QtGui.QBrush(QtCore.Qt.red))
        d[parent_index.data()] = v


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            try:
                value = float(value)
                if not 0 <= value <= 1:
                    raise ValueError('The parameter should be between 0 and 1!')
                self.itemFromIndex(index).setText(str(value))
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                if self.pop_up:
                    self.pop_up('Update Data Warning!', e.__str__(), 'Warning')
                print(e)
                return False
        return False