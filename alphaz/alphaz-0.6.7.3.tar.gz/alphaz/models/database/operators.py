from enum import Enum

class Operators(Enum):
    EQUAL = "=="
    ASIGN = "="
    DIFFERENT = "!="
    NOT = "!"
    LIKE = "like"
    NOT_LIKE = "notlike"
    ILIKE = "ilike"
    NOT_ILIKE = "notlike"
    SUPERIOR = ">"
    INFERIOR = "<"
    SUPERIOR_OR_EQUAL = ">="
    INFERIOR_OR_EQUAL = "<="
    IN = "in"
    NOT_IN = "notin"
    HAS = "has"
    ANY = "any"
    BETWEEN = "<>"
    BETWEEN_OR_EQUAL = "<==>"

    def equals(self, val):
        if type(val) == str:
            return self.value == val
        elif type(val) == Operators:
            return self.value == val.value
        return False