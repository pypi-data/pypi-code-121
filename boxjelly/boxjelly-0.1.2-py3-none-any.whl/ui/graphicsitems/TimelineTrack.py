from PyQt5 import QtWidgets, QtCore

from boxjelly.lib.track import IdentifiedTrack
from boxjelly.lib.util import concept_color


class TimelineTrack(QtWidgets.QGraphicsItemGroup):
    """
    Graphical representation of a track within the timeline view.
    """
    
    DEFAULT_HEIGHT = 30
    
    def __init__(self, track: IdentifiedTrack, scale_x: float = 1.0, scale_y: float = 1.0, parent=None):
        super().__init__(parent=parent)
        
        self._track = track  # original track
        
        self._scale_x = scale_x  # horizontal scale, in scene units per frame
        self._scale_y = scale_y  # vertical scale, in scene units per height unit
        
        self._track_rect = QtWidgets.QGraphicsRectItem(self)
        self._track_id_text = QtWidgets.QGraphicsSimpleTextItem(str(track.id), self)
        
        self.update()
        
    def update(self):
        self._track_rect.setBrush(concept_color(self._track.label))
        self._rescale()
        super().update()
    
    def set_scale(self, scale_x: float, scale_y: float):
        """
        Set the scale of the track.
        """
        self._scale_x = scale_x
        self._scale_y = scale_y
        
        self._rescale()
    
    def __len__(self):
        return len(self._track)
    
    @property
    def width_scene(self):
        return len(self) * self._scale_x
    
    @property
    def height_scene(self):
        return self.DEFAULT_HEIGHT * self._scale_y 
    
    def _rescale(self):
        """
        Rescale the child items.
        """
        self._track_rect.setRect(0, 0, self.width_scene, self.height_scene)
        
        rect_bounds = self._track_rect.boundingRect()
        text_bounds = self._track_id_text.boundingRect()
        self._track_id_text.setPos(
            int(rect_bounds.width() / 2 - text_bounds.width() / 2), 
            int(rect_bounds.height() / 2 - text_bounds.height() / 2)
        )
        self._track_id_text.setVisible(text_bounds.width() < rect_bounds.width())
            
    @property
    def track(self):
        return self._track
    
    def boundingRect(self) -> QtCore.QRectF:
        return self._track_rect.boundingRect()
    
    