from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources

from ....resources.icons import gui as _, shotgrid as _


class ShotListItem(QtWidgets.QTreeWidgetItem):

    ICON_BY_STATUS = {
        'valid':   ('icons.gui', 'available'),
        'warning': ('icons.gui', 'warning'),
        'error':   ('icons.gui', 'error')
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

        self.setText(0, d['sg_name'])
        self.setIcon(0, self.get_icon(self.ICON_BY_STATUS[d['status']]))
        self.setIcon(1, self.get_icon(('icons.shotgrid', d['sg_status'])))

        # File statutes
        for i, name in enumerate(self.treeWidget().package_file_names()):
            path, optional = d['source_files'][name]
            icon_ref = ('icons.gui', 'found')
            
            if path is None:
                if optional:
                    icon_ref = ('icons.gui', 'not-found-gray')
                else:
                    icon_ref = ('icons.gui', 'not-found')
            
            self.setIcon(i+2, self.get_icon(icon_ref))
        
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
        labels = ['Shot', 'Status']
        labels.extend([n.title() for n in self.package_file_names()])
        return labels
    
    def refresh(self, force_update=False):
        self.clear()
        shot_ids = self.session.cmds.Flow.call(
            self.custom_widget.oid, 'shot_ids', [force_update], {}
        )
        for shot_id in shot_ids:
            ShotListItem(self, shot_id, self.custom_widget, self.session)
    
    def package_file_names(self):
        return self.session.cmds.Flow.call(
            self.custom_widget.oid, 'package_file_names', [], {}
        )

    def _on_item_changed(self, item, column):
        if column == 0 and item.status() == 'error':
            item.setCheckState(column, QtCore.Qt.Unchecked)
