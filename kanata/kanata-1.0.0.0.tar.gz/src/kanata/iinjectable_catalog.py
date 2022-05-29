from .models import InjectableRegistration
from abc import ABCMeta, abstractmethod
from typing import Any, Optional, Tuple, Type, TypeVar

T = TypeVar("T")

class IInjectableCatalog(metaclass=ABCMeta):
    """Interface for a catalog of injectable registrations."""

    @abstractmethod
    def get_registrations(self) -> Tuple[InjectableRegistration, ...]:
        """Gets all the registrations available in the catalog.

        :return: The available registrations.
        :rtype: Tuple[InjectableRegistration, ...]
        """

    @abstractmethod
    def get_registrations_by_contract(
        self,
        contract: Type[Any]) -> Tuple[InjectableRegistration, ...]:
        """Gets the registrations associated to the specified contract.

        :param contract: The contract for which to get the registrations.
        :type contract: Type[Any]
        :return: The registrations associated to the contract.
        :rtype: Tuple[InjectableRegistration, ...]
        """

    @abstractmethod
    def get_registration_by_injectable(
        self,
        injectable: Type[Any]) -> Optional[InjectableRegistration]:
        """Gets the registration associated to the specified injectable.

        :param injectable: The injectable for which to get the registration.
        :type injectable: Type[Any]
        :return: If exists, the registration associated to the injectable.
        :rtype: Optional[InjectableRegistration]
        """
