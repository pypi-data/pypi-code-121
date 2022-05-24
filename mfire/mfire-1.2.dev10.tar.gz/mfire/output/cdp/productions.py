""" Gestion du fichier de sortie via l'objet OutputProduction
"""
from __future__ import annotations

from typing import Optional

from pydantic import validator

from mfire.utils.date import Datetime
from mfire.output.base import BaseOutputProduction
from mfire.output.cdp.components import CDPComponents


class CDPProduction(BaseOutputProduction):
    """Création d'un objet OutputProduction contenant le json de sortie
    de la tâche de production promethee, au format recquis par le CDP bulletin.

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet OutputProduction
    """

    ProductionId: str
    ProductionName: str
    CustomerId: Optional[str]
    CustomerName: Optional[str]
    DateBulletin: Datetime
    DateProduction: Datetime
    DateConfiguration: Datetime
    Components: CDPComponents

    @validator("DateBulletin", "DateProduction", "DateConfiguration", pre=True)
    def init_dates(cls, v: str) -> Datetime:
        return Datetime(v)

    @validator("CustomerId", "CustomerName", always=True)
    def init_customer(cls, v: str) -> str:
        if v is None:
            return "unknown"
        return v

    def append(self, other_production: CDPProduction) -> CDPProduction:
        return CDPProduction(
            ProductionId=self.ProductionId,
            ProductionName=self.ProductionName,
            CustomerId=self.CustomerId,
            CustomerName=self.CustomerName,
            DateBulletin=self.DateBulletin,
            DateProduction=self.DateProduction,
            DateConfiguration=self.DateConfiguration,
            Components=self.Components.append(other_production.Components),
        )
