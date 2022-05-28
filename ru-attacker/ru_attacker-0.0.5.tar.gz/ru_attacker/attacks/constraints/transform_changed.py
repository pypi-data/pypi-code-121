from .basic_constraint import BasicConstraint

__all__ = ["TransformChanged"]


class TransformChanged(BasicConstraint):
    def check(self, original, transformed):
        if original == transformed:
            return False
        else:
            return True
