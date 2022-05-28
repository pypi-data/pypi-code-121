class JudiFilter:
    def __init__(self, accepted=None, rejected=None):
        self.buffer = ""
        self.depth = 0
        self.accepted = accepted
        self.rejected = rejected

    def reset(self):
        self.buffer = ""
        self.depth = 0

    def insert_char(self, c):
        if c == "{":
            self.depth += 1
        if self.depth > 0:
            self.buffer += c
            if self.accepted:
                self.accepted(c)
        if c == "}" and self.depth > 0:
            self.depth -= 1

        if len(self.buffer) == 0:
            if self.rejected:
                self.rejected(c)

        return self.completed()

    def completed(self):
        if (self.depth == 0) and (len(self.buffer) > 0):
            return True
        return False