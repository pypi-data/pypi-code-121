import math

from PyQt5 import QtWidgets, QtCore, QtGui


class Timeline(QtWidgets.QWidget):
    
    frameChanged = QtCore.pyqtSignal(int)
    frameStepChanged = QtCore.pyqtSignal(int)
    frameScaleChanged = QtCore.pyqtSignal(float)
    frameSelected = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, frame_step: int, frame_scale: float = 1.0):
        super().__init__(parent)
        
        self._background_brush = self.palette().window()
        self._foreground_brush = self.palette().windowText()
        
        self._frame = 0
        self._frame_step = frame_step
        self._frame_scale = frame_scale
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def set_frame(self, frame: int):
        """
        Set the current frame to be displayed.
        """
        if frame != self._frame:
            self.frameChanged.emit(frame)
        self._frame = frame
        self.update()
    
    def set_frame_step(self, frame_step: int):
        """
        Set the frame step.
        """
        if frame_step != self._frame_step:
            self.frameStepChanged.emit(frame_step)
        self._frame_step = frame_step
        self.update()
    
    def set_frame_scale(self, frame_scale: float):
        """
        Set the frame scale.
        """
        if frame_scale != self._frame_scale:
            self.frameScaleChanged.emit(frame_scale)
        self._frame_scale = frame_scale
        self.update()
    
    def map_frame_to_x(self, frame: int) -> int:
        """
        Map a frame to an x coordinate.
        """
        return int((frame - self._frame) * self._frame_scale)
    
    def map_x_to_frame(self, x: int) -> int:
        """
        Map an x coordinate to a frame.
        """
        return int(x / self._frame_scale + self._frame)

    @property
    def frame(self):
        return self._frame
    
    @property
    def frame_step(self):
        return self._frame_step
    
    @property
    def frame_scale(self):
        return self._frame_scale
    
    @property
    def max_frame(self) -> int:
        return int(self._frame + self.width() / self._frame_scale)

    def paintEvent(self, event: QtGui.QPaintEvent):
        # Get the painter
        painter = QtGui.QPainter(self)
        
        # Get the device size
        width = painter.device().width()
        height = painter.device().height()
        
        # Set pen to foreground
        painter.setPen(self._foreground_brush.color())
        
        # Draw horizontal line at bottom
        painter.drawLine(0, height - 1, width, height - 1)
        
        # Compute the multiples of the frame step in the range [frame, max_frame]
        tick_frames = range(math.floor(self._frame / self._frame_step) * self._frame_step, self.max_frame + 1, self._frame_step)
        
        # Draw vertical lines and labels at the tick frames
        for tick_frame in tick_frames:
            x = self.map_frame_to_x(tick_frame)
            painter.drawLine(x, height - 1, x, height - height // 4)
            painter.drawText(x + 5, height - 5, str(tick_frame))
    
    def sizeHint(self):
        return QtCore.QSize(100, 20)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.frameSelected.emit(self.map_x_to_frame(event.x()))
