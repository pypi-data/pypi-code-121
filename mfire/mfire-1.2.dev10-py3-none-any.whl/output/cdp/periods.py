""" gestion des périodes pour les fichiers de sortie promethee
"""
from __future__ import annotations
from mfire.utils.date import Datetime

from pydantic import BaseModel, validator

from mfire.composite.periods import Period


class CDPPeriod(BaseModel):
    """Création d'un objet Period contenant la configuration des périodes
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Period
    """

    PeriodId: str
    PeriodName: str
    DateDebutPeriode: Datetime
    DateFinPeriode: Datetime

    @validator("DateDebutPeriode", "DateFinPeriode", pre=True)
    def init_dates(cls, v: str) -> Datetime:
        return Datetime(v)

    @classmethod
    def from_composite(cls, period: Period) -> CDPPeriod:
        """Class for transforming a composite period into a
        actual Output CDP Model period

        Args:
            period (Period): Composite Period object

        Returns:
            CDPPeriod: Output Model

        TODO: Put the PeriodName into a template.
        """
        name = period.name
        if name is None:
            name = f"Du {period.start} au {period.stop}"
        return CDPPeriod(
            PeriodId=period.id,
            PeriodName=name,
            DateDebutPeriode=period.start,
            DateFinPeriode=period.stop,
        )
