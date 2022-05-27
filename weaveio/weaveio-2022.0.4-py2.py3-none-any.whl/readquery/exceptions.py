class UserError(Exception):
    pass


class AmbiguousPathError(UserError):
    pass


class CardinalityError(UserError):
    pass


class AttributeNameError(UserError):
    pass


class DisjointPathError(UserError):
    pass
