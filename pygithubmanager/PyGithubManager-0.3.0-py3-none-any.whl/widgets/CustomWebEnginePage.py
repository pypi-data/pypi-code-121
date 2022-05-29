from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView


class CustomWebEnginePage(QWebEnginePage):
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        """
        Override the default navigation behavior.

        Parameters
        ----------
        url : str
            The URL to navigate to.
        _type : QWebEnginePage.NavigationType
            The type of navigation.
        isMainFrame : bool
            Whether the navigation is for the main frame.

        Returns
        -------
        bool
            Whether the navigation should be accepted.
        """
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            w = QWebEngineView()
            w.setUrl(url)
            w.show()

            self.external_windows.append(w)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)
