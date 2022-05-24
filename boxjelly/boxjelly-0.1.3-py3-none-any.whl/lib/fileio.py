"""
File IO operations. 

Each type is encapsulated in a QObject subclass which provides read/write capability.
"""

from collections import defaultdict
from io import BytesIO
import json
import os
import tarfile
from typing import List, Union, Any
from pathlib import Path
from uuid import UUID

from PyQt5 import QtCore

from boxjelly.lib.track import BoundingBox, IdentifiedTrack


class AbstractFileIO(QtCore.QObject):
    """
    File IO abstract class.
    """
    
    fileRead = QtCore.pyqtSignal(object)  # payload can be any object
    fileWritten = QtCore.pyqtSignal()
    fileReadFailure = QtCore.pyqtSignal(str)
    fileWriteFailure = QtCore.pyqtSignal(str)
    
    def __init__(self, path: Union[str, Path]):
        super().__init__()
        
        self._path = None
        self.path = path
    
    @property
    def path(self) -> Path:
        return self._path
    
    @path.setter
    def path(self, path: Union[str, Path]):
        self._path = Path(path)  # ensure type Path
    
    def _write(self, data: Any):
        """
        Write data to file. Do not call this directly; instead call write.
        
        Subclasses should implement this method.
        """
        raise NotImplementedError()
        
    def write(self, data: Any):
        """
        Write data to file.
        """
        try:
            self._write(data)
        except Exception as e:
            self.fileWriteFailure.emit(str(e))
            return
        
        self.fileWritten.emit()
    
    def _read(self) -> Any:
        """
        Read data from file. Do not call this directly; instead call read.
        
        Subclasses should implement this method.
        """
        raise NotImplementedError()
    
    def read(self) -> Any:
        """
        Read data from file.
        """
        try:
            data = self._read()
        except Exception as e:
            self.fileReadFailure.emit(str(e))
            return
        
        self.fileRead.emit(data)
        return data


class AbstractTrackFileIO(AbstractFileIO):
    """
    File IO abstract class that deals with collections of identified tracks.
    """
    
    def _write(self, data: List[IdentifiedTrack]):
        return super()._write(data)
    
    def write(self, data: List[IdentifiedTrack]):
        """
        Write tracks to file.
        """
        return super().write(data)
    
    def _read(self) -> List[IdentifiedTrack]:
        return super()._read()
    
    def read(self) -> List[IdentifiedTrack]:
        """
        Read tracks from file.
        """
        return super().read()


class JSONTrackFileIO(AbstractTrackFileIO):
    """
    JSON track file IO.
    """
    
    def _write(self, data: List[IdentifiedTrack]):
        track_dicts = [track.to_dict() for track in data]
        
        with self._path.open('w') as f:
            json.dump(track_dicts, f, indent=2)
    
    def _read(self) -> List[IdentifiedTrack]:
        with self._path.open('r') as f:
            track_dicts = json.load(f)
        
        tracks = []
        for track_dict in track_dicts:
            tracks.append(IdentifiedTrack.from_dict(track_dict))
        return tracks


class YOLOv5DeepSortTrackFileIO(AbstractTrackFileIO):
    """
    YOLOv5-DeepSort track file IO.
    """
    
    def _write(self, data: List[IdentifiedTrack]):
        raise NotImplementedError()
    
    def _read(self) -> List[IdentifiedTrack]:
        track_dict = {}
        
        with open(self._path, 'r') as f:
            for line in f:
                if not line:  # Empty line, skip
                    continue
                
                # Try to parse line fields
                try:
                    parts = line.strip().split(' ')
                    
                    # video_filename = parts[0]
                    frame_number = int(parts[1])
                    track_id = int(parts[2])
                    x = int(parts[3])
                    y = int(parts[4])
                    w = int(parts[5])
                    h = int(parts[6])
                    label = ' '.join(parts[11:])
                    
                    # Create track if it doesn't exist
                    if track_id not in track_dict:
                        track_dict[track_id] = IdentifiedTrack(start_frame=frame_number, boxes=[], id=track_id, label=label)
                    track = track_dict[track_id]
                    
                    # Fill in frame jump
                    if track.boxes:
                        start_frame = track.start_frame
                        while frame_number != start_frame + len(track.boxes):
                            track.boxes.append(None)
                    
                    # Add detection to track
                    track.boxes.append(BoundingBox(x, y, w, h))
                    
                except Exception as e:
                    raise ValueError(f'Failed to parse YOLOv5-DeepSort line: {line}') from e
        
        tracks = list(track_dict.values())
        
        return tracks


class DeepseaTrackFileIO(AbstractTrackFileIO):
    """
    Deepsea track file IO.
    """
    
    def _write(self, data: List[IdentifiedTrack]):
        # Reformat list of tracks as dict of frame -> "visual event" set
        visual_events_by_frame = defaultdict(list)
        for track in data:
            for frame_offset, box in enumerate(track.boxes):
                frame_num = track.start_frame + frame_offset
                visual_events_by_frame[frame_num].append({
                    'bounding_box': {
                        'height': int(box.h),
                        'width': int(box.w),
                        'x': int(box.x),
                        'y': int(box.y)
                    },
                    'class_index': -1,  # TODO: fill in
                    'class_name': track.label,
                    'confidence': -1,  # TODO: fill in
                    'frame_num': frame_num,
                    'occlusion': -1,  # TODO: fill in
                    'surprise': -1,  # TODO: fill in
                    'uuid': str(UUID(int=track.id))  # TODO: come up with mapping system ... or switch to UUIDs internally
                })
        
        # Get max frame number
        max_frame = max(visual_events_by_frame.keys())
        
        # For each frame, write boxes to JSON in .tar.gz archive
        with tarfile.open(self._path, 'w:gz') as tar:
            for frame in range(1, max_frame + 1):
                visual_events = visual_events_by_frame.get(frame, [])
                filename = f'f{str(frame).zfill(6)}.json'
                
                json_data = [  # wacky format
                    'visualevents',
                    [
                        ['visualevent'] + [visual_event]
                        for visual_event in visual_events
                    ]
                ]
                
                # Encode and describe file
                byte_data = json.dumps(json_data).encode('utf-8')
                buf = BytesIO(byte_data)
                tar_info = tarfile.TarInfo(filename)
                tar_info.size = len(byte_data)
                
                # Add to archive
                tar.addfile(tar_info, buf)
    
    def _read(self) -> List[IdentifiedTrack]:
        track_dict = {}
    
        # Open the tar file
        with tarfile.open(self._path) as t:
            # Find archived JSON files
            json_paths = [path for path in t.getnames() if path.endswith('.json') and os.path.basename(path).startswith('f')]
        
            for json_path in json_paths:
                # Try to parse the JSON
                try:
                    with t.extractfile(json_path) as f:
                        data = json.load(f)
                        event_items = data[1]
                        for event_item in event_items:
                            event_data = event_item[1]
                            
                            frame_number = int(event_data['frame_num'])
                            box = event_data['bounding_box']
                            x = int(box['x'])
                            y = int(box['y'])
                            w = int(box['width'])
                            h = int(box['height'])
                            label = event_data['class_name']
                            
                            # Create track if it doesn't exist
                            uuid = event_data['uuid']
                            if uuid not in track_dict:
                                track_dict[uuid] = IdentifiedTrack(start_frame=frame_number, boxes=[], id=len(track_dict), label=label)
                            track = track_dict[uuid]
                            
                            # Fill in frame jump
                            if track.boxes:
                                start_frame = track.start_frame
                                while frame_number != start_frame + len(track.boxes):
                                    track.boxes.append(None)
                            
                            # Add detection to track
                            track.boxes.append(BoundingBox(x, y, w, h))
                            
                except Exception as e:
                    raise ValueError(f'Failed to parse {self.filename}/{json_path}') from e

        tracks = list(track_dict.values())
        
        return tracks
