from PyQt5 import QtWidgets, QtGui, QtCore

from boxjelly.models.TrackListModel import TrackListModel
from boxjelly.ui.graphicsitems.TimelineTrack import TimelineTrack

class TrackGraphicsView(QtWidgets.QGraphicsView):
    
    TRACK_HEIGHT = 30
    
    frameSelected = QtCore.pyqtSignal(int)
    scaleChanged = QtCore.pyqtSignal(float, float)
    
    verticalScrollBarChanged = QtCore.pyqtSignal(int)
    horizontalScrollBarChanged = QtCore.pyqtSignal(int)
    frameScrolled = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, track_model: TrackListModel, selection_model: QtCore.QItemSelectionModel):
        super().__init__(parent)
        
        self._track_model = track_model
        self._track_model.dataChanged.connect(self._on_track_model_data_changed)
        self._track_model.modelReset.connect(self._on_track_model_reset)
        self._track_model.rowsInserted.connect(self._on_track_model_rows_inserted)
        self._track_model.rowsAboutToBeRemoved.connect(self._on_track_model_rows_about_to_be_removed)
        self._track_model.rowsRemoved.connect(self._on_track_model_rows_removed)
        self._track_model.layoutChanged.connect(self._on_track_model_layout_changed)
        
        self._selection_model = selection_model
        
        self._scene = QtWidgets.QGraphicsScene()
        self.setScene(self._scene)
        self.setViewportMargins(0, 0, 0, 0)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        
        self._background_rect = None  # backround rectangle
        self._timeline_track_dict = {}  # track ID -> TimelineTrack graphics item
        
        self._current_frame = 0  # current frame that the playhead is on
        self._frame_scale = 1.0  # horizontal scale of the timeline, in scene units per frame
        
        self.scaleChanged.connect(self._rescale)
        
        self.set_frame_scale(self._frame_scale)
        
        self.verticalScrollBar().valueChanged.connect(self.verticalScrollBarChanged.emit)
        self.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBarChanged.emit)
        self.horizontalScrollBar().valueChanged.connect(lambda value: self.frameScrolled.emit(self._map_scene_to_frame(value)))
    
    @property
    def _n_frames(self):
        if self._track_model.rowCount(None) == 0:
            return 0
    
        last_index = self._track_model.index(self._track_model.rowCount(None) - 1, 0)
        return self._track_model.data(last_index, TrackListModel.StartFrameRole) + len(self._track_model.data(last_index, TrackListModel.BoxesRole))
    
    @property
    def loaded(self):
        return self._n_frames > 0
    
    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def _on_track_model_data_changed(self, top_left: QtCore.QModelIndex, bottom_right: QtCore.QModelIndex):
        """Handle track data changes."""
        if not self.loaded:
            return
        
        for row_idx in range(top_left.row(), bottom_right.row() + 1):
            index = self._track_model.index(row_idx, 0)
            track_id = self._track_model.data(index, TrackListModel.IDRole)
            
            timeline_track = self._timeline_track_dict[track_id]
            timeline_track.update()
    
    @QtCore.pyqtSlot()
    def _on_track_model_reset(self):
        """When the track model is reset, reset the scene."""
        self._reset_scene()
    
    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def _on_track_model_rows_inserted(self, parent, start, end):
        """When tracks are added, add new timeline tracks."""
        for row_idx in range(start, end + 1):
            track = self._track_model.get_track(row_idx)
            
            timeline_track = TimelineTrack(track)
            
            timeline_track.setZValue(0)
            timeline_track.set_scale(self._frame_scale, 1.0)
            self.scaleChanged.connect(timeline_track.set_scale)
            timeline_track.clicked.connect(self._on_timeline_track_clicked)
            
            self._scene.addItem(timeline_track)
            self._timeline_track_dict[track.id] = timeline_track
    
    @QtCore.pyqtSlot(object)
    def _on_timeline_track_clicked(self, timeline_track: TimelineTrack):
        """When timeline track is clicked, select it."""
        model_index = self._track_model.index(self._track_model.index_by_id(timeline_track.track.id), 0)
        self._selection_model.select(model_index, QtCore.QItemSelectionModel.ClearAndSelect)
    
    @QtCore.pyqtSlot('QList<QPersistentModelIndex>', QtCore.QAbstractItemModel.LayoutChangeHint)
    def _on_track_model_layout_changed(self, removed_indexes, change_hint):
        """When the track model layout changes, reposition the tracks."""
        self._reposition_tracks()
    
    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def _on_track_model_rows_about_to_be_removed(self, parent, start, end):
        """When tracks are removed, remove the corresponding timeline tracks."""
        for row_idx in range(start, end + 1):
            track = self._track_model.get_track(row_idx)
            
            timeline_track = self._timeline_track_dict[track.id]
            
            self._scene.removeItem(timeline_track)
            del self._timeline_track_dict[track.id]
    
    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def _on_track_model_rows_removed(self, parent, start, end):
        self._reposition_tracks()
    
    def _center_on_frame(self, frame: int):
        self.horizontalScrollBar().setValue(self._map_frame_to_scene(frame) - self.width() / 2)
    
    def set_frame_scale(self, scale: float):
        self._frame_scale = scale
        self._center_on_frame(self._current_frame)
        self.scaleChanged.emit(scale, 1.0)
    
    def _map_scene_to_frame(self, scene_x: float) -> int:
        return int(scene_x / self._frame_scale)
    
    def _map_frame_to_scene(self, frame: int) -> float:
        return frame * self._frame_scale
    
    @property
    def scene_width(self) -> float:
        if not self.loaded:
            return 0.
        
        return self._map_frame_to_scene(self._n_frames)

    @property
    def scene_height(self):
        if not self.loaded:
            return 0.
        
        return self.TRACK_HEIGHT * len(self._track_model)
    
    @QtCore.pyqtSlot(float, float)
    def _rescale(self, new_frame_scale: float, _):
        """
        Rescale scene.
        """
        if not self.loaded:
            return
        
        self._frame_scale = new_frame_scale
        
        self._reposition_tracks()
        
        self._scene.setSceneRect(0, 0, self.scene_width, self.TRACK_HEIGHT * self._track_model.rowCount(None))  # update scene size
        
        self._background_rect.setRect(0, 0, self._scene.width(), self._scene.height())  # rescale background rect
    
    def _clear_scene(self):
        self._scene.clear()
        
        self._background_rect = None
        self._timeline_track_dict = {}
    
    def _reset_scene(self):
        self._clear_scene()
        self._add_background()
        self._reposition_tracks()
        self.set_frame_scale(self._frame_scale)
    
    def _add_background(self):
        """Add a background rectangle to the scene."""
        self._background_rect = QtWidgets.QGraphicsRectItem(0, 0, self._scene.width(), self._scene.height())
        self._background_rect.setBrush(QtGui.QColor(0, 0, 0, 0))
        self._background_rect.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self._background_rect.setZValue(-1)
        
        self._scene.addItem(self._background_rect)
    
    def _reposition_tracks(self):
        """Reposition tracks."""
        for row_idx in range(self._track_model.rowCount(None)):
            index = self._track_model.index(row_idx, 0)
            track_id = self._track_model.data(index, TrackListModel.IDRole)
            
            timeline_track = self._timeline_track_dict[track_id]
            timeline_track.setPos(timeline_track.track.start_frame * self._frame_scale, row_idx * self.TRACK_HEIGHT)
    
    def show_frame(self, frame: int):
        """Update the view to a specific frame, trying to center it in the viewport."""
        if not self.loaded:
            return
        
        self._current_frame = frame
        
        new_scrollbar_position = self._map_frame_to_scene(frame) - self.viewport().width() / 2
        if new_scrollbar_position < 0:
            new_scrollbar_position = 0
        elif new_scrollbar_position > self.scene_width - self.viewport().width():
            new_scrollbar_position = self.scene_width - self.viewport().width()
        self.horizontalScrollBar().setValue(new_scrollbar_position)
        
        self.viewport().repaint()  # Trigger a repaint of the viewport.
    
    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)
        
        if not self.loaded:
            return
        
        # Draw a red line to mark the current frame.
        painter = QtGui.QPainter(self.viewport())
        scene_x = self._map_frame_to_scene(self._current_frame)
        view_x = self.mapFromScene(scene_x, 0).x()
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
        painter.drawLine(view_x, 0, view_x, self._scene.height())
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """Handle mouse press events."""
        super().mousePressEvent(event)
        
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == QtCore.Qt.LeftButton:  # Left click
            self.frameSelected.emit(self._map_scene_to_frame(scene_pos.x()))  # Emit the frame selected signal.
    
    def wheelEvent(self, event: QtGui.QWheelEvent):
        """Handle mouse wheel events."""
        
        # If Ctrl+scroll, change the frame scale.
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.set_frame_scale(round(self._frame_scale * 1.1, 2))
            else:
                self.set_frame_scale(round(self._frame_scale / 1.1, 2))
            return
        
        # Otherwise, scroll the view.
        super().wheelEvent(event)
    