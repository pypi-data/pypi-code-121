from trame_client.widgets.core import AbstractElement
from . import module


class HtmlElement(AbstractElement):
    def __init__(self, _elem_name, children=None, **kwargs):
        super().__init__(_elem_name, children, **kwargs)
        if self.server:
            self.server.enable_module(module)


class XaiImageOverlay(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-image-overlay",
            **kwargs,
        )
        self._attr_names += [
            "id",
            "scale",
            "data",
            ("color_map", "dataToColor"),
            "overlay",
            "weights",
            ("pointer_location", "pointerLocation"),
            ("show_ij", "showIJ"),
            "crop",
        ]
        self._event_names += [
            "hover",
            "exit",
            "enter",
        ]


class XaiFullPipeline(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-full-pipeline",
            **kwargs,
        )
        self._attr_names += [
            "pipeline",
            "labels",
        ]
        self._event_names += ["click"]


class XaiImage(HtmlElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-image",
            **kwargs,
        )
        self._attr_names += [
            "config",
            "scale",
            "size",
            "values",
            "convert",
            "rgb",
            "alpha",
        ]
        self._event_names += [
            "exit",
        ]
