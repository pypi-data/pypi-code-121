from typing import Any, Generic, Optional, Callable, Type, TypeVar, List, Tuple, Dict, ContextManager, cast, get_args, get_origin
from typing_extensions import ParamSpec, Literal
from functools import partial, update_wrapper
from inspect import Parameter, signature as get_signature, Signature
from contextvars import ContextVar
from dataclasses import dataclass, replace
from contextlib import contextmanager, suppress
from collections import abc
from threading import Lock


P = ParamSpec('P')
T = TypeVar('T')


void = object()


def inject(name: Optional[str] = None, tp: Type[Any] = None) -> Any:
    return Requirement(name, tp, 'injector', void)


@dataclass(frozen=True)
class Requirement(Generic[T]):
    name: str
    tp: Type[T]
    location: str
    default: T


class _Definition(Generic[T]):
    def __init__(self, signature: Signature, factory: Callable[..., ContextManager], scope: str, name: str):
        self.signature = signature
        self.factory = factory
        self.scope = scope
        self.name = name

        self.lock = Lock()

    def enter(self):
        raise NotImplementedError()

    def exit(self, error_type: Type[Exception], error: Exception, tb: Any):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    @property
    def tp(self):
        tp = get_origin(self.signature.return_annotation)

        if not issubclass(tp, abc.Iterator):
            raise TypeError()

        arg, = get_args(self.signature.return_annotation)

        return arg


class _InstanceDefinition(_Definition):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._instance: Any = None
        self._manager: ContextManager[Any, Any, Any] = None

    def enter(self):
        manager = self.factory()

        self._manager = manager
        self._instance = manager.__enter__()

    def exit(self, error_type: Type[Exception], error: Exception, tb: Any):
        if not self._manager:
            return

        self._manager.__exit__(error_type, error, tb)
        self._manager = None
        self._instance = None

    def get(self):
        return self._instance


class _ContextDefinition(_Definition):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._instance_var = ContextVar(f'instance_{self.tp.__name__}_{self.factory.__name__}', default=None)
        self._manager_var = ContextVar(f'manager_{self.tp.__name__}_{self.factory.__name__}', default=None)

    def enter(self):
        manager = self.factory()

        self._manager_var.set(manager)
        self._instance_var.set(manager.__enter__())

    def exit(self, error_type: Type[Exception], error: Exception, tb: Any):
        manager = self._manager_var.get()

        if not manager:
            return

        manager.__exit__(error_type, error, tb)

        self._manager_var.set(None)
        self._instance_var.set(None)

    def get(self):
        return self._instance_var.get()


class Injector:
    def __init__(self, plugins: Optional[List[Callable]] = None):
        self._plugins = plugins or []
        self._definitions: List[_Definition] = []

    def _get_definition(self, requirement: Requirement[T]) -> _Definition:
        for definition in self._definitions:
            if issubclass(definition.tp, requirement.tp) and (
                    definition.name is None or definition.name == requirement.name):
                return definition

    def define(self, scope: Literal['context', 'singleton'], name=None) -> Callable[[Callable[P, T]], Callable[P, T]]:
        assert scope in ['context', 'singleton']

        def definer(function: Callable[P, T]) -> Callable[P, T]:
            signature = get_signature(function)
            factory = contextmanager(function)

            if scope == 'context':
                self._definitions.append(_ContextDefinition(
                    signature=signature,
                    factory=factory,
                    scope=scope,
                    name=name,
                ))

            elif scope == 'singleton':
                self._definitions.append(_InstanceDefinition(
                    signature=signature,
                    factory=factory,
                    scope=scope,
                    name=name,
                ))

            return factory

        return definer

    def release(self, factories, error, error_type, tb):
        for definition in self._definitions:
            if not factories or definition.factory in factories:
                definition.exit(error, error_type, tb)

    @contextmanager
    def entry(self, release_factories=None):
        try:
            yield
        except Exception as error:
            self.release(release_factories, type(error), error, None)
            raise
        else:
            self.release(release_factories, None, None, None)

    def _get_from_plugin(self, requirement: Requirement[T], args=None, kwargs=None) -> T:
        for plugin in self._plugins or []:
            with suppress(LookupError):
                value = plugin(requirement, args, kwargs)

                if value:
                    return value

        if requirement.default is not void:
            return requirement.default

        raise LookupError()

    def _get(self, requirement: Requirement[T]) -> T:
        definition = self._get_definition(requirement)

        if not definition:
            raise LookupError()

        with definition.lock:
            if not definition.get():
                definition.enter()

        return cast(T, definition.get())

    def get(self, tp: Type[T], name: Optional[str] = None) -> T:
        return self._get(inject(name, tp))

    def injectable(self, function: Callable[P, T]) -> Callable[P, T]:
        return update_wrapper(_Injector(self, function), function)


class _Injector:
    def __init__(self, injector: Injector, function: Callable[P, T]):
        self._injector = injector
        self._function = function
        self._requires = []
        self._signature = get_signature(function)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        for position, parameter in enumerate(self._signature.parameters.values()):
            requirement = parameter.default

            if not isinstance(requirement, Requirement):
                continue

            requirement = replace(
                requirement,
                tp=requirement.tp or parameter.annotation,
                name=requirement.name or parameter.name,
            )

            arg = void

            if parameter.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
                with suppress(IndexError):
                    arg = args[position]

            if arg is void and parameter.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
                with suppress(KeyError):
                    arg = kwargs[parameter.name]

            if arg is void:
                try:
                    value = self._injector._get(requirement)
                except LookupError:
                    value = self._injector._get_from_plugin(requirement, args, kwargs)

                kwargs[parameter.name] = value

        return self._function(*args, **kwargs)

    def __get__(self, instance, tp) -> Callable[P, T]:
        return partial(self, instance if instance else tp)
