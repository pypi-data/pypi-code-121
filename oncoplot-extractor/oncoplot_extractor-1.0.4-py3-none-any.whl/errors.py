"""General Error classes for OncoPlot Extractor"""


class OncoPlotExtractorError(Exception):
    """Base class for all OncoPlot Extractor errors."""

    def __init__(self, msg) -> None:
        super().__init__(msg)


class OncoPlotPlotterError(Exception):
    """Base class for all OncoPlot Plotter errors."""

    def __init__(self, msg) -> None:
        super().__init__(msg)
