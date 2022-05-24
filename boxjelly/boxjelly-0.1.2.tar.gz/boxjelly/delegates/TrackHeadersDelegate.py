from PyQt5 import QtWidgets, QtCore, QtGui

from boxjelly.models.TrackListModel import TrackListModel


class TrackHeadersDelegate(QtWidgets.QStyledItemDelegate):
    
    def paint(self, painter: QtGui.QPainter, opt: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        self.initStyleOption(opt, index)
        
        rect = opt.rect
        
        painter.save()
        
        # Get the track ID and label
        id = index.data(TrackListModel.IDRole)
        label = index.data(TrackListModel.LabelRole)
        
        # Draw the highlight if the track is selected
        if opt.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, opt.palette.highlight())
            
        # Define padded contents rect
        contents = rect.adjusted(5, 0, -5, 0)
        
        # Draw the track ID
        painter.setPen(QtGui.QPen(opt.palette.color(QtGui.QPalette.Text)))
        painter.drawText(contents, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, str(id))
        
        # Draw the track label
        painter.drawText(contents, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, label)
        
        painter.restore()
    
    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        return QtCore.QSize(100, 30)