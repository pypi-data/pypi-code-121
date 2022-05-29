from PySide6.QtWidgets import QLabel


class HyperlinkLabel(QLabel):
    def __init__(self, parent=None):
        """
        Label with a clickable link.

        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        super().__init__()

        self.link_template = '<a href={0}>{1}</a>'

        self.setOpenExternalLinks(True)
        self.setParent(parent)

    def setText(self, arg__1: str) -> None:
        """
        Set the text of the label.
        Parameters
        ----------
        arg__1 : str
            Text to set.
        """
        super().setText(self.link_template.format(arg__1, arg__1))
