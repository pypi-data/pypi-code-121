class AutosplitError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        if len(self.args) > 0:
            self.message = self.args[0]
        else:
            self.message = "Default message"


class Incoherence(AutosplitError):
    pass


class ParseError(AutosplitError):
    pass
