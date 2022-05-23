from typing import Union

from lumipy.query.expression.column.column_base import BaseColumnExpression
from ...column_op.binary_op import (
    Trim, Like, Glob, NotLike, NotGlob, Regexp, NotRegexp,
    StringConcat, StrFilter, RightStr, LeftStr,
    Replicate, Pad,
)
from ...column_op.ternary_op import StrReplace, Substr, Index
from ...column_op.unary_op import (
    Len, LowerCase, UpperCase, Soundex, Unicode, Reverse, Proper, ToDate
)


class StringColumnFunctionAccessor:
    """StringColumnFunctionAccessor contains a collection of string functions that act on a column such like or glob.

    This and the other accessor classes behave like a namespace and keep the different column methods organised.

    They are presented as methods on an accessor attribute in each column class inheritor instance analogous to the
    string and datetime accessor methods in pandas, e.g
    https://pandas.pydata.org/pandas-docs/stable/reference/series.html#api-series-str

    Try hitting tab to see what functions you can use.
    """

    def __init__(self, x):
        self.__x = x

    def len(self) -> Len:
        """Apply a string length (len) expression to this column expression.

        Returns:
            Len: Len instance representing this operation.
        """
        return Len(self.__x)

    def trim(self, trim_str=None, trim_type='both') -> Trim:
        """Apply a trim expression to this column expression.

        This will trim characters from the left, right or both (default = both) ends of a string.
        If no target value to trim is given the operation will trim any whitespace instead.

        Args:
            trim_str (Optional[str]): substring to trim from the string expression.
            trim_type (str): string denoting which trim type to use ('left', 'right', or 'both')

        Returns:
            Trim: Trim instance representing this expression.
        """

        trim_text = trim_str if trim_str is not None else ''

        if trim_type.lower() == 'both':
            return Trim(self.__x, trim_text, '')
        elif trim_type.lower() == 'left':
            return Trim(self.__x, trim_text, 'l')
        elif trim_type.lower() == 'right':
            return Trim(self.__x, trim_text, 'r')
        else:
            raise ValueError(
                f"Invalid trim type '{trim_type}'. Must be one of 'right', 'left' or 'both'. Defaults to 'both'."
            )

    def like(self, other: str) -> Like:
        """Apply a 'like' condition expression to this expression (sql = '[col] like '%example%')

        The like operation is for case-insensitive pattern matching in strings where you're looking for a value located
        somewhere in the string. There are two wildcards: '%' which matches and sequence of characters and '_' which
        matches any single character.

        This expression and the argument to like must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Like: the Like expression object that represents this operation.
        """
        return Like(self.__x, other)

    def not_like(self, other: str) -> NotLike:
        """Apply a 'not like' condition expression to this expression (sql = '[col] not like '%example%').

        The not like operation is the negation of case-insensitive pattern matching in strings where you're looking for
        a value located somewhere in the string. There are two wildcards: '%' which matches and sequence of characters
        and '_' which matches any single character.

        This expression and the argument to not like must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotLike: the NotLike expression object that represents this operation.

        """
        return NotLike(self.__x, other)

    def glob(self, other: str) -> Glob:
        """Apply a 'glob' condition expression to this expression (sql = '[col] glob '*example*').

        The glob operation does unix-style string pattern matching. It is case sensitive and there are two wildcards:
        '*' will match any sequence of characters '?' matches a single character.

        This expression and the argument to glob must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Glob: the Glob expression object that represents this operation.

        """
        return Glob(self.__x, other)

    def not_glob(self, other: str) -> NotGlob:
        """Apply a 'not glob' condition expression to this expression (sql = '[col] not glob '*example*').

        Negation of the glob operation that does unix-style string pattern matching. It is case sensitive and there are
        two wildcards '*' will match any sequence of characters '?' matches a single character.

        This expression and the argument to not glob must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotGlob: the NotGlob expression object that represents this operation.

        """
        return NotGlob(self.__x, other)

    def regexp(self, other) -> Regexp:
        """Apply a 'regexp' condition expression to this expression (sql = '[col] regexp 'example[0-9A-Za-z]*$').

        The regexp operation checks whether a regular expression finds a match in the input string. It is case sensitive.

        This expression and the argument to regexp must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Regexp : the Regexp expression object that represents this operation.

        """
        return Regexp(self.__x, other)

    def not_regexp(self, other) -> NotRegexp:
        """Apply a 'not regexp' condition expression to this expression (sql = '[col] not regexp 'example[0-9A-Za-z]*$').

        Negation of the regexp operation that checks whether a regular expression finds a match in the input string. It is case sensitive.

        This expression and the argument to not regexp must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotRegexp : the NotRegexp expression object that represents this operation.

        """
        return NotRegexp(self.__x, other)

    def concat(self, other: Union[str, BaseColumnExpression], where: str = 'end') -> StringConcat:
        """Concatenate this column expression with another (sql = 'x | y'). Only valid for expressions
        that resolve to Text SQL value type.

        Args:
            other (Union[str, BaseSqlExpression]): other expression that resolves to a column of SQL Text values.
            where (str): where to concatente the str: "start" or "end" (defaults to "end").
        Returns:
            StringConcat: expression that represents the string concat of this column and other.
        """
        if where.lower() == 'end':
            return StringConcat(self.__x, other)
        elif where.lower() == 'start':
            return StringConcat(other, self.__x)
        else:
            raise ValueError(f"Invalid input for the where arg: {where}. Must be 'start' or 'end'.")

    def replace(self, target: Union[str, BaseColumnExpression], substitute: Union[str, BaseColumnExpression]) -> StrReplace:
        """Apply a replace expression to this column expression.

        Will swap all occurrences of the substring with the supplied replacement value.

        Args:
            target (Union[str, BaseColumnExpression]): target value to replace - can a string literal or column expression.
            substitute (Union[str, BaseColumnExpression]): value to replace with - can be string literal or column expression.

        Returns:
            StrReplace: StrReplace instance representing the replace expression applied to this column expression.
        """
        return StrReplace(self.__x, target, substitute)

    def lower(self) -> LowerCase:
        """Apply a lower expression to this column expression.

        Lower will convert a text value to all lower case.

        Returns:
            LowerCase: LowerCase instance representing the lower expression applied to this column expression.
        """
        return LowerCase(self.__x)

    def upper(self) -> UpperCase:
        """Apply an upper expression to this column expression.

        Upper will convert a text value to all upper case.

        Returns:
            UpperCase: UpperCase instance representing the lower expression applied to this column expression.
        """
        return UpperCase(self.__x)

    def soundex(self) -> Soundex:
        """Apply a soundex expression to this column expression.

        Soundex returns an English phonetic representation of a given text value.

        Returns:
            Soundex: Soundex instance representing the soundex expression applied to this column expression.
        """
        return Soundex(self.__x)

    def substr(self, start_ind: Union[int, BaseColumnExpression], length: Union[int, BaseColumnExpression] = 1) -> Substr:
        """Apply a substr expression to this column expression.

        Gets a substring of a given length starting at a given index starting at 1. Index and length can be negative,
        this denotes indexing/length from the end of the string.

        Args:
            start_ind (Union[int, BaseColumnExpression]): starting index of the substring.
            length (Union[int, BaseColumnExpression]): length of the substring (default = 1).

        Returns:
            Substr: Substr instance representing a substr expression to this column expression.
        """
        if isinstance(start_ind, int) and start_ind == 0:
            raise ValueError(
                f'Invalid input for start_ind: 0. '
                f'SQL substring index must be a positive non-zero int (indexing from string start) or negative '
                f'(indexing backward from string end).'
            )

        return Substr(self.__x, start_ind, length)

    def unicode(self) -> Unicode:
        """Apply a unicode expression to this column expression.

        Unicode SQL function returns the unicode int value for the first character in a string.

        Returns:
            Unicode: Unicode instance representing a unicode expression applied to this column expression.
        """
        return Unicode(self.__x)

    def replicate(self, times: Union[int, BaseColumnExpression]) -> Replicate:
        """Apply a replicate expression to this column expression.

        Replicate will return a string value repeated a give number of times. For example replicate('ABC', 3) will give
        'ABCABCABC.

        Args:
            times Union[int, BaseColumnExpression]: number of times to repeat the string.

        Returns:
            Replicate: Replicate instance the represents the expression applied to this column expression.
        """
        return Replicate(self.__x, times)

    def reverse(self) -> Reverse:
        """Apply a reverse expression to this column expression.

        Reverse will return the string with the characters in reverse order.

        Returns:
            Reverse: Reverse instance representing the reverse expression applied to this column expression.
        """
        return Reverse(self.__x)

    def left_str(self, n_char: Union[int, BaseColumnExpression]) -> LeftStr:
        """Apply a leftstr expression to this column expression.

        Leftstr will get the substring consisting of the first n-many character from the left.

        Args:
            n_char (Union[int, BaseColumnExpression]): number of characters to take from the left.

        Returns:
            LeftStr: LeftStr instance representing a leftstr expression applied to this column expression.
        """
        if isinstance(n_char, int) and n_char < 1:
            raise ValueError("n_char must be positive and non-zero.")
        return LeftStr(self.__x, n_char)

    def right_str(self, n_char: Union[int, BaseColumnExpression]) -> RightStr:
        """Apply a rightstr expression to this column expression.

        Leftstr will get the substring consisting of the first n-many character from the right.

        Args:
            n_char (Union[int, BaseColumnExpression]): number of characters to take from the right.

        Returns:
            RightStr: RightStr instance representing a rightstr expression applied to this column expression.
        """
        if isinstance(n_char, int) and n_char < 1:
            raise ValueError("n_char must be positive and non-zero.")
        return RightStr(self.__x, n_char)

    def pad(self, length: Union[int, BaseColumnExpression], pad_type: Union[str, BaseColumnExpression]) -> Pad:
        """Apply a pad expression to this column expression.

        Pads out a string with whitespace so it reaches a given length.

        Args:
            length (Union[int, BaseColumnExpression]): target length of padded string.
            pad_type (Union[str, BaseColumnExpression]): type of pad operation: 'right', 'left' or 'center'.

        Returns:
            Pad: Pad instance representing the expression applied to this column expression.
        """
        if pad_type.lower() == 'right':
            return Pad(self.__x, length, 'r')
        elif pad_type.lower() == 'left':
            return Pad(self.__x, length, 'l')
        elif pad_type.lower() == 'center':
            return Pad(self.__x, length, 'c')
        else:
            raise ValueError(f'Unrecognised pad type: {pad_type}')

    def filter(self, filter_str: Union[str, BaseColumnExpression]) -> StrFilter:
        """Apply a strfilter expression to this column expression.

        Strfilter will filter a string for the characters that exist in another string.

        Args:
            filter_str (Union[str, BaseColumnExpression]): string value or text valued expression containing the
            characters to filter for.

        Returns:
            Strfilter: Strfilter instance representing the expression applied to this column expression.
        """
        return StrFilter(self.__x, filter_str)

    def index(self, chars: str, start_position: int = 0) -> Index:
        """Apply an index (charindex) expression to this column expression.

        Index (charindex) will find the index of the first occurrence of a substring after a specified starting position.

        Args:
            chars Union[str, BaseColumnExpression]: substring to locate.
            start_position Union[str, BaseColumnExpression]: starting position of the search (defaults to 0)

        Returns:
            Index: Index instance representing the expression applied to this column expression.
        """
        return Index(chars, self.__x, start_position)

    def proper(self) -> Proper:
        """Apply a proper expression to this column expression.

        Proper will capitalize each word in a string delimited by spaces so
            'arthur morgan'
        becomes
            'Arthur Morgan'

        Returns:
            Proper: Proper instance representing the expression applied to this column expression.
        """
        return Proper(self.__x)

    def contains(self, sub_str: Union[str, BaseColumnExpression], case_sensitive: bool = False) -> Union[Like, Glob]:
        """Test whether a string-valued column expression contains a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if not isinstance(case_sensitive, bool):
            raise TypeError(f"The case_sensitive arg to contains method must be a bool. "
                            f"Was {type(case_sensitive).__name__}")

        if case_sensitive and isinstance(sub_str, str):
            return self.__x.str.glob(f"*{sub_str}*")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('*').str.concat('*', where='start')
            return self.__x.str.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.__x.str.like(f"%{sub_str}%")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('%').str.concat('%', where='start')
            return self.__x.str.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def startswith(self, sub_str: Union[str, BaseColumnExpression], case_sensitive: bool = False) -> Union[Glob, Like]:
        """Test whether a string-valued column expression starts with a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if case_sensitive and isinstance(sub_str, str):
            return self.__x.str.glob(f"{sub_str}*")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('*')
            return self.__x.str.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.__x.str.like(f"{sub_str}%")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('%')
            return self.__x.str.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def endswith(self, sub_str: Union[str, BaseColumnExpression], case_sensitive: bool = False) -> Union[Glob, Like]:
        """Test whether a string-valued column expression ends with a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if case_sensitive and isinstance(sub_str, str):
            return self.__x.str.glob(f"*{sub_str}")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('*', where='start')
            return self.__x.str.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.__x.str.like(f"%{sub_str}")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.str.concat('%', where='start')
            return self.__x.str.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def to_date(self) -> ToDate:
        """Apply a To_Date expression to this column expression.

        To_Date will take a string value to a datetime value.

        Returns:
            ToDate: ToDate instance representing the expression applied to this column.
        """
        return ToDate(self.__x)
