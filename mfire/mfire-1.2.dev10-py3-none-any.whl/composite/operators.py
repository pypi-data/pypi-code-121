"""
    Module d'interprétation de la configuration, module Operator
"""
from __future__ import annotations

import operator
from enum import Enum
from typing import Callable, List, Any


import xarray as xr

from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="composite.operators.mod", bind="composite.operators")


def or_operator(first_field: Any, second_field: Any) -> bool:
    """
       Prend le maximum des champs présents (en chaque point)
    """
    if first_field.count() == second_field.count():
        res = operator.or_(first_field, second_field)
    else:
        LOGGER.warning("On passe par le max pour simuler le or")
        dfirst = first_field.expand_dims("place").assign_coords(place=[1])
        dsecond = second_field.expand_dims("place").assign_coords(place=[2])
        concat = xr.concat([dfirst, dsecond], dim="place")
        res = concat.max(dim="place")
    return res


def and_operator(first_field: Any, second_field: Any) -> bool:
    """
    On ne fait rien pour l'instant.
    A voir comment on doit traiter ce cas
    """
    return operator.and_(first_field, second_field)


def is_in(val: Any, my_list: List[Any]) -> bool:
    """vérifie si un valeur val est bien contenue
    dans une liste

    Args:
        val : valeur d'entrée
        my_list : liste de référence

    Returns:
        bool
    """
    return my_list.isin(val)


class Operator(str, Enum):
    """ Objet de type opérateur qui traduit les données de la
    configuration en opérateur python ou bien fonctions spécifique
    """

    def __new__(cls, value: str, oper: Callable) -> Operator:
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.oper = oper
        return obj

    def __call__(self, v1: object, v2: object) -> bool:
        return self.oper(v1, v2)

    @classmethod
    def apply(cls, operators: List[Operator], elements: List[Any]) -> bool:
        """Perform the following operation :
        operators[n](element[n+1], operators[n-1](evt[n],... op[0](evt[1],evt[0])...))

        Args:
            operators (List[Operator]): Operators to apply
            elements (List[Any]): List of elements to apply given operators

        Raises:
            ValueError: Raised if len(operators) != len(elements)

        Returns:
            bool: Result of the operation
        """

        if len(operators) + 1 != len(elements):
            raise ValueError(
                "Length of operands and operators are not good. "
                f"Operand is {len(elements)} and Operator is {len(operators)}. "
                f"Operand should be of length {len(operators) + 1}."
            )
        result = elements[0]
        for op, element in zip(operators, elements[1:]):
            result = cls(op)(element, result)
        return result


class LogicalOperator(Operator):
    """Opérateur logique AND et OR

    Inheritance : Operator
    """

    AND = ("and", and_operator)
    OR = ("or", or_operator)


class ComparisonOperator(Operator):
    """objet opérateur de comparaison

    Inheritance : Operator
    """

    SUP = ("sup" or ">", operator.gt)
    SUPEGAL = ("supegal" or ">=", operator.ge)
    INF = ("inf" or "<", operator.lt)
    INFEGAL = ("infegal" or "<=", operator.le)
    EGAL = ("egal" or "==", operator.eq)
    DIF = ("dif" or "!=", operator.ne)
    ISIN = ("isin", (lambda da, l: da.isin(l)))
