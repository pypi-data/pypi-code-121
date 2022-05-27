import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from kamzik3.constants import *
from kamzik3.gui.general.customOpenDialog import CustomOpenDialog
from kamzik3.gui.general.loadingOverlayWidget import LoadingOverlayWidget
from kamzik3.gui.templates.logViewWindowTemplate import Ui_MainWindow
from kamzik3.snippets.snippetsWidgets import show_error_message


class LogViewWindow(QMainWindow, Ui_MainWindow):
    sig_task_update = pyqtSignal(str, str, object, object)
    sig_task_progress_update = pyqtSignal(float)

    def __init__(
        self, view_widget, cache_directory="./.cache/", virtual_directory_device=None
    ):
        self.virtual_directory_device = virtual_directory_device
        self.cache_directory = cache_directory
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/icons/log_icon_client.png"))
        self.setCentralWidget(view_widget)
        self.sig_task_update.connect(self.slot_task_update)
        self.loading_overlay = LoadingOverlayWidget(self)
        self.sig_task_progress_update.connect(self.loading_overlay.slot_set_progress)

    def load_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if self.virtual_directory_device is None:
            extension_filter = "Logfile (*.log *.log.*)"
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Choose recipe to load",
                ".",
                filter=extension_filter,
                initialFilter=extension_filter,
                options=options,
            )
            if file_path != "":
                self.slot_open_file(file_path, file_path)
        else:
            if (
                self.virtual_directory_device.get_value(ATTR_STATUS)
                in READY_DEVICE_STATUSES
            ):
                dialog = CustomOpenDialog(self.virtual_directory_device, parent=self)
                if dialog.exec():
                    (
                        requested_files,
                        metadata,
                    ) = self.virtual_directory_device.prepare_files(
                        input_files=dialog.selected_files
                    )
                    task_id = self.virtual_directory_device.sync_files(requested_files)

                    def callback(value):
                        self.sig_task_update.emit(
                            value, task_id, dialog.selected_files, metadata
                        )

                    def cancel():
                        self.virtual_directory_device.stop_task(task_id)

                    self.loading_overlay.set_over(
                        self, cancel_function=cancel, message="Syncing..."
                    )
                    self.virtual_directory_device.attach_attribute_callback(
                        [task_id, ATTR_STATUS], callback, key_filter=VALUE
                    )
                    self.virtual_directory_device.attach_attribute_callback(
                        [task_id, ATTR_PROGRESS],
                        self.sig_task_progress_update.emit,
                        key_filter=VALUE,
                    )
            else:
                show_error_message(
                    "Virtual directory device is not ready.", parent=self
                )

    def slot_task_update(self, status, task_id, original_file_names, metadata):
        if status == STATUS_BUSY:
            pass
        elif status == STATUS_IDLE:
            aborted = self.virtual_directory_device.get_value([task_id, ATTR_ABORTED])
            self.loading_overlay.hide()
            if not aborted:
                synced_files = self.virtual_directory_device.get_value(
                    [task_id, ATTR_SYNCED_FILES]
                )
                self.centralWidget().input_windowed_plots.setChecked(
                    metadata.get("windowed", True)
                )
                self.centralWidget().input_view_scale_plots.setChecked(
                    metadata.get("scaled", True)
                )
                for index, value in enumerate(synced_files.items()):
                    _, local_path = value
                    self.centralWidget().open(
                        local_path,
                        append=index != 0,
                        refresh=index == 0,
                        filter=metadata.get("filter", None),
                    )
                self.centralWidget().slot_select_rows(metadata.get("select", None))
                self.setWindowTitle(os.path.join(*original_file_names[0]))

    def slot_open_file(self, local_path, file_path):
        self.centralWidget().open(local_path, append=False, refresh=True)
        self.setWindowTitle(file_path)

    def resizeEvent(self, QResizeEvent):
        self.loading_overlay.resizeEvent(QResizeEvent)
