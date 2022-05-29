import re
import numpy as np
from enum import Flag, auto


class ClipFlags(Flag):
    Below = auto()
    Above = auto()
    Equal = auto()
    BelowAndAbove = Below | Above


class SplitFlags(Flag):
    OverlapInLoRows = auto()
    OverlapInHiRows = auto()
    OverlapInBothRows = OverlapInLoRows | OverlapInHiRows


class DataProvider:
    def __init__(self, ColumnHeader, NumpyArray: np.ndarray):
        if type(ColumnHeader) == dict:
            self.ColumnHeader = ColumnHeader
        else:
            ColCnt = len(ColumnHeader)
            self.ColumnHeader = {ColumnHeader[i]: range(ColCnt)[i] for i in range(ColCnt)}
        self.Data = NumpyArray

        self.Columns = np.size(self.Data, axis=1)
        if not self.Columns == len(ColumnHeader):
            raise ValueError("ColumnHeader-count not matching with DataColumns-count.")
        self.Rows = np.size(self.Data, axis=0)

    def ClipData(self, iColumn: int, ValueExcluded, ClipFlag: ClipFlags):
        clipCol = self.GetColumn(iColumn)
        removeIndicies = []
        for iRow in range(len(clipCol)):
            if ClipFlags.Above in ClipFlag and clipCol[iRow] > ValueExcluded:
                removeIndicies.append(iRow)
            if ClipFlags.Below in ClipFlag and clipCol[iRow] < ValueExcluded:
                removeIndicies.append(iRow)
            if ClipFlags.Equal in ClipFlag and clipCol[iRow] == ValueExcluded:
                removeIndicies.append(iRow)

        self.RemoveRows(removeIndicies)
        return

    def GetData(self):
        return self.Data

    def GetRow(self, RowIndex):
        return self.Data[RowIndex, :]

    def RemoveRows(self, RowIndicies):
        self.Data = np.delete(self.Data, RowIndicies, axis=0)
        return

    def SplitDataAtRow(self, Index: int, SplitFlag: SplitFlags = SplitFlags.OverlapInBothRows):
        cRows = len(self.GetColumn(0))
        Index = int(Index)
        # The short ifs define where the overlapping index is stored (loRows, hiRows or both!)
        loRows = self.Data[0 : Index + (1 if SplitFlags.OverlapInLoRows in SplitFlag else 0)]
        hiRows = self.Data[Index + (0 if SplitFlags.OverlapInHiRows in SplitFlag else 1) : cRows]
        return loRows, hiRows

    def __RemoveRowsFromNumpyarray__(nparray: np.ndarray, Indicies):
        return np.delete(nparray, Indicies, axis=0)

    def GetColumn(self, Column):
        if type(Column) == str:
            return self.Data[:, self.ColumnHeader[Column]]

        return self.Data[:, Column]

    def RemoveColumn(self, ColumnIndicies):
        for columnIndex in ColumnIndicies:
            for key, value in self.ColumnHeader.items():
                if value == columnIndex:
                    self.ColumnHeader.pop(key)
                    break

        self.Data = np.delete(self.Data, ColumnIndicies, axis=1)
        return
