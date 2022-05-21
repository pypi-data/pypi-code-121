"""Hydroquebec Account Module."""
from typing import Optional, Any

from hydroqc.logger import get_logger
from hydroqc.contract import Contract
from hydroqc.error import HydroQcError
from hydroqc.hydro_api.client import HydroClient


class Account:
    """Hydroquebec account.

    Represents an account (compte)
    """

    _balance: float

    def __init__(
        self,
        webuser_id: str,
        customer_id: str,
        account_id: str,
        contracts: list[Contract],
        hydro_client: HydroClient,
        log_level: Optional[str] = None,
    ):
        """Create an Hydroquebec account."""
        self._logger = get_logger(
            f"a-{account_id}", log_level, parent=f"w-{webuser_id}.c-{customer_id}"
        )
        self._no_partenaire_demandeur: str = webuser_id
        self._no_partenaire_titulaire: str = customer_id
        self._no_compte_contrat: str = account_id
        self._hydro_client: HydroClient = hydro_client
        self.contracts: list[Contract] = contracts
        self._address: str = ""
        self._balance_unpaid: str = ""
        self._last_bill: str = ""
        self._bill_date_create: str = ""
        self._bill_date_due: str = ""
        self._bill_date_next: str = ""

    @property
    def webuser_id(self) -> str:
        """Get webuser id."""
        return self._no_partenaire_demandeur

    @property
    def customer_id(self) -> str:
        """Get customer id."""
        return self._no_partenaire_titulaire

    @property
    def account_id(self) -> str:
        """Get account id."""
        return self._no_compte_contrat

    async def get_info(self) -> dict[str, Any]:
        """Fetch latest data of this account."""
        self._logger.info("Get account info")
        data = await self._hydro_client.get_account_info(
            self.webuser_id, self.customer_id, self.account_id
        )
        self._address = data["adresse"].strip()
        self._balance = data["solde"]
        self._balance_unpaid = data["solde"]
        self._last_bill = data["montant"]
        self._bill_date_create = data["dateEmission"]
        self._bill_date_due = data["dateEcheance"]
        self._bill_date_next = data["dateProchaineFacture"]
        return data

    @property
    def balance(self) -> float:
        """Get current balance."""
        return self._balance

    def get_contract(self, contract_id: str) -> Contract:
        """Find contract by id."""
        contracts = [c for c in self.contracts if c.contract_id == contract_id]
        if not contracts:
            raise HydroQcError(f"Contract {contract_id} not found")
        return contracts[0]

    def __repr__(self) -> str:
        """Represent object."""
        return f"""<Account - {self.webuser_id} - {self.customer_id} - {self.account_id}>"""
