from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from .shot_list import ShotList


class CreateLayoutPackagesWidget(CustomPageWidget):

    def build(self):
        self.shot_list = ShotList(self, self.session)
        self.button_refresh = QtWidgets.QPushButton(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))), ''
        )
        self.button_refresh.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_refresh.setToolTip('Refresh list')
        self.checkbox_selectall = QtWidgets.QCheckBox('Select all')
        self.checkbox_upload = QtWidgets.QCheckBox('Upload now')
        self.button_create = QtWidgets.QPushButton('Create packages')
        
        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.shot_list, 0, 0, 1, 5)
        glo.addWidget(self.button_create, 1, 4)
        glo.addWidget(self.checkbox_selectall, 1, 1)
        glo.addWidget(self.checkbox_upload, 1, 2)
        glo.addWidget(self.button_refresh, 1, 0)
        glo.setColumnStretch(3, 10)
        glo.setSpacing(2)
        self.setLayout(glo)

        self.checkbox_selectall.stateChanged.connect(self.on_checkbox_state_changed)
        self.button_refresh.clicked.connect(self.on_refresh_button_clicked)
        self.button_create.clicked.connect(self.on_create_button_clicked)

    def get_shots_data(self, refresh_data=False):
        return self.session.cmds.Flow.call(
            self.oid, 'get_shots_data', [], dict(refresh=refresh_data)
        )
    
    def create_packages(self, shots_data, do_upload):
        self.session.cmds.Flow.call(
            self.oid, 'create_packages', [shots_data], dict(do_upload=do_upload)
        )

    def on_create_button_clicked(self):
        data = []
        for i in range(self.shot_list.topLevelItemCount()):
            item = self.shot_list.topLevelItem(i)

            if item.is_selected():
                data.append(item.to_dict())
        
        do_upload = self.checkbox_upload.checkState() == QtCore.Qt.Checked

        if data:
            self.create_packages(data, do_upload=do_upload)
            self.shot_list.refresh(refresh_data=True)
    
    def on_refresh_button_clicked(self):
        self.checkbox_selectall.setCheckState(QtCore.Qt.Unchecked)
        self.shot_list.refresh(refresh_data=True)
    
    def on_checkbox_state_changed(self, state):
        for i in range(self.shot_list.topLevelItemCount()):
            item = self.shot_list.topLevelItem(i)

            if item.status() != 'error':
                item.setCheckState(0, QtCore.Qt.CheckState(state))
    
    def _close_view(self):
        self.parentWidget().page.view.close()