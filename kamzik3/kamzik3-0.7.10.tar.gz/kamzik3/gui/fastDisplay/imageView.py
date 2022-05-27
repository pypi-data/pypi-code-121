import time
from collections import deque
from threading import Lock

import numpy as np
from PyQt5.QtCore import QRect, pyqtSlot, Qt
from PyQt5.QtGui import QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QOpenGLWidget


class ImageView(QOpenGLWidget):
    scaled = True
    max_fps = 30

    def __init__(self):
        QOpenGLWidget.__init__(self)
        self.paint_lock = Lock()
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.frame_size_rect = QRect(0, 0, self.width(), self.height())
        self.screen_size_rect = QRect(0, 0, self.width(), self.height())
        self.last_processed_frame = QPixmap(1, 1).toImage()
        self.frame_buffer = deque(maxlen=2)
        self.last_frame_time = time.perf_counter_ns()
        self.refresh_timeout = 1e9 / self.max_fps

    @pyqtSlot(np.ndarray)
    def slot_new_frame(self, frame_data):
        if (time.perf_counter_ns() - self.last_frame_time) >= self.refresh_timeout:
            self.last_frame_time = time.perf_counter_ns()
            self.frame_buffer.append(frame_data)
            self.update()

    def resizeGL(self, new_w, new_h):
        frame_w, frame_h = (
            self.last_processed_frame.width(),
            self.last_processed_frame.height(),
        )

        if frame_h > 0 and new_h > 0:
            ri = frame_w / frame_h
            rs = new_w / new_h

            if rs > ri:
                w, h = frame_w * new_h / frame_h, new_h
            else:
                w, h = new_w, frame_h * new_w / frame_w
        else:
            w = new_w
            h = new_h
        self.frame_size_rect = QRect(0, 0, w, h)
        self.screen_size_rect = QRect(0, 0, new_w, new_h)

    @staticmethod
    def frame_to_qimage(frame, color_scheme=QImage.Format_RGB888):
        """
        Convert frame from numpy array format into QImage.

        :param frame: Numpy array
        :type frame: Array
        :return: Converted QImage
        :rtype: QImage
        """
        h, w = frame.shape[:2]
        return QImage(frame.data, w, h, color_scheme)

    def process_next_frame(self):
        """
        Frame processing pipeline.

        Apply filters and transformations for next frame.

        :return: Processed frame as QImage object.
        :rtype: QImage
        """
        frame = self.frame_buffer.pop()
        color_scheme = QImage.Format_RGB888
        if len(frame.shape) == 2:
            color_scheme = QImage.Format_Grayscale8
        return self.frame_to_qimage(frame, color_scheme)

    def paintEvent(self, QPaintEvent):
        # Return If previous paint event is still handled
        if self.paint_lock.locked():
            return
        with self.paint_lock:
            try:
                self.last_processed_frame = self.process_next_frame()
            except IndexError:
                # No new frame to process.
                # We just skip here and use previous processed frame.
                pass
            painter = QPainter(self)
            painter.drawImage(self.frame_size_rect, self.last_processed_frame)
