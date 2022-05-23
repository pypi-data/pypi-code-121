import regex as re

class Regex():
    def __init__(self, label, pattern, flag=0):
        self.label=label
        self.pattern=pattern
        if isinstance(flag, str):
            self.flag=eval(flag)
        else:
            self.flag=flag

    @property
    def regex(self):
        if isinstance(self.pattern, str):
            self.pattern=re.compile(self.pattern, self.flag)
        return self.pattern