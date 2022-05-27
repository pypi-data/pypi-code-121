from PyQt5.QtCore import QObject, QPointF, QPoint, Qt
from PyQt5.QtGui import QBrush
from typing import Any, Dict

NORMAL_TEXT = 0
STATIC_TEXT = 1


class GlWidget(QObject):
    all: Dict[Any, "GlWidget"] = {}
    tooltipText = None
    text = None
    textCoords = None
    opacity = 1
    onClick = None
    angle = None
    background = None

    def __init__(self, parent, widget_id, coords, texture=None, border=False):
        QObject.__init__(self)
        self.setParent(parent)
        self.font = None
        self.add_border = border
        self.id = widget_id
        self.coords = coords
        self.texture = texture
        self.clickPath = coords
        self.clickPathTransformed = coords
        self.align = Qt.AlignCenter
        self.background_shape = "rect"
        self.background_coords = coords
        GlWidget.all[self.id] = self

    def set_background(self, coords=None, color=Qt.white, shape=None):
        if coords is None:
            coords = self.background_coords
        else:
            self.background_coords = coords
        if shape is None:
            shape = self.background_shape
        else:
            self.background_shape = shape
        self.background = (coords, color, shape)
        return self

    def set_text(self, text, font, align=Qt.AlignCenter):
        self.text = text
        self.font = font
        self.align = align
        return self

    def set_tooltip_text(self, value):
        self.tooltipText = value
        return self

    def draw(self, painter):
        painter.save()
        if self.angle is not None:
            painter.translate(self.coords.center())
            painter.rotate(self.angle)
            painter.translate(self.coords.center() * -1)

        if self.texture is not None:
            painter.setOpacity(self.opacity)
            painter.drawPixmap(self.coords, self.texture)
        if self.background is not None:
            coords, color, shape = self.background
            pen = painter.pen()
            brush = painter.brush()
            if not self.add_border:
                painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            if shape == "rect":
                painter.drawRect(coords)
            elif shape == "ellipse":
                painter.drawEllipse(coords)
            painter.setPen(pen)
            painter.setBrush(brush)

        self.matrix = painter.worldTransform()
        self.clickPathTransformed = self.matrix.mapToPolygon(self.clickPath)

        painter.setOpacity(1)
        self.paint_text(painter)
        painter.restore()
        return self

    def paint_text(self, painter):
        if self.text is None:
            return
        painter.setFont(self.font)
        painter.drawText(self.coords, self.align, self.text)
        return self

    @staticmethod
    def _getStaticTextCoordds(boundRect, staticText):
        center = boundRect.center()
        font_size = staticText.size()
        return QPointF(
            center.x() - (font_size.width() / 2.0),
            center.y() - font_size.height() / 2.0,
        )

    @staticmethod
    def get(widget_id):
        return GlWidget.all.get(widget_id)

    def set_on_click(self, callback):
        self.onClick = callback
        return self

    def click(self):
        self.onClick(self)

    def rotate(self, angle):
        self.angle = angle
        return self

    def set_click_path(self, click_path):
        self.clickPath = click_path
        return self

    def is_point_inside(self, point):
        if isinstance(point, (QPoint, QPointF)):
            return self.clickPathTransformed.containsPoint(
                point, Qt.FillRule(Qt.OddEvenFill)
            )


class GlSwitchTexture(GlWidget):
    state = 0

    def __init__(self, parent, widget_id, coords, on_texture, off_texture):
        GlWidget.__init__(self, parent, widget_id, coords)
        self.on_texture = on_texture
        self.off_texture = off_texture

    def set_state(self, state):
        self.state = state
        return self

    def draw(self, painter):
        if self.state:
            self.texture = self.on_texture
        else:
            self.texture = self.off_texture
        return GlWidget.draw(self, painter)


class GlMappedTexture(GlWidget):
    key = 0

    def __init__(self, parent, widget_id, coords, texture_map):
        GlWidget.__init__(self, parent, widget_id, coords)
        self.texture_map = texture_map

    def set_state(self, state):
        return self.set_key(state)

    def set_key(self, key):
        self.key = key
        return self

    def draw(self, painter):
        self.texture = self.texture_map[self.key]
        return GlWidget.draw(self, painter)


class GlSwitchColor(GlWidget):
    state = 0

    def __init__(self, parent, widget_id, coords, on_color, off_color):
        GlWidget.__init__(self, parent, widget_id, coords)
        self.on_color = on_color
        self.off_color = off_color

    def set_state(self, state):
        self.state = state
        return self

    def draw(self, painter):
        if self.background is not None:
            coords, _, shape = self.background
        else:
            coords, shape = self.coords, "rect"
        if self.state:
            self.background = (coords, self.on_color, shape)
        else:
            self.background = (coords, self.off_color, shape)
        return GlWidget.draw(self, painter)


class GlMappedColor(GlWidget):
    key = 0

    def __init__(self, parent, widget_id, coords, color_map):
        GlWidget.__init__(self, parent, widget_id, coords)
        self.color_map = color_map

    def set_state(self, state):
        return self.set_key(state)

    def set_key(self, key):
        self.key = key
        return self

    def draw(self, painter):
        if self.background is not None:
            coords, _, shape = self.background
        else:
            coords, shape = self.coords, "rect"
        self.background = (coords, self.color_map[self.key], shape)
        return GlWidget.draw(self, painter)
