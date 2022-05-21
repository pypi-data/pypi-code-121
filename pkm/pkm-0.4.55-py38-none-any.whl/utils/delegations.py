from abc import ABC, ABCMeta
from typing import Type, TypeVar, Union, Callable, Tuple, Dict

from pkm.utils.commons import UnsupportedOperationException

_T = TypeVar("_T")
_U = TypeVar("_U")

_ABSTRACT_METHODS_KEY = '__abstractmethods__'


def delegate(type_: Type[_T], attr: str) -> Callable[[Type[_U]], Type[Union[_T, _U]]]:
    return delegate_all((type_, attr))


def delegate_all(*reqs: Tuple[Type[_T], str]) -> Callable[[Type[_U]], Type[Union[_T, _U]]]:
    method_to_attr: Dict[str, str] = {}

    for type_, attr in reqs:
        if not hasattr(type_, '__dict__'):
            raise UnsupportedOperationException(
                f"cannot create delegations using classes that has no __dict__ ({type_})")

        method_to_attr.update({
            method: attr
            for method in type_.__dict__[_ABSTRACT_METHODS_KEY]
        })

    def delegate_(cls: Type[_U]) -> Type[Union[_T, _U]]:

        if not hasattr(cls, '__dict__'):
            raise UnsupportedOperationException("cannot create delegations for classes that has no __dict__")

        if _ABSTRACT_METHODS_KEY not in cls.__dict__:
            # no delegation is needed - all methods are already implemented..
            return cls

        # first copy the previous dict but without the abstract methods, we are going to implement them in a second
        new_dict = {
            attr_k: attr_v
            for attr_k, attr_v in cls.__dict__.items()
            if attr_k not in (_ABSTRACT_METHODS_KEY, '_abc_impl')
        }

        # now 'implement' the abstract methods using the type requirements
        abstract_methods = []
        for method in cls.__dict__[_ABSTRACT_METHODS_KEY]:
            if attr_m := method_to_attr.get(method):

                def _create(attr, method): # noqa
                    def do_delegation(self, *args, **kwargs):
                        return getattr(getattr(self, attr), method)(*args, **kwargs)

                    new_dict[method] = do_delegation

                _create(attr_m, method)
            else:
                abstract_methods.append(method)

        if abstract_methods:
            # we are not creating a concrete class so we should use abcmeta to create it
            return ABCMeta(cls.__name__, cls.__bases__, new_dict)

        # we are creating a concrete class
        return type(cls.__name__, tuple(b for b in cls.__bases__ if b is not ABC), new_dict)

    return delegate_
