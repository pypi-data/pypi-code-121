
from .namespace import Namespace


class FormattedNamespace(Namespace):

    def __init__(self, string):
        super(FormattedNamespace, self).__init__()
        self.obj = string
