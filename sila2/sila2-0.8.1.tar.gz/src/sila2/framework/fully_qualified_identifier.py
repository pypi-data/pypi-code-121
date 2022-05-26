import re

from sila2.framework.utils import FullyQualifiedIdentifierRegex


class FullyQualifiedIdentifier(str):
    """
    String class with case-insensitive comparison operations

    Examples
    --------
    >>> original_id = FullyQualifiedIdentifier("org.silastandard/core/SiLAService/v1")
    >>> lowercase_id = FullyQualifiedIdentifier("org.silastandard/core/silaservice/v1")
    >>> original_id == lowercase_id
    True
    """

    def __eq__(self, other):
        if isinstance(other, str):
            return self.lower() == other.lower()

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __hash__(self):
        return super().lower().__hash__()


class CheckedFullyQualifiedIdentifier(FullyQualifiedIdentifier):
    def __init__(self, identifier: str, check_regex: str) -> None:
        if not re.match(check_regex, identifier):
            raise ValueError(f"Invalid identifier: {identifier!r} does not match {check_regex!r} (case-insensitive)")


class FullyQualifiedMetadataIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.MetadataIdentifier)


class FullyQualifiedFeatureIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.FeatureIdentifier)


class FullyQualifiedCommandIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.CommandIdentifier)


class FullyQualifiedCommandParameterIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.CommandParameterIdentifier)


class FullyQualifiedCommandResponseIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.CommandResponseIdentifier)


class FullyQualifiedIntermediateCommandResponseIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.IntermediateCommandResponseIdentifier)


class FullyQualifiedDefinedExecutionErrorIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.DefinedExecutionErrorIdentifier)


class FullyQualifiedPropertyIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.PropertyIdentifier)


class FullyQualifiedDataTypeIdentifier(CheckedFullyQualifiedIdentifier):
    def __init__(self, identifier: str) -> None:
        super().__init__(identifier, FullyQualifiedIdentifierRegex.DataTypeIdentifier)
