from mfire.settings import get_logger
from mfire.text.template import Template


# Logging
LOGGER = get_logger(name="base_builder.mod", bind="base_builder")


class BaseBuilder:
    """ BaseBuilder qui doit construire le texte de synthèse
    """

    def __init__(self) -> None:
        self._text = ""
        self.reduction = None

    @property
    def text(self) -> Template:
        """synthesis: synthesis being built and processed by the synthesis builder

        Returns:
            Template: synthesis (with a Template type instead of a simple string
                in order to profit from the formatting advantages of the Template
                type.)
        """
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = None
        if isinstance(text, str):
            self._text = Template(text)

    def reset(self) -> None:
        """reset: resets the synthesis
        """
        self._text = None
        self.reduction = None

    def compute(self, reduction: dict) -> None:
        self.reset()
        self.reduction = reduction
