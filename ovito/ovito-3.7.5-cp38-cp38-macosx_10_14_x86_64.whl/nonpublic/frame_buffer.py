from . import FrameBuffer

# Implement FrameBuffer.image property (requires conversion to a Shiboken object).
def _get_FrameBuffer_image(self):
    from ovito.qt_compat import shiboken
    from ovito.qt_compat import QtGui
    return QtGui.QImage(shiboken.wrapInstance(self._image, QtGui.QImage))
FrameBuffer.image = property(_get_FrameBuffer_image)
