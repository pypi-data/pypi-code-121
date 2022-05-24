"""
    Module d'interprétation de la configuration des périodes
"""
from typing import List, Any, Optional

from pydantic import BaseModel, validator

from mfire.utils.date import Datetime


class Period(BaseModel):
    """Création d'un objet Period contenant la configuration des périodes
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Period
    """

    id: str
    name: Optional[str] = None
    start: Datetime
    stop: Datetime

    @validator("start", "stop", pre=True)
    def init_boundaries(cls, v: str) -> Datetime:
        return Datetime(v)


class PeriodCollection(BaseModel):
    """Création d'un objet PeriodCollection contenant une liste de périodes
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        List[baseModel] : liste d'objet Period
    """

    periods: List[Period]

    def __iter__(self):
        """iterate over periods"""
        return iter(self.periods)

    def __len__(self):
        """return periods length"""
        return len(self.periods)

    def __getitem__(self, id: str) -> Period:
        """get periods at a given index"""
        try:
            return next(period for period in self.periods if period.id == id)
        except StopIteration:
            raise KeyError(f"'{id}'")

    def get(self, index: str, default: Any = None) -> Period:
        """get period with a default value in case
        """
        try:
            return self[index]
        except KeyError:
            return default
