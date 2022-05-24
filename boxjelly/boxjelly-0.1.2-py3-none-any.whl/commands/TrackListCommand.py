from PyQt5 import QtWidgets
from boxjelly.lib.track import IdentifiedTrack

from boxjelly.models.TrackListModel import TrackListModel


class TrackListModelCommand(QtWidgets.QUndoCommand):
    def __init__(self, track_model: TrackListModel):
        super().__init__()
        
        self._track_model = track_model
        
        self.setText('Track list model command')


class DeleteTrackByRowCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, row: int):
        super().__init__(track_model)
        
        self._row = row
        self._track = None
        
        self.setText('Delete track by row {}'.format(row))
    
    def undo(self):
        self._track_model.add_track(self._track)
        self._row = self._track_model.index_by_id(self._track.id)
    
    def redo(self):
        self._track = self._track_model.get_track(self._row)
        self._track_model.delete_track(self._row)


class DeleteTrackByIDCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, track_id: int):
        super().__init__(track_model)
        
        self._track_id = track_id
        self._track = None
        
        self.setText('Delete track {}'.format(track_id))

    def undo(self):
        self._track_model.add_track(self._track)

    def redo(self):
        idx = self._track_model.index_by_id(self._track_id)
        self._track = self._track_model.get_track(idx)
        self._track_model.delete_track(idx)
        

class BatchDeleteTracksByIDCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, track_ids: list):
        super().__init__(track_model)
        
        self._track_ids = track_ids
        self._tracks = []
        
        self.setText('Batch delete tracks {}'.format(', '.join(str(track_id) for track_id in track_ids)))
    
    def undo(self):
        for track in self._tracks:
            self._track_model.add_track(track)
    
    def redo(self):
        self._tracks.clear()
        for track_id in self._track_ids:
            row_idx = self._track_model.index_by_id(track_id)
            track = self._track_model.get_track(row_idx)
            self._tracks.append(track)
            self._track_model.delete_track(row_idx)
        

class BatchRenameTracksCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, track_ids: list, new_label: str):
        super().__init__(track_model)
        
        self._track_ids = track_ids
        self._new_label = new_label
        self._old_labels = []
        
        self.setText('Rename track(s) {} -> "{}"'.format(', '.join(str(track_id) for track_id in track_ids), new_label))
    
    def undo(self):
        for track_id, label in zip(self._track_ids, self._old_labels):
            idx = self._track_model.index_by_id(track_id)
            index = self._track_model.index(idx, 0)
            self._track_model.setData(index, label, TrackListModel.LabelRole)
    
    def redo(self):
        self._old_labels.clear()
        for track_id in self._track_ids:
            row_idx = self._track_model.index_by_id(track_id)
            index = self._track_model.index(row_idx, 0)
            self._old_labels.append(self._track_model.data(index, TrackListModel.LabelRole))
            self._track_model.setData(index, self._new_label, TrackListModel.LabelRole)


class SplitTrackCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, track_id: int, split_idx: int):
        super().__init__(track_model)
        
        self._track_id = track_id
        self._new_track_id = None
        self._split_idx = split_idx
        
        self.setText('Split track {} at {}'.format(track_id, split_idx))
    
    def undo(self):
        old_track_row_idx = self._track_model.index_by_id(self._track_id)
        old_track_index = self._track_model.index(old_track_row_idx, 0)
        
        new_track_row_idx = self._track_model.index_by_id(self._new_track_id)
        new_track_index = self._track_model.index(new_track_row_idx, 0)
        
        old_boxes = old_track_index.data(TrackListModel.BoxesRole)
        new_boxes = new_track_index.data(TrackListModel.BoxesRole)
        
        self._track_model.setData(old_track_index, old_boxes + new_boxes, TrackListModel.BoxesRole)  # Concatenate new boxes back to old track
        self._track_model.delete_track(new_track_row_idx)  # Remove new track
    
    def redo(self):
        row_idx = self._track_model.index_by_id(self._track_id)
        index = self._track_model.index(row_idx, 0)
        
        boxes = self._track_model.data(index, TrackListModel.BoxesRole)
        
        old_boxes = boxes[:self._split_idx]
        new_boxes = boxes[self._split_idx:]
        
        old_start_frame = index.data(TrackListModel.StartFrameRole)
        old_label = index.data(TrackListModel.LabelRole)
        
        new_track = IdentifiedTrack(
            old_start_frame + self._split_idx,  # Start frame = old start frame + split index
            new_boxes,
            self._track_model.get_next_id(),  # ID = next ID available from model
            old_label  # Label = old label
        )
        
        self._new_track_id = new_track.id
        
        self._track_model.setData(index, old_boxes, TrackListModel.BoxesRole)  # Clip the old track boxes
        self._track_model.add_track(new_track)  # Add the new track


class MergeTracksCommand(TrackListModelCommand):
    def __init__(self, track_model: TrackListModel, track_ids: list):
        super().__init__(track_model)
        
        self._track_ids = track_ids
        self._original_tracks = []
        self._new_track_id = None
        
        self.setText('Merge tracks {}'.format(', '.join(str(track_id) for track_id in track_ids)))
    
    def undo(self):
        new_track_row_idx = self._track_model.index_by_id(self._new_track_id)
        self._track_model.delete_track(new_track_row_idx)  # Delete the new track
        
        # Restore the original tracks
        for track in self._original_tracks:
            self._track_model.add_track(track)
    
    def redo(self):
        # Collect the tracks and remove them from the model
        self._original_tracks.clear()
        for track_id in self._track_ids:
            row_idx = self._track_model.index_by_id(track_id)
            track = self._track_model.get_track(row_idx)
            self._original_tracks.append(track)
            self._track_model.delete_track(row_idx)
            
        # Sort by start frame
        self._original_tracks.sort(key=lambda track: track.start_frame)
        
        start_frame = self._original_tracks[0].start_frame
        end_frame = max(track.start_frame + len(track.boxes) for track in self._original_tracks)
        
        boxes_by_frame = []
        next_track_idx = 0
        for frame_num in range(start_frame, end_frame + 1):
            if next_track_idx < len(self._original_tracks) and self._original_tracks[next_track_idx].start_frame == frame_num:
                current_track = self._original_tracks[next_track_idx]
                next_track_idx += 1
            
            # Get the index of the box in the current track that corresponds to this frame
            box_idx = frame_num - current_track.start_frame
            
            # Append the corresponding box (or None if there is no box) to the list
            if box_idx < len(current_track.boxes):
                boxes_by_frame.append(current_track.boxes[box_idx])
            else:  # If the box index is out of bounds, then the current track has no boxes for this frame
                boxes_by_frame.append(None)
        
        # Create the new track
        new_track = IdentifiedTrack(
            start_frame,  # Start frame = start frame of first track
            boxes_by_frame,
            self._track_model.get_next_id(),  # ID = next ID available from model
            self._original_tracks[0].label  # Label = label of first track
        )
        
        self._new_track_id = new_track.id

        self._track_model.add_track(new_track)  # Add the new track
        