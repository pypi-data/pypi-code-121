"""Hydroquebec webuser module."""
import logging
from typing import Optional, Union

from hydroqc.hydro_api.client import HydroClient
from hydroqc.customer import Customer
from hydroqc.logger import get_logger
from hydroqc.error import HydroQcError


class WebUser:
    """Hydroquebec webuser.

    Represents a login/password web account (Demandeur)
    """

    _no_partenaire_demandeur: str
    _nom1_demandeur: str
    _nom2_demandeur: str

    def __init__(
        self,
        username: str,
        password: str,
        verify_ssl: bool,
        log_level: Optional[str] = None,
        http_log_level: Optional[str] = None,
    ):
        """Create a new Hydroquebec webuser."""
        self._hydro_client = HydroClient(
            username, password, verify_ssl, log_level=http_log_level
        )
        self._username: str = username
        self._log_level: Optional[str] = log_level
        self.customers: list[Customer] = []
        self._logger: Union[None, logging.Logger] = None

    async def login(self) -> bool:
        """Login to Hydroquebec website."""
        return await self._hydro_client.login()

    async def get_info(self) -> None:
        """Fetch data about this webuser.

        Retrieve customers, accounts and contracts.
        """
        user_info = await self._hydro_client.get_user_info()
        self._no_partenaire_demandeur = user_info[0]["noPartenaireDemandeur"]
        # We can only create the logger after getting user info at least on time
        if self._logger is None:
            self._logger = get_logger(f"w-{self.webuser_id}", self._log_level)
        self._logger.info("Got webuser info")

        if (
            not user_info
            or "nom1Demandeur" not in user_info[0]
            or "nom2Demandeur" not in user_info[0]
        ):
            msg = f"Can not find customer name: {user_info}"
            self._logger.error(msg)
            raise HydroQcError(msg)

        # is the same accross contracts
        self._nom1_demandeur = user_info[0]["nom1Demandeur"]
        self._nom2_demandeur = user_info[0]["nom2Demandeur"]
        for customer_data in user_info:
            customer_names = [
                v
                for k, v in customer_data.items()
                if k.startswith("nom") and k.endswith("Titulaire")
            ]
            customer_id = customer_data["noPartenaireTitulaire"]
            # Create new customer if it's not there
            if customer_id not in [c.customer_id for c in self.customers]:
                self._logger.info("Creating new customer %s", customer_id)
                customer = Customer(
                    self.webuser_id,
                    customer_data["noPartenaireTitulaire"],
                    customer_names,
                    self._hydro_client,
                    self._log_level,
                )
                self.customers.append(customer)
            else:
                customer = [c for c in self.customers if c.customer_id == customer_id][
                    0
                ]
            await customer.get_info()

    @property
    def webuser_id(self) -> str:
        """Get webuser id."""
        return self._no_partenaire_demandeur

    @property
    def first_name(self) -> str:
        """Get webuser firstname."""
        return self._nom1_demandeur

    @property
    def last_name(self) -> str:
        """Get webuser lastname."""
        return self._nom2_demandeur

    @property
    def session_expired(self) -> bool:
        """Is the current session expired or not."""
        return self._hydro_client.session_expired

    async def refresh_session(self) -> None:
        """Refresh the current session."""
        await self._hydro_client.refresh_session()

    def get_customer(self, customer_id: str) -> Customer:
        """Find customer by id."""
        customers = [c for c in self.customers if c.customer_id == customer_id]
        if not customers:
            raise HydroQcError(f"Customer {customer_id} not found")
        return customers[0]

    async def close_session(self) -> None:
        """Close http sessions."""
        await self._hydro_client.close_session()

    def __repr__(self) -> str:
        """Represent object."""
        if not self._no_partenaire_demandeur:
            return f"""<Webuser - {self._username}>"""
        return f"""<Webuser - {self.webuser_id}>"""
