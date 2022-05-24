from PySide2 import QtCore, QtWidgets, QtGui


class ElidingLabel(QtWidgets.QLabel):
    """Label with text elision.

    QLabel which will elide text too long to fit the widget.  Based on:
    https://doc.qt.io/qt-5/qtwidgets-widgets-elidedlabel-example.html

    Parameters
    ----------
    text : str

        Label text.

    mode : QtCore.Qt.TextElideMode

       Specify where ellipsis should appear when displaying texts that
       don’t fit.

       Default is QtCore.Qt.ElideMiddle.

       Possible modes:
         QtCore.Qt.ElideLeft
         QtCore.Qt.ElideMiddle
         QtCore.Qt.ElideRight

    parent : QWidget

       Parent widget.  Default is None.

    f : Qt.WindowFlags()

       https://doc-snapshots.qt.io/qtforpython-5.15/PySide2/QtCore/Qt.html#PySide2.QtCore.PySide2.QtCore.Qt.WindowType

    """

    elision_changed = QtCore.Signal(bool)

    def __init__(self, text='', mode=QtCore.Qt.ElideMiddle, **kwargs):
        super().__init__(**kwargs)

        self._mode = mode
        self.is_elided = False

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setText(text)

    def setText(self, text):
        self._contents = text
        self.update()

    def text(self):
        return self._contents

    def minimumSizeHint(self):
        # make sure label doesn't clip vertically
        metrics = QtGui.QFontMetrics(self.font())
        return QtCore.QSize(0, metrics.height())

    def paintEvent(self, event):
        super().paintEvent(event)

        did_elide = False

        painter = QtGui.QPainter(self)
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())

        # layout phase
        text_layout = QtGui.QTextLayout(self._contents, painter.font())
        text_layout.beginLayout()

        while True:

            line = text_layout.createLine()

            if not line.isValid():
                break

            line.setLineWidth(self.width())

            if text_width >= self.width():
                elided_line = font_metrics.elidedText(self._contents, self._mode, self.width())
                painter.drawText(QtCore.QPoint(0, font_metrics.ascent()), elided_line)
                did_elide = line.isValid()
                break
            else:
                line.draw(painter, QtCore.QPoint(0, 0))

        text_layout.endLayout()

        self.elision_changed.emit(did_elide)

        if did_elide != self.is_elided:
            self.is_elided = did_elide
            self.elision_changed.emit(did_elide)


class TabSafeLineEdit(QtWidgets.QLineEdit):
    """Line edit with tab key control.

    The default QLineEdit will exit the widget when tab is pressed.
    This may be undesirable (e.g. entering steno strokes in a practice
    program changes the input focus).  This widget prevents focus from
    changing.

    """

    # Focus will leave regardless of the focusPolicy.  Tab is not
    # caught by keyPressEvent.  The documentation states,
    #
    #     "There are also some rather obscure events described in the
    #     documentation for Type . To handle these events, you need to
    #     reimplement event() directly."
    #
    # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QWidget.html?highlight=qwidget#events
    def event(self, event):
        if (event.type() == QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Tab):
            self.insert("\t")
            return True

        return QtWidgets.QLineEdit.event(self, event)


class TextLabel(QtWidgets.QTextEdit):
    """Enhanced text label.

    This widget is a QTextEdit styled to look like a QLabel.  QLabels
    handle color only through markup which complicates text
    manipulation.  QTextEdits provide cursors which can style text
    using object properties.

    Parameters
    ----------
    text : str

      Text to display.

    parent : QWidget, optional

      Parent widget.  Default is None.

    """

    def __init__(self, text='', parent=None):
        super().__init__()

        if parent:
            color = parent.palette().background().color()
        else:
            color = QtGui.QColor(239, 239, 239)  # the default light gray

        p =  self.viewport().palette()
        p.setColor(self.viewport().backgroundRole(), color)
        self.viewport().setPalette(p)

        self.document().setDocumentMargin(0)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setReadOnly(True)

        # NOTE Widget height isn't updated auto changed on font
        # change.  This prevents the widget from resizing as might be
        # expected when compared to a QLabel.
        font_metrics = QtGui.QFontMetrics(self.font())
        height = font_metrics.height() + (self.frameWidth()) * 2
        self.setFixedHeight(height)
