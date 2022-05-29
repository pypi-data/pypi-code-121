from .constants import LOGGER_NAME
from .exceptions import DependencyResolutionException
from .graphs import BidirectedGraph
from .graphs.sorting import topological_sort
from .iinjectable_catalog import IInjectableCatalog
from .ilifetime_scope import ILifetimeScope, TInjectable
from .models import InjectableScopeType, LifetimeScopeOptions
from .utils import get_or_add
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Type, get_args

import inspect
import structlog

DEFAULT_OPTIONS: LifetimeScopeOptions = LifetimeScopeOptions()

SCOPE_TYPE_RANKS: Dict[InjectableScopeType, int] = {
    InjectableScopeType.TRANSIENT: 0,
    InjectableScopeType.SCOPED: 1,
    InjectableScopeType.SINGLETON: 2
}

class LifetimeScope(ILifetimeScope):
    """An injectable lifetime scope
    that manages the lifetimes of injectables
    and provides access to them."""

    def __init__(self,
                 catalog: IInjectableCatalog,
                 options: LifetimeScopeOptions = DEFAULT_OPTIONS,
                 **kwargs: Any) -> None:
        self.__catalog: IInjectableCatalog = catalog
        self.__options: LifetimeScopeOptions = options
        self.__log = structlog.get_logger(LOGGER_NAME)
        self.__instances_by_injectable: Dict[InjectableScopeType, Dict[Type[Any], Set[Any]]] = {}
        self.__parent: Optional[ILifetimeScope] = None

        if (parent := kwargs.get("parent", None)) is not None:
            if not isinstance(parent, ILifetimeScope):
                raise ValueError("The parent must be an instance of ILifetimeScope.")
            self.__parent = parent

    def resolve(self, injectable: Type[TInjectable]) -> TInjectable:
        registration = self.__catalog.get_registration_by_injectable(injectable)
        if (registration is not None
            and registration.scope == InjectableScopeType.SINGLETON
            and self.__parent is not None):
            return self.__parent.resolve(injectable)

        dependency_graph = self.__build_dependency_graph_for(injectable)
        instance = None
        for current_injectable in topological_sort(dependency_graph, injectable):
            self.__log.debug("Resolving injectable", type=current_injectable)
            instance = self.__resolve_injectable(current_injectable)
            self.__log.debug("Resolved injectable", type=current_injectable)

        if not isinstance(instance, injectable):
            raise DependencyResolutionException(
                type(instance),
                (
                    "Got an unexpected type during dependency resolution."
                    " This is likely an error in the algorithm."
                )
            )

        return instance

    def create_child_scope(self) -> ILifetimeScope:
        return LifetimeScope(self.__catalog, self.__options, parent=self)

    @staticmethod
    def __get_dependent_contracts(
        injectable: Type[Any]) -> Generator[Tuple[Type[Any], bool], None, None]:
        constructor = getattr(injectable, "__init__", None)
        if not constructor or not callable(constructor):
            raise DependencyResolutionException(injectable, "Invalid constructor.")
        signature = inspect.signature(constructor)
        for name, descriptor in signature.parameters.items():
            if name in ("self", "args", "kwargs"):
                continue
            if descriptor.annotation == inspect.Parameter.empty:
                raise DependencyResolutionException(
                    injectable,
                    f"The initializer of '{injectable}' is missing annotations."
                )
            yield LifetimeScope.__unpack_dependent_intf(descriptor.annotation)

    @staticmethod
    def __unpack_dependent_intf(contract: Type[Any]) -> Tuple[Type[Any], bool]:
        # The dependency must be either a specific contract (single instance dependency)
        # or a tuple of a single specific contract (multiple instance dependency).
        if (origin := getattr(contract, "__origin__", None)) is not None:
            if origin != tuple:
                raise DependencyResolutionException(
                    contract,
                    f"Expected a tuple, but got {origin}."
                )
            args = get_args(contract)
            if len(args) != 2 or args[-1] != Ellipsis:
                raise DependencyResolutionException(
                    contract,
                    "Expected a tuple with two arguments, the second being an ellipsis."
                )
            return (args[0], True)
        return (contract, False)

    @staticmethod
    def __is_captive_dependency(
        dependee_scope: InjectableScopeType,
        dependent_scope: InjectableScopeType) -> bool:
        ranked_scopes = sorted((dependee_scope, dependent_scope), key=lambda i: SCOPE_TYPE_RANKS[i])
        return ranked_scopes[0] != dependee_scope

    def __build_dependency_graph_for(self, injectable: Type[Any]) -> BidirectedGraph[Type[Any]]:
        graph: BidirectedGraph[Type[Any]] = BidirectedGraph()
        injectables_to_resolve: List[Type[Any]] = [injectable]
        while (len(injectables_to_resolve)) > 0:
            dependee_injectable = injectables_to_resolve.pop()
            if not graph.try_add_node(dependee_injectable):
                # This type's dependency chain has already been mapped.
                continue

            self.__log.debug("Gathering dependent contracts", dependee=dependee_injectable)
            dependent_contracts = LifetimeScope.__get_dependent_contracts(dependee_injectable)
            for dependent_contract, is_multi in dependent_contracts:
                self.__log.debug("Found dependent contract",
                               dependee=dependee_injectable,
                               dependent=dependent_contract,
                               is_multi=is_multi)
                dependent_registrations = self.__catalog.get_registrations_by_contract(
                    dependent_contract)
                if len(dependent_registrations) == 0 and not is_multi:
                    raise DependencyResolutionException(
                        dependee_injectable,
                        (
                            "Cannot satisfy the dependency"
                            f" of {dependee_injectable} on {dependent_contract}."
                        )
                    )

                # Mark each implementation as a dependency. At this point,
                # it is possible only one of them will be needed by
                # this specific type. But we'll make sure all are initialized
                # as they may be needed later.
                for dependent_registration in dependent_registrations:
                    graph.try_add_node(dependee_injectable)
                    graph.try_add_edge(dependee_injectable, dependent_registration.injectable_type)
                    injectables_to_resolve.append(dependent_registration.injectable_type)
                    self.__log.debug("Identified dependent injectable",
                                     dependee=dependee_injectable,
                                     dependent=dependent_registration.injectable_type)

        return graph

    def __resolve_injectable(self, injectable: Type[Any]) -> Any:
        registration = self.__catalog.get_registration_by_injectable(injectable)
        if not registration:
            raise DependencyResolutionException(
                injectable,
                (
                    f"Cannot find the registration for injectable '{injectable}'."
                    " This is likely an error in the algorithm."
                )
            )

        # For singleton and scoped injectables, we know that there exists one and only one
        # instance for all of the associated contracts, therefore we can find and return
        # taht specific one if it is created already.
        scope_by_injectable = get_or_add(
            self.__instances_by_injectable,
            registration.scope,
            lambda _: {})
        instances_by_injectable = get_or_add(scope_by_injectable, injectable, lambda _: set())
        if registration.scope in (InjectableScopeType.SINGLETON, InjectableScopeType.SCOPED):
            if len(instances_by_injectable) > 0:
                return next(iter(instances_by_injectable))

        instance = self.__create_instance(injectable, registration.scope)
        self.__log.debug("Instantiated injectable", injectable=injectable)
        instances_by_injectable.add(instance)

        return instance

    def __create_instance(self, injectable: Type[Any], dependee_scope: InjectableScopeType) -> Any:
        dependent_contracts = LifetimeScope.__get_dependent_contracts(injectable)
        dependent_injectables = []
        for dependent_contract, is_multi in dependent_contracts:
            registrations = self.__catalog.get_registrations_by_contract(dependent_contract)
            candidate_instances = []
            for registration in registrations:
                if LifetimeScope.__is_captive_dependency(dependee_scope, registration.scope):
                    self.__on_captive_dependency_detected(injectable, dependent_contract)

                scope = get_or_add(self.__instances_by_injectable, registration.scope, lambda _: {})
                candidate_instances.extend(scope[registration.injectable_type])

            if is_multi:
                dependent_injectables.append(tuple(candidate_instances))
            elif len(candidate_instances) > 0:
                dependent_injectables.append(candidate_instances[0])
            else:
                raise DependencyResolutionException(
                    injectable,
                    (
                        "Cannot satisfy the dependency"
                        f"of '{injectable}' on '{dependent_contract}'."
                    )
                )

        return injectable(*dependent_injectables)

    def __on_captive_dependency_detected(self, injectable: Type[Any], contract: Type[Any]) -> None:
        # Unless turned off, issue a warning, because a captive dependency
        # may be the result of a coding error, as it's generally undesirable.
        error_message = (
            "Detected captive dependency."
            f" Singleton '{injectable}' depends on transient '{contract}'."
        )
        if not self.__options.suppress_captive_dependency_warnings:
            self.__log.warn(error_message)
        if self.__options.raise_on_captive_dependency:
            raise DependencyResolutionException(injectable, error_message)
