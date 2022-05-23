from .._OptionHandler import OptionHandler
from ..options import Option
from ._OptionContext import OptionContext


class OptionInstanceContext(OptionContext):
    """
    Class which handles accessing an option in the context of a
    specific option handler instance.
    """
    def __init__(self, option: Option, context: OptionHandler):
        # The option must be owned by the instance's type (or super-type)
        if not isinstance(context, option.owner):
            raise TypeError("Context instance does not have access to this option")

        super().__init__(option, context)
