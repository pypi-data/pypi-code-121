# AristaFlow REST Libraries
from af_remote_html_runtime_manager.models.gui_context import GuiContext


class HtmlGuiContext(object):
    """
    Small wrapper given direct access to Remote HTML GUI Context attributes.
    """

    _gui_context: GuiContext = None

    def __init__(self, gui_context: GuiContext):
        self._gui_context = gui_context

    @property
    def gui_context(self) -> GuiContext:
        return self._gui_context

    @property
    def url(self) -> str:
        return self._gui_context.gui_context_attributes["URLContext.URL"]
