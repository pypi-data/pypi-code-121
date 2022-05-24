"""
Module permettant de gérer la génération de commentaires.
C'est dans ce module qu'on va décider vers quel module
de génération de texte on va orienter.
"""
from typing import Union

from pydantic import BaseModel
import xarray as xr

from mfire.settings import get_logger
from mfire.localisation.localisation_manager import Localisation
from mfire.localisation.core_spatial import LocalisationError
from mfire.text.comment.component import ComponentHandlerLocalisation
from mfire.text.comment.multizone import MultiZoneAdapter
from mfire.text.comment_generator.text_generator import GenerationText
from mfire.composite.components import RiskComponentComposite


# Logging
LOGGER = get_logger(name="comment_manager.mod", bind="comment_manager")

xr.set_options(keep_attrs=True)


class CommentManager(BaseModel):
    """Class responsible for choosing which algorithm to use to produce the comment
    of a given component and to produce it.

    Args:
        component (RiskComponentComposite) : RiskComponentComposite to be commented.
    """

    component: RiskComponentComposite
    _text_generator_handler: Union[GenerationText, MultiZoneAdapter]

    class Config:
        """ Cette classe Config permet de contrôler de comportement de pydantic
        """

        underscore_attrs_are_private = True
        arbitrary_types_allowed = True

    def get_comment(self, geo_id: str) -> str:
        """
        Permet de récupérer le commentaire pour la zone identifiée
        Attention cette fonction a besoin que decision_tree ai été déclenché auparavant.

        Args:
            geo_id (str) : L'identifiant de la zone

        Returns:
            str: Le commentaire
        """
        self.decision_tree(geo_id)
        return self._text_generator_handler.identification_cas(geo_id)

    def produce_monozone(self, geo_id):
        self._text_generator_handler = GenerationText(self.component)
        return self._text_generator_handler.identification_cas(geo_id)

    def decision_tree(self, geo_id):
        """
        Permet de décider quel module de génération de commentaire est à utiliser.

        Args:
            geo_id (str): Id de la zone.
        """
        module = "unizone"
        maxi_risk = self.component.get_final_risk_max_level(geo_id)

        if maxi_risk >= 1:
            # Mettre d'autres conditions pour ne pas passer par la localisation.
            #   - Type de risque (upstream/downstream)

            # On recupere la définition du risque
            risk_list = self.component.select_risk_level(level=maxi_risk)

            agg = risk_list[0].aggregation_type

            if agg == "downStream":
                hourly_maxi_risk = self.component.final_risk_da.sel(id=geo_id)
                # On recupere la periode où le risque le plus grand existe
                risk_period = hourly_maxi_risk.sel(
                    valid_time=(hourly_maxi_risk == maxi_risk)
                ).valid_time
                try:
                    loca_handler = Localisation(
                        self.component,
                        risk_level=maxi_risk,
                        geo_id=geo_id,
                        period=set(risk_period.values),
                    )
                    unique_table, _ = loca_handler.get_summarized_info()
                    # On va regarder s'il est nécessaire de faire de
                    # la localisation spatiale sur le risque le plus eleve.
                    if unique_table.id.size > 1:
                        module = "multizone"
                        LOGGER.debug("Going to multiZone commentary type")
                except LocalisationError as e:
                    # Si c'est une erreur 'normale' du module de localisaion
                    # (pas de zones descriptive, pas le bon type de risque, etc... ).
                    # On passe alors au module monozone.
                    LOGGER.warning(repr(e))
                    pass

        if module == "unizone":
            self._text_generator_handler = GenerationText(self.component)
        else:
            compo_handler = ComponentHandlerLocalisation(loca_handler)
            self._text_generator_handler = MultiZoneAdapter(
                compo_handler, monozone_access=self.produce_monozone
            )
