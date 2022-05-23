from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from .shot_list import ShotList


class CreateCleanPackagesWidget(CustomPageWidget):

    def build(self):
        self.shot_list = ShotList(self, self.session)
        
        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh')))
        self.button_refresh = QtWidgets.QPushButton(icon, '')
        self.checkbox_selectall = QtWidgets.QCheckBox('Select all')
        self.checkbox_upload = QtWidgets.QCheckBox('Upload now')
        self.button_create = QtWidgets.QPushButton('Create packages')
        
        self.button_refresh.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.button_refresh.setToolTip('Refresh shot list')
        self.button_refresh.setMaximumHeight(40)
        self.button_create.setMaximumWidth(150)
        self.button_create.setMaximumHeight(40)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.shot_list, 0, 0, 1, 5)
        glo.addWidget(self.button_refresh, 1, 0)
        glo.addWidget(self.checkbox_selectall, 1, 1)
        glo.addWidget(self.checkbox_upload, 1, 2)
        glo.addWidget(self.button_create, 1, 4)
        glo.setColumnStretch(3, 1)
        self.setLayout(glo)
    
        # Install callbacks
        self.button_refresh.clicked.connect(self._on_button_refresh_clicked)
        self.checkbox_selectall.stateChanged.connect(self._on_checkbox_selectall_state_changed)
        self.button_create.clicked.connect(self._on_button_create_clicked)

    def _on_button_refresh_clicked(self):
        self.shot_list.refresh(force_update=True)
        self.checkbox_selectall.setCheckState(QtCore.Qt.Unchecked)

    def _on_checkbox_selectall_state_changed(self, state):
        for i in range(self.shot_list.topLevelItemCount()):
            state = QtCore.Qt.CheckState(state)
            self.shot_list.topLevelItem(i).setCheckState(0, state)

    def _on_button_create_clicked(self):
        do_upload = self.checkbox_upload.checkState() == QtCore.Qt.Checked
        selected_shot_ids = []

        for i in range(self.shot_list.topLevelItemCount()):
            item = self.shot_list.topLevelItem(i)
            if item.checkState(0) == QtCore.Qt.Checked:
                selected_shot_ids.append(item.id)
        
        self.session.cmds.Flow.call(
            self.oid, 'create_shot_packages', [selected_shot_ids, do_upload], {}
        )

        self.shot_list.refresh()
