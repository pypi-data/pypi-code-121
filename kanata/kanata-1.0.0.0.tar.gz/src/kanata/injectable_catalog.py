from .iinjectable_catalog import IInjectableCatalog
from .models import InjectableRegistration
from kanata.utils import get_or_add
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type

class InjectableCatalog(IInjectableCatalog):
    """Provides access to information about the known injectables."""

    def __init__(self, registrations: Iterable[InjectableRegistration]) -> None:
        self.__registrations_by_contract: Dict[Type[Any], List[InjectableRegistration]] = {}
        self.__registrations_by_injectable: Dict[Type[Any], InjectableRegistration] = {}
        self.__build_registration_maps(registrations)

    def get_registrations(self) -> Tuple[InjectableRegistration, ...]:
        return tuple(self.__registrations_by_injectable.values())

    def get_registrations_by_contract(
        self,
        contract: Type[Any]) -> Tuple[InjectableRegistration, ...]:
        return tuple(self.__registrations_by_contract.get(contract, []))

    def get_registration_by_injectable(
        self,
        injectable: Type[Any]) -> Optional[InjectableRegistration]:
        return self.__registrations_by_injectable.get(injectable, None)

    def __build_registration_maps(self, registrations: Iterable[InjectableRegistration]) -> None:
        for registration in registrations:
            for contract_type in registration.contract_types:
                by_injectables: List[InjectableRegistration] = get_or_add(
                    self.__registrations_by_contract,
                    contract_type,
                    lambda _: [])
                by_injectables.append(registration)

            self.__registrations_by_injectable[registration.injectable_type] = registration
