"""Gestion des configurations des composants type risk
et type textt

"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from mfire.composite.components import (
    AbstractComponentComposite,
    RiskComponentComposite,
    TextComponentComposite,
)
from mfire.output.cdp import CDPPeriod, CDPDataset


class BaseCDPComponent(BaseModel):
    """ Création d'un objet contenant la configuration du composant

    Args:
        BaseModel : objet pydantic

    Returns:
        BaseModel: BaseCDPComponent
    """

    ComponentId: str
    ComponentName: str
    Period: CDPPeriod
    GeoId: str
    GeoName: str

    @classmethod
    def from_composite(
        cls, component: AbstractComponentComposite, geo_id: str
    ) -> BaseCDPComponent:
        return BaseCDPComponent(
            ComponentId=component.id,
            ComponentName=component.name,
            Period=CDPPeriod.from_composite(component.period),
            GeoId=geo_id,
            GeoName=component.get_geo_name(geo_id=geo_id),
        )


class CDPAlea(BaseCDPComponent):
    """Création d'un objet Alea contenant la configuration de l'Alea
    """

    HazardId: str
    HazardName: str
    Dataset: CDPDataset
    DetailComment: str

    @classmethod
    def from_composite(
        cls, component: RiskComponentComposite, geo_id: str, text: str
    ) -> CDPAlea:
        base_dict = super().from_composite(component=component, geo_id=geo_id).dict()
        base_dict.update(Period=CDPPeriod.from_composite(component.get_risk_period()))
        return CDPAlea(
            HazardId=component.hazard,
            HazardName=component.hazard_name,
            Dataset=CDPDataset.from_composite(component=component, geo_id=geo_id),
            DetailComment=text,
            **base_dict,
        )


class CDPText(BaseCDPComponent):
    """ Création d'un objet contenant la configuration du composant type texte
    """

    SyntText: str

    @classmethod
    def from_composite(
        cls, component: TextComponentComposite, geo_id: str, text: str
    ) -> CDPText:
        base_dict = super().from_composite(component=component, geo_id=geo_id).dict()

        return CDPText(SyntText=text, **base_dict)


class CDPComponents(BaseModel):
    """Création d'un objet contenant la configuration du composant
    de type text ou de type risk
    """

    Aleas: Optional[List[CDPAlea]]
    Text: Optional[List[CDPText]]

    def append(self, components: CDPComponents) -> CDPComponents:
        if self.Aleas is None:
            aleas = components.Aleas
        elif components.Aleas is None:
            aleas = self.Aleas
        else:
            aleas = self.Aleas + components.Aleas

        if self.Text is None:
            text = components.Text
        elif components.Text is None:
            text = self.Text
        else:
            text = self.Text + components.Text

        return CDPComponents(Aleas=aleas, Text=text)
