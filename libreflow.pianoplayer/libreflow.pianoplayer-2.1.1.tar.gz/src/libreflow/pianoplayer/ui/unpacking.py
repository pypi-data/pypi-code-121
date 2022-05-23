from kabaret.app.ui.gui.widgets.flow.flow_view import CustomPageWidget, QtWidgets, QtCore, QtGui
from kabaret.app import resources

from ..resources.icons import gui as _


class FileMatchItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, custom_widget, package_item, shot_id, package_id, file_id):
        super(FileMatchItem, self).__init__(package_item)
        self._custom_widget = custom_widget
        self._shot_id = shot_id
        self._package_id = package_id
        self._id = file_id
        
        self._file = None
        self._refresh()
    
    def _refresh(self):
        self._file = self._custom_widget.get_match(
            self._shot_id,
            self._package_id,
            self._id
        )
        f = self._file
        
        self.setText(0, f['file_label'])

        if f['undefined']:
            icon = QtGui.QIcon(resources.get_icon(
                ('icons.gui', 'warning')
            ))
            self.setIcon(1, icon)
        else:
            self.setIcon(1, QtGui.QIcon())

            if f['to_ignore']:
                self.setText(1, '-')
            else:
                target_text = '%s/%s' % (f['department'], f['name'])
                if f['relpath'] is not None:
                    target_text += '/' + f['relpath']
                
                self.setText(1, target_text)
        
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        self._paint()
    
    def update(self):
        self._custom_widget.update_target(
            self._shot_id,
            self._package_id,
            self._id,
            self.text(1)
        )
        self._refresh()
        self.parent().update()
    
    def current_target(self):
        target = self._custom_widget.get_target(self.text(1))
        return target
    
    def _paint(self):
        if self.to_ignore():
            color = QtGui.QColor(80, 80, 80)
        else:
            color = QtGui.QColor(185, 194, 200)
        
        for i in range(self.treeWidget().header().count()):
            self.setForeground(i, QtGui.QBrush(color))

    # def valid(self):
    #     return not self._file['undefined']
    
    def to_ignore(self):
        return self._file['to_ignore']
    
    def to_dict(self):
        department = name = relpath = None
        target = self.current_target()

        if target is not None:
            department, name, relpath = target
        
        f = self._file
        f.update({
            'name': name,
            'department': department,
            'relpath': relpath
        })

        return f


class PackageItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, custom_widget, shot_item, shot_id, package_id):
        super(PackageItem, self).__init__(shot_item)
        self._custom_widget = custom_widget
        self._package = None
        self._shot_id = shot_id
        self._id = package_id
        
        self._package = None
        self._refresh()
    
    def update(self):
        self.parent().update()
    
    def _refresh(self):
        self._package = self._custom_widget.get_package(self._shot_id, self._id)
        p = self._package

        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setText(0, f'{p["department"]}/{p["name"]} {p["revision"]}')
        self.setIcon(0, QtGui.QIcon(resources.get_icon(
            ('icons.gui', 'package')
        )))

        for match_id, _ in enumerate(p['matches']):
            FileMatchItem(
                self._custom_widget, self,
                self._shot_id,
                self._id,
                match_id
            )
        
        self.setExpanded(not self.is_valid())
    
        self._paint()
    
    def _paint(self):
        for i in range(self.treeWidget().header().count()):
            self.setBackgroundColor(i, QtGui.QColor(60, 60, 60))
    
    def is_valid(self):
        return self._custom_widget.package_is_valid(
            self._shot_id, self._id
        )
    
    def to_dict(self):
        d = self._package

        matches = []
        
        for i in range(self.childCount()):
            file_item = self.child(i)

            if not file_item.to_ignore():
                matches.append(file_item.to_dict())
        
        d.update({
            'path': self._package['path'],
            'department': self._package['department'],
            'matches': matches,
        })

        return d


class ShotItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, custom_widget, tree, shot_id):
        super(ShotItem, self).__init__(tree)
        self._custom_widget = custom_widget
        self._id = shot_id

        self._shot = None
        self._refresh()
    
    def update(self):
        if self.is_valid():
            self.setIcon(1, QtGui.QIcon())
            self.setCheckState(0, QtCore.Qt.Checked)
        else:
            icon = QtGui.QIcon(resources.get_icon(
                ('icons.gui', 'warning')
            ))
            self.setIcon(1, icon)
            self.setCheckState(0, QtCore.Qt.Unchecked)
    
    def id(self):
        return self._id
    
    def _refresh(self):
        self._shot = self._custom_widget.get_shot(self._id)
        s = self._shot

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(0, QtCore.Qt.Unchecked)
        self.setExpanded(True)
        self.setText(0, f'{s["sequence"]} {s["shot"]}')

        for pkg_id in s['packages']:
            PackageItem(self._custom_widget, self, self._id, pkg_id)
        
        self.update()
        self._paint()
    
    def _paint(self):
        for i in range(self.treeWidget().header().count()):
            self.setBackgroundColor(i, QtGui.QColor(70, 70, 70))
    
    def is_valid(self):
        return self._custom_widget.shot_is_valid(self._id)
    
    def to_dict(self):
        d = self._shot
        packages = []

        for i in range(self.childCount()):
            packages.append(self.child(i).to_dict())
        
        d.update({
            'sequence': self._shot['sequence'],
            'shot': self._shot['shot'],
            'packages': packages
        })

        return d


class PackageList(QtWidgets.QTreeWidget):

    def __init__(self, custom_widget):
        super(PackageList, self).__init__()
        self._custom_widget = custom_widget

        self.setHeaderLabels(self.get_columns())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        self.refresh()

        self.itemChanged.connect(self.on_item_changed)

        self.header().resizeSections(QtWidgets.QHeaderView.ResizeToContents)

    def get_columns(self):
        return ('Source file', 'Target')
    
    def sizeHint(self):
        return QtCore.QSize(300, 500)
    
    def refresh(self, force_update=False):
        self.blockSignals(True)
        self.clear()

        shot_ids = self._custom_widget.get_shot_ids(force_update)

        for shot_id in shot_ids:
            ShotItem(self._custom_widget, self, shot_id)
        
        self.blockSignals(False)
    
    def on_item_changed(self, item, column):
        if column == 0 and item.checkState(0) == QtCore.Qt.Checked and not item.is_valid():
            item.setCheckState(0, QtCore.Qt.Unchecked)
        elif column == 1:
            item.update()


class UnpackSourcePackagesWidget(CustomPageWidget):

    def build(self):
        self.package_list = PackageList(self)
        self.button_settings = QtWidgets.QPushButton('Settings')
        self.button_refresh = QtWidgets.QPushButton(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))), ''
        )
        self.button_refresh.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_refresh.setToolTip('Refresh list')
        self.checkbox_selectall = QtWidgets.QCheckBox('Select all')
        self.button_unpack = QtWidgets.QPushButton('Unpack')
        
        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.package_list, 0, 0, 1, 5)
        glo.addWidget(self.button_settings, 1, 0)
        glo.addWidget(self.button_refresh, 1, 1)
        glo.addWidget(self.checkbox_selectall, 1, 2)
        glo.addWidget(self.button_unpack, 1, 4)
        glo.setColumnStretch(3, 10)
        glo.setSpacing(2)
        self.setLayout(glo)

        self.checkbox_selectall.stateChanged.connect(self._on_checkbox_state_changed)
        self.button_refresh.clicked.connect(self._on_refresh_button_clicked)
        self.button_settings.clicked.connect(self._on_settings_button_clicked)
        self.button_unpack.clicked.connect(self._on_unpack_button_clicked)
    
    def get_shot_ids(self, force_update=False):
        return self.session.cmds.Flow.call(
            self.oid, 'shot_ids', [force_update], {}
        )

    def get_shot(self, shot_id):
        return self.session.cmds.Flow.call(
            self.oid, 'get_shot', [shot_id], {}
        )

    def get_package(self, shot_id, package_id):
        return self.session.cmds.Flow.call(
            self.oid, 'get_package', [shot_id, package_id], {}
        )

    def get_match(self, shot_id, package_id, match_id):
        return self.session.cmds.Flow.call(
            self.oid, 'get_match', [shot_id, package_id, match_id], {}
        )

    def update_target(self, shot_id, package_id, match_id, target_str):
        return self.session.cmds.Flow.call(
            self.oid, 'update_target', [shot_id, package_id, match_id, target_str], {}
        )

    def get_target(self, target_str):
        return self.session.cmds.Flow.call(
            self.oid, 'get_target', [target_str], {}
        )
    
    def shot_is_valid(self, shot_id):
        return self.session.cmds.Flow.call(
            self.oid, 'shot_is_valid', [shot_id], {}
        )

    def package_is_valid(self, shot_id, package_id):
        return self.session.cmds.Flow.call(
            self.oid, 'package_is_valid', [shot_id, package_id], {}
        )

    def _on_refresh_button_clicked(self):
        self.package_list.refresh(force_update=True)
    
    def _on_unpack_button_clicked(self):
        ids = []
        for i in range(self.package_list.topLevelItemCount()):
            shot_item = self.package_list.topLevelItem(i)

            if shot_item.checkState(0) == QtCore.Qt.Checked:
                ids.append(shot_item.id())
        
        self.session.cmds.Flow.call(
            self.oid, 'unpack', [ids], {}
        )

        self.package_list.refresh()
    
    def _on_settings_button_clicked(self):
        pass
    
    def _on_checkbox_state_changed(self, state):
        for i in range(self.package_list.topLevelItemCount()):
            item = self.package_list.topLevelItem(i)
            item.setCheckState(0, QtCore.Qt.CheckState(state))
