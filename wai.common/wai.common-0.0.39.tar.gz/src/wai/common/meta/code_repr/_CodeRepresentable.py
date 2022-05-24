from ._typing import CodeRepresentation


class CodeRepresentable:
    """
    Base class for types that can represent themselves as a Python expression which,
    when evaluated, evaluates to a copy of themselves.
    """
    def code_repr(self) -> CodeRepresentation:
        """
        Gets the code representation of the object.

        :return:                            The code representation.
        :raise CodeRepresentationError:     If the object is not code-representable.
        """
        raise NotImplementedError(CodeRepresentable.code_repr.__qualname__)
