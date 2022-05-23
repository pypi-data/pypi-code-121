from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources

from libreflow.resources.icons import libreflow as _
from ...resources.icons import gui as _


class ShotListItem(QtWidgets.QTreeWidgetItem):

    ICON_BY_STATUS = {
        'needs_dl':   ('icons.gui', 'available'),
        'needs_sync': ('icons.gui', 'warning'),
        'requested': ('icons.libreflow', 'waiting'),
        'missing_files':   ('icons.gui', 'error')
    }

    def __init__(self, tree, shot_id, custom_widget, session):
        super(ShotListItem, self).__init__(tree)
        self.custom_widget = custom_widget
        self.session = session
        self.id = shot_id

        self.refresh()

    def shot_data(self):
        return self.session.cmds.Flow.call(
            self.custom_widget.oid, 'shot_data', [self.id], {}
        )
    
    def refresh(self):
        d = self.shot_data()

        self.setText(0, d['name'])
        self.setIcon(0, self.get_icon(self.ICON_BY_STATUS[d['status']]))

        # File statutes
        for i, (name, _) in enumerate(self.treeWidget().file_names_and_labels()):
            file_data = d['files'][name]
            icon_ref = ('icons.gui', 'found')
            
            if file_data['status'] == 'not_found':
                if file_data['optional']:
                    icon_ref = ('icons.gui', 'not-found-gray')
                else:
                    icon_ref = ('icons.gui', 'not-found')
            elif file_data['status'] == 'needs_sync':
                icon_ref = ('icons.libreflow', 'sync')
            elif file_data['status'] == 'requested':
                icon_ref = ('icons.libreflow', 'waiting')
            
            self.setIcon(i+1, self.get_icon(icon_ref))
        
        self.setCheckState(0, QtCore.Qt.Unchecked)

    def status(self):
        return self.shot_data()['status']
    
    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))


class ShotList(QtWidgets.QTreeWidget):
    
    def __init__(self, custom_widget, session):
        super(ShotList, self).__init__()
        self.custom_widget = custom_widget
        self.session = session

        self.setHeaderLabels(self.get_header_labels())

        self.refresh()

        self.itemChanged.connect(self._on_item_changed)
    
    def get_header_labels(self):
        labels = ['Shot']
        labels.extend([label for (_, label) in self.file_names_and_labels()])
        return labels
    
    def refresh(self, force_update=False):
        self.clear()
        shot_ids = self.session.cmds.Flow.call(
            self.custom_widget.oid, 'shot_ids', [force_update], {}
        )
        for shot_id in shot_ids:
            ShotListItem(self, shot_id, self.custom_widget, self.session)
    
    def file_names_and_labels(self):
        return self.session.cmds.Flow.call(
            self.custom_widget.oid, 'file_names_and_labels', [], {}
        )

    def _on_item_changed(self, item, column):
        if column == 0 and (item.status() == 'missing_files' or item.status() == 'requested'):
            item.setCheckState(column, QtCore.Qt.Unchecked)
        
        selected = item.checkState(0) == QtCore.Qt.Checked
        self.session.cmds.Flow.call(
            self.custom_widget.oid, 'update_selected', [item.id, selected], {}
        )
