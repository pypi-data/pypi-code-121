from PyQt5 import QtCore, QtMultimedia, QtWidgets, QtGui

import boxjelly.lib.resources
from boxjelly.commands.TrackListCommand import BatchRenameTracksCommand, DeleteTrackByIDCommand, BatchDeleteTracksByIDCommand, BatchRenameTracksCommand, SplitTrackCommand, MergeTracksCommand
from boxjelly.lib.constants import APP_NAME
from boxjelly.models.TrackListModel import TrackListModel
from boxjelly.ui.OpenDialog import OpenDialog
from boxjelly.ui.settings.SettingsDialog import SettingsDialog
from boxjelly.ui.track.TrackPanel import TrackPanel
from boxjelly.ui.video.CthulhuVideoController import CthulhuVideoController

class MainWindow(QtWidgets.QMainWindow):
    """Application main window"""
    
    mediaLoaded = QtCore.pyqtSignal(QtMultimedia.QMediaContent)
    tracksLoaded = QtCore.pyqtSignal(list)
    
    readRequested = QtCore.pyqtSignal()
    writeRequested = QtCore.pyqtSignal(list)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set window title
        self.setWindowTitle(APP_NAME)
        
        # Set window icon
        self.setWindowIcon(QtGui.QIcon(':/icons/boxjelly_logo.svg'))
        
        # Create media
        self._media = None
        
        # Create track list model
        self._track_model = TrackListModel(self)
        
        # Create selection model
        self._selection_model = QtCore.QItemSelectionModel(self._track_model)
        
        # Create undo stack
        self._undo_stack = QtWidgets.QUndoStack(self)
        
        # Create the menu bar
        self._create_menu_bar()
        
        # Create the track panel and set it as the main widget
        self._track_panel = TrackPanel(self, self._track_model, self._selection_model)
        self.setCentralWidget(self._track_panel)
        
        # Create the Cthulhu video controller
        self._video_controller = CthulhuVideoController(self, self._track_model, self._selection_model)
        
        # Create the settings dialog
        self._settings_dialog = SettingsDialog(self)
        
        # Media content and track IO
        self._media_content = None
        self._track_io = None
        
        # Create the background worker thread
        self._worker_thread = QtCore.QThread()
        self._worker_thread.start()
        
        # Connect signals
        self.mediaLoaded.connect(self._video_controller.set_media)
        self._track_panel.frameSelected.connect(self._video_controller.set_frame)
        self._video_controller.frameUpdated.connect(self._track_panel.show_frame)
        self._selection_model.selectionChanged.connect(self._on_selection_changed)
    
    @QtCore.pyqtSlot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _on_selection_changed(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        # Select
        for model_index in selected.indexes():
            self._track_model.select_track(model_index.row())
        
        # Deselect
        for model_index in deselected.indexes():
            self._track_model.deselect_track(model_index.row())

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction('&Open', self.open, QtGui.QKeySequence.Open)
        file_menu.addAction('&Save', self.save, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        file_menu.addAction('Save &As', self.save_as, QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_S)
        file_menu.addSeparator()
        file_menu.addAction('Se&ttings', self.open_settings, QtCore.Qt.CTRL + QtCore.Qt.Key_Comma)
        file_menu.addSeparator()
        file_menu.addAction('&Quit', self.close, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        # Edit menu
        edit_menu = menu_bar.addMenu('&Edit')
        edit_menu.addAction('Re&name', self.rename_selected_tracks, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        edit_menu.addAction('&Split', self.split_selected_track, QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        edit_menu.addAction('&Merge', self.merge_selected_tracks, QtCore.Qt.CTRL + QtCore.Qt.Key_M)
        edit_menu.addAction('&Delete', self.delete_selected_tracks, QtCore.Qt.Key_Delete)
        edit_menu.addSeparator()
        edit_menu.addAction('&Undo', self._undo_stack.undo, QtCore.Qt.CTRL + QtCore.Qt.Key_Z)
        edit_menu.addAction('&Redo', self._undo_stack.redo, QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_Z)
        
        # Go menu
        go_menu = menu_bar.addMenu('&Go')
        go_menu.addAction('Seek &beginning', self.seek_beginning_selected_tracks, QtCore.Qt.CTRL + QtCore.Qt.Key_BracketLeft)
        go_menu.addAction('Seek &end', self.seek_end_selected_tracks, QtCore.Qt.CTRL + QtCore.Qt.Key_BracketRight)
    
    def open_settings(self):
        """Open the settings dialog."""
        self._settings_dialog.show()
    
    def open(self):
        """Show the open dialog and load."""
        # Create and run the dialog
        open_dialog = OpenDialog(self)
        open_dialog.exec_()
        
        # If not accepted, return
        if open_dialog.result() != QtWidgets.QDialog.Accepted:
            return
        
        # Otherwise, get the media content and track IO
        self._media_content = open_dialog.media_content
        self._track_io = open_dialog.track_io
        
        # Load the media
        self.load_media(self._media_content)
        
        # Run the track IO read in the worker thread thread
        self._track_io.moveToThread(self._worker_thread)
        self._track_io.fileRead.connect(self._track_model.set_tracks)
        self._track_io.fileWritten.connect(self._on_save_finished)
        self._track_io.fileReadFailure.connect(self._on_read_failure)
        self._track_io.fileWriteFailure.connect(self._on_write_failure)
        self.readRequested.connect(self._track_io.read)
        self.writeRequested.connect(self._track_io.write)
        self.do_read()
    
    def do_read(self):
        """Read the tracks from the track IO."""
        self.readRequested.emit()
        
        # Show a progress dialog while reading
        progress = QtWidgets.QProgressDialog('Reading tracks...', None, 0, 0, self)
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        # Wait for the read to finish or fail, then close
        self._track_io.fileRead.connect(progress.close)
        self._track_io.fileReadFailure.connect(progress.close)
    
    @QtCore.pyqtSlot(str)
    def _on_read_failure(self, error_message: str):
        """Show a message box when reading fails."""
        QtWidgets.QMessageBox.critical(self, 'Error', 'Failed to read tracks: \n\n{}'.format(error_message))
    
    def do_write(self):
        """Write the tracks to the track IO."""
        self.writeRequested.emit(self._track_model.get_all_tracks())
    
    @QtCore.pyqtSlot(str)
    def _on_write_failure(self, error_message: str):
        """Show a message box when writing fails."""
        QtWidgets.QMessageBox.critical(self, 'Error', 'Failed to write tracks: \n\n{}'.format(error_message))
    
    @QtCore.pyqtSlot()
    def _on_save_finished(self):
        QtWidgets.QMessageBox.information(self, 'Saved', 'Saved successfully.')
    
    def save(self):
        # If no track IO, show an error
        if not self._track_io:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No file open.')
            return
        
        # Get confirmation
        confirm = QtWidgets.QMessageBox.question(self, 'Confirm', 'Are you sure you want to save?')
        
        # If confirmed, send the signal to save
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            self.do_write()
    
    def save_as(self):
        # If no track IO, show an error
        if not self._track_io:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No file open.')
            return
        
        # Get the new file path, requiring the same suffix as the current
        current_dir = self._track_io.path.parent
        current_suffix = self._track_io.path.suffix
        new_path_str, ok = QtWidgets.QFileDialog.getSaveFileName(self, 'Save As', str(current_dir), f'{current_suffix[1:].upper()} (*{current_suffix})')
        
        if not ok:
            return
        
        # Update the track IO target path
        self._track_io.path = new_path_str
        
        # Send the signal to save
        self.do_write()
        
    
    @QtCore.pyqtSlot(QtMultimedia.QMediaContent)
    def load_media(self, media):
        """Load the media and emit the mediaLoaded signal."""
        self._media = media
        self.mediaLoaded.emit(media)
    
    @QtCore.pyqtSlot(list)
    def load_tracks(self, tracks):
        """Load the tracks and emit the tracksLoaded signal."""
        self._track_model.set_tracks(tracks)
        self.tracksLoaded.emit(tracks)
    
    @QtCore.pyqtSlot(int)
    def delete_track(self, track_id):
        """Delete a track from the model by its ID."""
        command = DeleteTrackByIDCommand(self._track_model, track_id)
        self._undo_stack.push(command)
    
    def delete_selected_tracks(self):
        """Delete the selected tracks."""
        selected_indices = self._selection_model.selectedIndexes()
        selected_ids = [index.data(TrackListModel.IDRole) for index in selected_indices]
        
        command = BatchDeleteTracksByIDCommand(self._track_model, selected_ids)
        self._undo_stack.push(command)
    
    def rename_selected_tracks(self):
        """Change the label of a track by its ID."""
        new_label, ok = QtWidgets.QInputDialog.getText(self, 'Rename track', 'Label:')
        if not ok:
            return
        
        selected_indices = self._selection_model.selectedIndexes()
        selected_ids = [index.data(TrackListModel.IDRole) for index in selected_indices]
        
        command = BatchRenameTracksCommand(self._track_model, selected_ids, new_label)
        self._undo_stack.push(command)
        
    def split_selected_track(self):
        """Split a track at the current frame."""
        selected_indices = self._selection_model.selectedIndexes()
        if len(selected_indices) != 1:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select a single track to split.')
            return
        
        selected_id = selected_indices[0].data(TrackListModel.IDRole)
        selected_start_frame = selected_indices[0].data(TrackListModel.StartFrameRole)
        
        split_idx = self._video_controller.get_frame_number() - selected_start_frame
        
        if not 1 <= split_idx <= len(selected_indices[0].data(TrackListModel.BoxesRole)):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid split position for selected track.')
            return
        
        command = SplitTrackCommand(self._track_model, selected_id, split_idx)
        self._undo_stack.push(command)
    
    def merge_selected_tracks(self):
        """Merge the selected tracks."""
        selected_indices = self._selection_model.selectedIndexes()
        if len(selected_indices) < 2:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select at least two tracks to merge.')
            return
        
        selected_ids = [index.data(TrackListModel.IDRole) for index in selected_indices]
        
        command = MergeTracksCommand(self._track_model, selected_ids)
        self._undo_stack.push(command)
    
    def seek_beginning_selected_tracks(self):
        """Seek to the first frame of the selected tracks."""
        selected_indices = self._selection_model.selectedIndexes()
        if len(selected_indices) < 1:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select at least one track to seek to.')
            return
        
        selected_start_frames = [index.data(TrackListModel.StartFrameRole) for index in selected_indices]
        
        self._video_controller.set_frame(min(selected_start_frames))
    
    def seek_end_selected_tracks(self):
        """Seek to the last frame of the selected tracks."""
        selected_indices = self._selection_model.selectedIndexes()
        if len(selected_indices) < 1:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select at least one track to seek to.')
            return
        
        selected_end_frames = [index.data(TrackListModel.EndFrameRole) for index in selected_indices]
        
        self._video_controller.set_frame(max(selected_end_frames))
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self._worker_thread.quit()
        return super().closeEvent(a0)
