from cleo.formatters.formatter import Formatter


class UIError:
    @property
    def pretty_error(self):
        raise NotImplementedError()

    def remove_format(self, message: str) -> str:
        return Formatter().remove_format(message)
