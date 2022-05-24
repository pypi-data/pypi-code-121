"""
    Module d'interprétation de la configuration
"""
from __future__ import annotations

from typing import List, Union

from mfire.settings import get_logger
from mfire.composite.base import BaseComposite
from mfire.composite.components import RiskComponentComposite, TextComponentComposite

# Logging
LOGGER = get_logger(name="productions.mod", bind="productions")


class ProductionComposite(BaseComposite):
    """Création d'un objet Production contenant la configuration
    de la tâche de production promethee

    Args:
        baseModel : modèle de la librairie pydantic

    Returns:
        baseModel : objet Production
    """

    id: str
    name: str
    config_hash: str
    prod_hash: str
    mask_hash: str
    components: List[Union[RiskComponentComposite, TextComponentComposite]]

    def compute(self):
        for component in self.components:
            component.compute()
