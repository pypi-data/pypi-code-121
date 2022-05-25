"""Contracts and tariffs."""
from datetime import datetime
from typing import List, Optional

from pandas import DataFrame, json_normalize

from bambooapi_client.openapi.apis import ContractsApi as _ContractsApi
from bambooapi_client.openapi.exceptions import NotFoundException
from bambooapi_client.openapi.models import (
    ContractCreate,
    ContractListItem,
    ContractUpdate,
    TariffCreate,
    TariffListItem,
    TariffSpecsCreate,
    TariffSpecsListItem,
    TariffSpecsUpdate,
    TariffUpdate,
)


class ContractsApi:
    """Implementation for '/v1/contracts' and '/v1/tariffs' endpoints."""

    def __init__(self, bambooapi_client):
        """Initialize defaults."""
        self._bambooapi_client = bambooapi_client
        self._api_instance = _ContractsApi(bambooapi_client.api_client)

    def list_contracts(self) -> List[ContractListItem]:
        """List contracts."""
        return self._api_instance.list_contracts()

    def read_contract(self, contract_id: int) -> Optional[dict]:
        """Get contract by id."""
        try:
            return self._api_instance.read_contract(contract_id)
        except NotFoundException:
            return None

    def create_contract(self, contract: ContractCreate) -> dict:
        """Create a new contract."""
        return self._api_instance.create_contract(contract.to_dict())

    def update_contract(
        self,
        contract_id: int,
        contract: ContractUpdate,
    ) -> dict:
        """Update contract."""
        return self._api_instance.update_contract(
            contract_id,
            contract.to_dict(),
        )

    def delete_contract(self, contract_id: int) -> dict:
        """Delete contract."""
        return self._api_instance.delete_contract(contract_id)

    def read_contract_schedule(
        self,
        contract_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> DataFrame:
        """Return a Dataframe with the contract schedule between two dates."""
        schedule = self._api_instance.read_contract_schedule(
            contract_id,
            start_time=start_time,
            end_time=end_time,
        )
        schedule_dicts = [
            contract_schedule_item.to_dict()
            for contract_schedule_item in schedule
        ]
        if schedule:
            return json_normalize(data=schedule_dicts).set_index(['time'])
        else:
            return DataFrame()

    def list_tariffs(self) -> List[TariffListItem]:
        """List tariffs."""
        return self._api_instance.list_tariffs()

    def read_tariff(self, tariff_id: int) -> Optional[dict]:
        """Get tariff by id."""
        try:
            return self._api_instance.read_tariff(tariff_id)
        except NotFoundException:
            return None

    def create_tariff(
        self,
        tariff: TariffCreate,
    ) -> dict:
        """Create a new tariff."""
        return self._api_instance.create_tariff(tariff.to_dict())

    def update_tariff(
        self,
        tariff_id: int,
        tariff: TariffUpdate,
    ) -> dict:
        """Update tariff."""
        return self._api_instance.update_tariff(
            tariff_id,
            tariff.to_dict(),
        )

    def delete_tariff(self, tariff_id: int) -> dict:
        """Delete tariff."""
        return self._api_instance.delete_tariff(tariff_id)

    def list_tariff_specs(
        self,
        tariff_id: int,
    ) -> List[TariffSpecsListItem]:
        """List tariff specs of a tariff."""
        return self._api_instance.list_tariff_specs(tariff_id)

    def read_tariff_specs(self, tariff_specs_id: int) -> Optional[dict]:
        """Get tariff specs by id."""
        try:
            return self._api_instance.read_tariff_specs(tariff_specs_id)
        except NotFoundException:
            return None

    def create_tariff_specs(
        self,
        tariff_id: int,
        tariff_specs: TariffSpecsCreate,
    ) -> dict:
        """Create a new tariff specs."""
        return self._api_instance.create_tariff_specs(
            tariff_id,
            tariff_specs.to_dict(),
        )

    def update_tariff_specs(
        self,
        tariff_specs_id: int,
        tariff_specs: TariffSpecsUpdate,
    ) -> dict:
        """Update tariff specs."""
        return self._api_instance.update_tariff_specs(
            tariff_specs_id,
            tariff_specs.to_dict(),
        )

    def delete_tariff_specs(self, tariff_specs_id: int) -> dict:
        """Delete tariff specs."""
        return self._api_instance.delete_tariff_specs(tariff_specs_id)
