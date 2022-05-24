import logging
from typing import Iterable, List, Set
from uuid import UUID, uuid4
from intervaltree.interval import Interval
from intervaltree.intervaltree import IntervalTree

from PyQt5 import QtCore
from sharktopoda_client.localization.LocalizationController import LocalizationController
from sharktopoda_client.localization.Localization import Localization
from sharktopoda_client.localization.IO import IO as LocalizationIO
from boxjelly.lib.settings import SettingsManager

from boxjelly.lib.track import IdentifiedTrack


class TrackListModel(QtCore.QAbstractListModel):
    """
    Track list model. Wraps a list of identified tracks and synchronizes with a Sharktopoda client LocalizationController.
    """
    
    IDRole = QtCore.Qt.UserRole + 1  # Integer ID (e.g. 42)
    LabelRole = QtCore.Qt.UserRole + 2  # String label (e.g. "fish")
    StartFrameRole = QtCore.Qt.UserRole + 3  # Integer start frame (e.g. 12345)
    BoxesRole = QtCore.Qt.UserRole + 4  # List of track's boxes (None indicates no box at that frame)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self._tracks: List[IdentifiedTrack] = []  # Root list of IdentifiedTracks
        
        # IntervalTree for quick lookup of tracks by frame
        self._track_id_interval_dict = {}
        self._track_tree = IntervalTree()
        
        # Sharktopoda client LocalizationController for adding/removing localizations
        self._track_id_localization_list_dict = {}
        self._localization_controller = LocalizationController()
        self._localization_controller.log.setLevel(logging.INFO)
        
        # Get the app settings manager, connect signals from setting proxies
        self._settings = SettingsManager.get_instance()
        self._settings.incoming_port.valueChanged.connect(self._refresh_localization_io)
        self._settings.incoming_topic.valueChanged.connect(self._refresh_localization_io)
        self._settings.outgoing_port.valueChanged.connect(self._refresh_localization_io)
        self._settings.outgoing_topic.valueChanged.connect(self._refresh_localization_io)
        
        # Create the localization IO
        self._localization_io = None
        self._selection_controller = None
        self._refresh_localization_io()
        
        # Video info (TODO: find this a new home)
        self._video_reference_uuid = None
        self._frame_rate = None
        self._settings.frame_rate.valueChanged.connect(self.set_frame_rate)
        
        # Set of track IDs that have been loaded into the LocalizationController
        self._loaded_ids = set()  # Set of track IDs that are currently loaded in Cthulhu
    
    @QtCore.pyqtSlot()
    def _refresh_localization_io(self):
        """
        Refresh the LocalizationIO.
        """
        # Close the current IO
        old_io = self._localization_io
        if old_io is not None:
            old_io.ok = False
            old_io.context.destroy()
        
        # Create a new IO from the current settings
        new_io = LocalizationIO(
            self._settings.incoming_port.value,
            self._settings.outgoing_port.value,
            self._settings.incoming_topic.value,
            self._settings.outgoing_topic.value,
            self._localization_controller
        )
        
        # Replace the old IO with the new one
        self._localization_io = new_io
        self._localization_io.log.setLevel(logging.INFO)
        self._selection_controller = self._localization_io.selectionController
    
    @property
    def video_loaded(self) -> bool:
        """
        Property to tell whether or not the video is loaded.
        """
        return self._video_reference_uuid is not None and self._frame_rate is not None
    
    def set_video_reference_uuid(self, uuid: str):
        """
        Set the video reference UUID.
        """
        self._video_reference_uuid = uuid
    
    def set_frame_rate(self, frame_rate: float):
        """
        Set the video frame rate.
        """
        # Check if we need to reload tracks
        if self._frame_rate is not None and self._frame_rate != frame_rate:
            self._localization_controller.clear()
            self._loaded_ids.clear()
        
        self._frame_rate = frame_rate
    
    def frame_to_ms(self, frame: int):
        """
        Convert a frame number to elapsed milliseconds.
        """
        if not self.video_loaded:
            return ValueError('Video not loaded')
        
        return round((1e3 / self._frame_rate) * frame)

    def ms_to_frame(self, ms: int):
        """
        Convert elapsed milliseconds to a frame number.
        """
        if not self.video_loaded:
            return ValueError('Video not loaded')
        
        return round(self._frame_rate * (ms / 1e3))
    
    def sort(self, *_):
        """
        Sort the list of tracks by start frame.
        """
        self._tracks.sort(key=lambda track: (track.start_frame, track.id))
        self.layoutChanged.emit()

    def rowCount(self, parent) -> int:
        """
        Get the number of tracks in the list.
        """
        return len(self._tracks)

    def _register(self, track: IdentifiedTrack):
        """
        Register a track internally. Do not call this directly - use add_track or set_tracks instead.
        """
        # Add the track to the list
        self._tracks.append(track)
        
        # Create an interval that represents the track duration
        interval = Interval(track.start_frame, track.start_frame + len(track), track)
        self._track_tree.add(interval)  # Add the interval to the IntervalTree
        self._track_id_interval_dict[track.id] = interval  # Keep a reference to the interval
        
        # Generate a list of Localizations for the track, but don't add them to the LocalizationController yet
        localizations = list(self._generate_localizations(track))
        self._track_id_localization_list_dict[track.id] = localizations
        
    def _unregister(self, idx: int):
        """
        Unregister a track internally. Do not call this directly - use remove_track instead.
        """
        track_id = self.get_track(idx).id
        
        # Immediately remove the track from the LocalizationController, if loaded
        if track_id in self._loaded_ids:
            self._localization_controller.removeLocalizations(self._track_id_localization_list_dict[track_id])
            self._loaded_ids.remove(track_id)
        del self._track_id_localization_list_dict[track_id]
        
        # Remove the track's interval from the IntervalTree
        interval = self._track_id_interval_dict[track_id]
        self._track_tree.remove(interval)
        del self._track_id_interval_dict[track_id]
        
        # Remove the track from the list
        del self._tracks[idx]

    def add_track(self, track: IdentifiedTrack):
        """
        Add a track to the list.
        
        Note: this will emit the layoutChanged signal on each call, which is inefficient when rendering to multiple displays. 
        If you want to add multiple tracks at once, use set_tracks instead.
        """
        self.beginInsertRows(QtCore.QModelIndex(), len(self._tracks), len(self._tracks))
        self._register(track)
        self.endInsertRows()
        self.sort()
    
    def clear(self):
        """
        Clear the list of tracks.
        """
        self.beginResetModel()
        self._tracks = []
        self._track_tree.clear()
        self._track_id_interval_dict = {}
        self._track_id_localization_list_dict = {}
        self._loaded_ids = set()
        self._localization_controller.clear()
        self.endResetModel()
    
    def set_tracks(self, tracks: List[IdentifiedTrack]):
        """
        Set the list of tracks.
        """
        self.clear()
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(tracks) - 1)
        for track in tracks:
            self._register(track)
        self.endInsertRows()
        self.sort()
    
    def _load_localizations(self, track: IdentifiedTrack):
        """
        Load the track's localizations into the LocalizationController.
        """
        if track.id in self._loaded_ids:  # Short-circuit if the track is already loaded
            return
        
        localizations = self._track_id_localization_list_dict[track.id]
        self._localization_controller.addLocalizations(localizations)
        self._loaded_ids.add(track.id)
    
    def load_at_frame(self, frame_number: int):
        """
        Load localizations for tracks overlapping the given frame number.
        """
        overlapping_intervals = self._track_tree[frame_number-100:frame_number+100]
        for interval in overlapping_intervals:
            self._load_localizations(interval.data)
    
    def get_track(self, idx: int) -> IdentifiedTrack:
        """
        Get the track at the given index.
        """
        return self._tracks[idx]
            
    def index_by_id(self, id: int) -> int:
        """
        Find the index of the track with the given ID.
        
        Raises a ValueError if a track with the given ID is not found.
        """
        return self._tracks.index(self._track_id_interval_dict[id].data)
    
    def get_interval(self, key):
        """
        Index the IntervalTree with the given key.
        
        TODO: Don't interfaace with the IntervalTree directly.
        """
        return self._track_tree[key]
    
    def set_track(self, idx: int, track: IdentifiedTrack):
        """
        Update the track at the given index.
        """
        self._tracks[idx] = track
        self.dataChanged.emit(self.index(idx), self.index(idx))
        self.sort()
        
    def delete_track(self, idx):
        """
        Delete the track at the given index.
        """
        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self._unregister(idx)
        self.endRemoveRows()
        
    def get_all_tracks(self):
        """
        Get the list of all tracks.
        """
        return self._tracks

    def get_next_id(self):
        """
        Get the next available track ID.
        """
        max_id = 0 if len(self._tracks) == 0 else max(track.id for track in self._tracks)
        return max_id + 1

    def data(self, index, role):
        if not index.isValid():
            return None
        
        track = self.get_track(index.row())
        
        if role == QtCore.Qt.DisplayRole:
            return track.label
        elif role == self.IDRole:
            return track.id
        elif role == self.LabelRole:
            return track.label
        elif role == self.StartFrameRole:
            return track.start_frame
        elif role == self.BoxesRole:
            return track.boxes
        return None
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        
        track = self.get_track(index.row())
        
        if role == self.LabelRole:
            # Update the label
            track.label = value
            
            # Replace localizations
            localizations = self._track_id_localization_list_dict[track.id]  # Get old localizations
            new_localizations = list(self._generate_localizations(track))  # Make the new localizations
            self._localization_controller.removeLocalizations(localizations)  # Remove the old localizations
            self._localization_controller.addLocalizations(new_localizations)  # Add the new localizations
            self._track_id_localization_list_dict[track.id] = new_localizations  # Update the localization list dict
            
            self.dataChanged.emit(index, index)
        elif role == self.BoxesRole:    
            # Update the boxes
            track.boxes = value
            
            # Replace interval
            interval = self._track_id_interval_dict[track.id]  # Get old interval
            new_interval = Interval(interval.begin, interval.begin + len(value), track)  # Make the new interval
            self._track_tree.remove(interval)  # Remove the old interval
            self._track_tree.add(new_interval)  # Add the new interval
            self._track_id_interval_dict[track.id] = new_interval  # Update the interval dict
            
            # Replace localizations
            localizations = self._track_id_localization_list_dict[track.id]  # Get old localizations
            new_localizations = list(self._generate_localizations(track))  # Make the new localizations
            self._localization_controller.removeLocalizations(localizations)  # Remove the old localizations
            self._localization_controller.addLocalizations(new_localizations)  # Add the new localizations
            self._track_id_localization_list_dict[track.id] = new_localizations  # Update the localization list dict
            
            self.dataChanged.emit(index, index)
        else:
            return False
        
        return True

    def _generate_localizations(self, track: IdentifiedTrack) -> Iterable[Localization]:
        """
        Generate localizations for the given track.
        """
        for frame_offset, box in enumerate(track.boxes):
            if not box:
                continue
            yield Localization(
                concept=f'{track.id} - {track.label}',
                elapsedTime=self.frame_to_ms(track.start_frame + frame_offset),
                duration=0,
                videoReferenceUuid=UUID(self._video_reference_uuid),
                annotationUuid=UUID(int=track.id),
                localizationUuid=uuid4(),  # TODO: Ensure unique
                x=box.x,
                y=box.y,
                width=box.w,
                height=box.h
            )
    
    def select_track(self, idx: int):
        """
        Select the track at the given index.
        """
        selected_track = self.get_track(idx)
        if selected_track.id not in self._loaded_ids:  # track needs load
            self._load_localizations(selected_track)
        
        track_localizations = self._track_id_localization_list_dict[selected_track.id]
        
        # Sharktopoda client clears the selection. We avoid this by unioning the new selection with the old selection.
        previous_localizations = self._selection_controller.getSelectedLocalizations()
        previous_localization_uuids = set(localization.localizationUuid for localization in previous_localizations)
        
        union = previous_localizations + [loc for loc in track_localizations if loc.localizationUuid not in previous_localization_uuids]
        
        self._selection_controller.select(union, True)
    
    def deselect_track(self, idx: int):
        """
        Deselect the track at the given index.
        """
        deselected_track = self.get_track(idx)
        if deselected_track.id not in self._loaded_ids:  # track needs load
            self._load_localizations(deselected_track)
        
        track_localizations = self._track_id_localization_list_dict[deselected_track.id]
        
        self._selection_controller.deselect(track_localizations, True)
