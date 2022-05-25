from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

from urllib.parse import quote


class Condition(ABC):
    """
    Class which combines all conditions that can be specified in a query.
    """

    @abstractmethod
    def __call__(self, do_url_escape: bool) -> str:
        """ :return:  The compiled output of the condition """
        ...

    @staticmethod
    def create(*args: 'Condition', exclude_empty: bool = True, do_url_escape: bool = True) -> str:
        """
        :param args:                The set of Conditions that is to be combined .

        :param exclude_empty:       If true, conditions that are empty (according to the Condition's implementation)
                                    are removed from the query.

        :param do_url_escape:       Escape variable comparator assignment characters in url if necessary.

        :return:                    The joined compiled output of the arguments.
        """
        list_conditions: List[Conditions] = []
        list_condition: List[Condition] = []

        for arg in args:
            if arg is not None and (not exclude_empty or arg):
                (list_conditions if isinstance(arg, Conditions) else list_condition).append(arg)

        if len(list_condition):
            list_conditions.append(Conditions(*list_condition))

        return '&'.join((c(do_url_escape=do_url_escape) for c in list_conditions))


class Conditions(Condition):
    """ Combination of multiple conditions. """

    def __init__(self, *args: Condition) -> None: self.args: Tuple[(Condition,) * len(args)] = (*args,)

    def __call__(self, do_url_escape: bool) -> str: return '&'.join(a(do_url_escape) for a in self.args if a)

    def __bool__(self) -> bool: return any((a for a in self.args))


class Comparator(Condition):
    """ Condition that expresses a comparison of a variable and a value. """

    def __init__(self, var: str, val: Any, attribute: Any = None, prefix: str = '', infix: str = ',',
                 suffix: str = ')') -> None:
        self.var: str = var
        self.val: Optional[str] = val if val is None else str(val)
        self.attribute: Optional[str] = None if attribute is None else str(attribute)
        self.prefix: str = prefix
        self.infix: str = infix
        self.suffix: str = suffix

    def __call__(self, do_url_escape: bool) -> str:
        val, var = (self.val, self.var) if self.attribute is None else (f'{self.var}:{self.val}', self.attribute)
        val = val if not do_url_escape else quote(val)
        return ''.join([self.prefix, var, self.infix, val, self.suffix])

    def __bool__(self) -> bool: return self.val is not None


class Equal(Comparator):
    """ Checks equality between a variable and a value. The variable can be part of an attribute. """

    def __init__(self, var: str, val: Optional[Union[str, Any]], attribute: Optional[Union[str, Any]] = None) -> None:
        if attribute is None:
            super(Equal, self).__init__(var=var, val=val, infix='=', suffix='', attribute=attribute)
        else:
            super(Equal, self).__init__(var=var, val=val, prefix='eq(', attribute=attribute)


class LessThan(Comparator):
    """ Checks if a variable is less than a value. The variable can be part of an attribute. """

    def __init__(self, var: str, val: Optional[Union[str, Any]], attribute: Optional[Union[str, Any]] = None) -> None:
        super(LessThan, self).__init__(var=var, val=val, attribute=attribute, prefix='lt(')


class GreaterThan(Comparator):
    """ Checks if a variable is greater than a value. The variable can be part of an attribute. """

    def __init__(self, var: str, val: Optional[Union[str, Any]], attribute: Optional[Union[str, Any]] = None) -> None:
        super(GreaterThan, self).__init__(var=var, val=val, attribute=attribute, prefix='gt(')


class LogicalExpression(Condition):
    """ Condition that expresses a logical combination of multiple child expressions. """

    def __init__(self, op: str, *args: Condition) -> None:
        self.op = op
        self.args: Tuple[(Condition,) * len(args)] = (*args,)

    def __call__(self, do_url_escape: bool) -> str:
        return f'{self.op}(' + ','.join((a(do_url_escape=do_url_escape) for a in self.args)) + ')' \
            if len(self.args) > 1 else self.args[0](do_url_escape)


class And(LogicalExpression):
    """ Checks if all the child conditions yield true. """

    def __init__(self, arg0: Condition, *args: Condition) -> None: super(And, self).__init__('and', arg0, *args)


class Or(LogicalExpression):
    """ Checks  if any of the child conditions yield true. """

    def __init__(self, arg0: Condition, *args: Condition) -> None: super(Or, self).__init__('or', arg0, *args)
