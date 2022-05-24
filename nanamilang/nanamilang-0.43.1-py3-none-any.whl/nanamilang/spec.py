"""NanamiLang Spec Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import (
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF,
    ASSERT_COLL_LENGTH_IS_EVEN,
    ASSERT_COLL_LENGTH_EQUALS_TO,
    ASSERT_COLLECTION_NOT_EMPTY, ASSERT_COLL_LENGTH_VARIANTS
)


class Spec:
    """NanamiLang Spec"""
    ArityIs: str = 'ArityIs'
    ArityEven: str = 'ArityEven'
    ArityAtLeast: str = 'ArityAtLeast'
    ArityVariants: str = 'ArityVariants'
    ArityAtLeastOne: str = 'ArityAtLeastOne'
    EachArgumentTypeIs: str = 'EachArgumentTypeIs'
    ArgumentsTypeChainVariants: str = 'ArgumentsTypeChainVariants'

    @staticmethod
    def validate(label: str, arguments: tuple, rules: list):
        """Validates function or macro arguments using certain rules"""

        # We require 'rules' to be an instance of a Python 3 list
        # And each 'rule' to be an instance of a Python 3 list as well.
        assert isinstance(rules, list), 'Spec.validate(): rules arg needs to be a list'
        for rule in rules:
            assert isinstance(rule, list), 'Spec.validate(): each rule needs to be a list'
            if len(rule) == 2:
                rule_key, single_or_multiple_rule_value = rule
            else:
                rule_key, single_or_multiple_rule_value = rule + [None]
            if rule_key == Spec.ArityIs:
                # I.e.: [ArityIs, <int>]; thus we do require single value
                ASSERT_COLL_LENGTH_EQUALS_TO(
                    arguments, single_or_multiple_rule_value,
                    f'{label}: '
                    f'invalid arity, form(s)/argument(s) possible: {single_or_multiple_rule_value}'
                )
            elif rule_key == Spec.ArityEven:
                # I.e.: [ArityEven]; thus we do not require any rule value here, single or multiple
                ASSERT_COLL_LENGTH_IS_EVEN(
                    arguments, f'{label}: invalid arity, number of form(s)/argument(s) must be even')
                # I.e.: [ArityVariants, [<int>, <int>, ..]]; require list of Python 3 integer numbers
            elif rule_key == Spec.ArityAtLeast:
                # I.e.: [ArityAtLeast, <int>]; single argument required, it needs to be type of <int>
                assert len(arguments) >= single_or_multiple_rule_value, (
                    f'{label}: invalid arity, '
                    f'minimum number of form(s)/argument(s) possible {single_or_multiple_rule_value}'
                )
            elif rule_key == Spec.ArityVariants:
                formatted = {', '.join(map(str, single_or_multiple_rule_value))}
                ASSERT_COLL_LENGTH_VARIANTS(
                    arguments,
                    single_or_multiple_rule_value,
                    f'{label}: invalid arity, numbers of form(s)/argument(s) possible: {formatted}.')
            if rule_key == Spec.ArityAtLeastOne:
                # I.e.: [ArityAtLeastOne]; thus we don't require any rule value here, single/multiple
                ASSERT_COLLECTION_NOT_EMPTY(
                    arguments, f'{label}: invalid arity, at least one form or argument was expected')
            elif rule_key == Spec.EachArgumentTypeIs:
                # I.e.: [EachArgumentTypeIs, <datatypes.Type>]; thus we require a NanamiLang datatype
                dt_name = single_or_multiple_rule_value.name
                # HINT: by passing datatypes.Base here, you mean that function can take any data type
                ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
                    arguments,
                    single_or_multiple_rule_value, f'{label}: can only accept {dt_name} argument(s)')
            elif rule_key == Spec.ArgumentsTypeChainVariants:
                # I.e.: [ArgumentsTypeChainVariants, [[datatypes.Type, datatypes.TypeN], [...], ...]]
                if arguments:
                    for chain in filter(lambda c: len(c) == len(arguments),
                                        single_or_multiple_rule_value):
                        if len(tuple(filter(lambda c: issubclass(arguments[c[0]].__class__, (c[1],)),
                                            enumerate(chain)))) == len(arguments):
                            return
                    raise AssertionError(f"{label}: the arguments type chain does not conform specs")
