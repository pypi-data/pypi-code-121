import re
from .validators import normalize_str


class Pincode(str):
    """
    Type for Indian pincodes. Verifies that pincodes are all numbers, exactly 6
    characters and start with non-zero
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("string required")
        if re.fullmatch(r"^[1-9][0-9]{5}$", value) is None:
            raise ValueError("invalid pincode format")

        return cls(value)


class NormalizedString(str):
    """
    Type for normalizing strings by stripping and removing newline characters. The type
    also checks the string after normalising and fails if Falsy. WARNING: using this
    type in conjunction with Field function seems to remove its validation. For now,
    only use this type directly if not using length or regex validation with Field(...)
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("string required")

        return cls(normalize_str(value))
