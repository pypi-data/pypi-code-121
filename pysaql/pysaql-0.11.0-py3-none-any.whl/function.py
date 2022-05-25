"""Contains core function definitions"""

from typing import Any, Optional, Sequence, Union

from .scalar import Scalar
from .util import stringify


class Function(Scalar):
    """Base function definition"""

    _args: Sequence[Any]
    _name: Optional[str] = None

    def __init__(self, *args: Any) -> None:
        """Initializer that accepts any number of arguments"""
        super().__init__()
        self._args = args

    def to_string(self) -> str:
        """Cast the function to a string"""
        args = [stringify(arg) for arg in self._args if arg is not None]
        name = self._name or self.__class__.__name__
        return f"{name}({', '.join(args)})"


class NullaryFunction(Function):
    """Base function definition that takes no arguments"""

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()


class coalesce(Function):
    """Get the first non-null value from a list of parameters

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_coalesce.htm
    """

    pass


class concat(Function):
    """Concatenate strings together with a delimiter"""

    def __init__(self, *args: Union[Scalar, str], delimiter: str = "-") -> None:
        """Initializer

        Args:
            delimiter: Delimiter string. Defaults to "-".

        """
        super().__init__(*args)
        self.delimiter = delimiter

    def to_string(self) -> str:
        """Cast the function to a string"""
        args = [stringify(arg) for arg in self._args if arg is not None]
        delimiter = f" + {stringify(self.delimiter)} + " if self.delimiter else " + "
        return delimiter.join(args)


class abs_(Function):
    """Get the absolute value of a number

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_abs.htm
    """

    _name = "abs"

    def __init__(self, value: Scalar) -> None:
        """Initializer

        Args:
            value: Number for which to get the absolute value

        """
        super().__init__(value)


class ceil(Function):
    """Returns the nearest integer of equal or greater value to n

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_ceil.htm
    """

    def __init__(self, value: Scalar) -> None:
        """Initializer

        Args:
            value: Number for which to get ceiling

        """
        super().__init__(value)


class floor(Function):
    """Returns the nearest integer of equal or lesser value to n

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_floor.htm
    """

    def __init__(self, value: Scalar) -> None:
        """Initializer

        Args:
            value: Number for which to get the floor

        """
        super().__init__(value)


class power(Function):
    """Returns m raised to the nth power

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_power.htm
    """

    def __init__(self, m: Scalar, n: int) -> None:
        """Initializer

        Args:
            m: Number to raise to the exponent
            n: Exponent

        """
        super().__init__(m, n)


class round_(Function):
    """Returns the value of n rounded to m decimal places

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_round.htm
    """

    _name = "round"

    def __init__(self, n: Scalar, m: int) -> None:
        """Initializer

        Args:
            n: Number to round
            m: Number of decimal places

        """
        super().__init__(n, m)


class sign(Function):
    """Returns sign of the number (-1, 0, 1)

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_sign.htm
    """

    def __init__(self, value: Scalar) -> None:
        """Returns sign of the number (-1, 0, 1)

        Args:
            value: Number to determine the sign

        """
        super().__init__(value)


class trunc(Function):
    """Returns the value of the numeric expression n truncated to m decimal places

    See: https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_saql.meta/bi_dev_guide_saql/bi_saql_functions_math_trunc.htm
    """

    def __init__(self, n: Scalar, m: int) -> None:
        """Initializer

        Args:
            n: Number to truncate
            m: Number of decimal places

        """
        super().__init__(n, m)
