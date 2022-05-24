from socket import socket, AF_INET, SOCK_DGRAM, timeout
from typing import Optional
from uuid import uuid4

from sharktopoda_client.model.GenericCommand import GenericCommand
from sharktopoda_client.model.GenericResponse import GenericResponse
from PyQt5 import QtMultimedia, QtCore
from boxjelly.lib.constants import CONTROL_HOST
from boxjelly.lib.settings import SettingsManager

from boxjelly.models.TrackListModel import TrackListModel


class CthulhuVideoController(QtCore.QObject):
    """
    Cthulhu video controller. Redirects calls to Cthulhu UDP commands/responses.
    """
    
    FRAME_UPDATE_INTERVAL = 100
    
    positionChanged = QtCore.pyqtSignal(int)
    frameUpdated = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, track_model: TrackListModel, selection_model: QtCore.QItemSelectionModel):
        super().__init__(parent)
        
        self._track_model = track_model
        self._selection_model = selection_model
        
        self._udp_socket = socket(AF_INET, SOCK_DGRAM)
        self._udp_socket.settimeout(0.5)  # 500ms timeout for response
        
        self._url = None
        self._uuid = None
        
        self._dummy_player = QtMultimedia.QMediaPlayer(self)
        
        self._last_frame_number = None
        
        self._settings = SettingsManager.get_instance()
        
        # Start polling to update the current frame every FRAME_UPDATE_INTERVAL milliseconds
        self.frame_update_timer = QtCore.QTimer(self)
        self.frame_update_timer.timeout.connect(self._do_frame_update)
        self.frame_update_timer.start(CthulhuVideoController.FRAME_UPDATE_INTERVAL)
    
    def send(self, command: GenericCommand) -> None:
        try:
            self._udp_socket.sendto(command.to_json().encode('utf-8'), (CONTROL_HOST, self._settings.control_port.value))
        except OSError as e:
            print(f'Error ({e}) while sending command to Cthulhu:\n{command.to_json(indent=2)}')  # TODO: Log
    
    def send_and_wait(self, command: GenericCommand) -> Optional[GenericResponse]:
        # Send the command
        self.send(command)
        
        # Wait for a response
        try:
            response_raw = self._udp_socket.recv(4096)
            return GenericResponse.from_json(response_raw.decode('utf-8'))
        except timeout:
            # print(f'Timeout while waiting for response to command:\n{command.to_json(indent=2)}')  # TODO: Log
            return None
    
    def set_media(self, media: QtMultimedia.QMediaContent):
        self._url = media.canonicalUrl().toString()
        self._uuid = str(uuid4())
        
        # Update track model video data
        self._track_model.set_video_reference_uuid(self._uuid)
        self._track_model.set_frame_rate(self._settings.frame_rate.value)
        
        self.open(self._url, self._uuid)
        self.pause()
    
    def open(self, url: str, uuid: str):
        """
        Open a video file by URL and assign it a given UUID.
        """
        open_video_command = GenericCommand(command='open', url=url, uuid=uuid)
        self.send_and_wait(open_video_command)
    
    def play(self):
        """
        Play (resume) the current video.
        """
        play_command = GenericCommand(command='play', uuid=self._uuid)
        self.send_and_wait(play_command)
    
    def pause(self):
        """
        Pause the current video.
        """
        pause_command = GenericCommand(command='pause', uuid=self._uuid)
        self.send_and_wait(pause_command)
    
    def stop(self):
        """
        Stop the current video (pause and seek to beginning).
        """
        self.pause()
        
        seek_beginning_command = GenericCommand(command='seek elapsed time', uuid=self._uuid, elapsedTime=0)
        self.send(seek_beginning_command)
    
    def set_frame(self, frame: int):
        """
        Seek the current video to a given frame.
        """
        seek_command = GenericCommand(command='seek elapsed time', uuid=self._uuid, elapsedTime=self._track_model.frame_to_ms(frame))
        self.send(seek_command)
    
    def get_elapsed_time(self):
        """
        Get the current elapsed time in milliseconds of the current video.
        """
        elapsed_time_command = GenericCommand(command='request elapsed time', uuid=self._uuid)
        res = self.send_and_wait(elapsed_time_command)
        
        if not res:
            return
        
        return res.elapsedTime
    
    def get_frame_number(self) -> Optional[int]:
        """
        Get the current frame number of the current video.
        """
        if not (self._url and self._uuid):
            return
        
        elapsed_time = self.get_elapsed_time()
        if not elapsed_time:
            return
        
        return self._track_model.ms_to_frame(elapsed_time)
    
    @QtCore.pyqtSlot()
    def _do_frame_update(self):
        """
        Slot for frame update timer. Updates the current frame.
        """
        frame_number = self.get_frame_number()
        if frame_number is not None and (self._last_frame_number is None or frame_number != self._last_frame_number):
            self.frameUpdated.emit(frame_number)
            self._track_model.load_at_frame(frame_number)
            self._last_frame_number = frame_number
