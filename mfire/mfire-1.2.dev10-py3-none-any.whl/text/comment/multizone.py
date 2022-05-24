"""
@package text.comment.multizone

Module retrieving text templates
"""

# Standard packages
from __future__ import annotations
from functools import partial

# Own package
from mfire.settings import Settings, TEMPLATES_FILENAMES
from mfire.text.comment.component import ComponentInterface
from mfire.text.comment.comment_builder import (
    TemplateCommentBuilder,
    PeriodCommentBuilder,
    ZoneCommentBuilder,
)
from mfire.text.comment.representative_builder import RepresentativeValueManager
from mfire.text.template import read_file
from mfire.utils.text_tools import (
    start_sentence_with_capital,
    modify_unit,
)
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.comment.multizone.mod", bind="text.comment.multizone")


def new_multizone(template_name, monozone_access=None) -> MultiZone:
    """new_multizone: temporary function that creates a full MultiZone
    CommentBuilder out of the box.

    Returns:
        Multizone: new multizone comment builder object.
    """
    key = "generic"
    if template_name == "SNOW":
        key = "snow"
    elif template_name == "PRECIP":
        key = "precip"
    return MultiZone(
        read_file(TEMPLATES_FILENAMES[Settings().language]["multizone"][key]),
        monozone_access=monozone_access,
    )


class MultiZone(
    TemplateCommentBuilder,
    PeriodCommentBuilder,
    ZoneCommentBuilder,
    RepresentativeValueManager,
):
    """Multizone: specific CommentBuilder for handling 'multizone' types of
    components.

    Args:
        template_retriever (TemplateRetriever): Object that is able to find and
            provide a template corresponding to the self.component_handler.

    Inheritance:
        TemplateCommentBuilder
        PeriodCommentBuilder
        ZoneCommentBuilder
    """

    def handle_area_problems(self, areaIds) -> None:
        LOGGER.debug(f"Fonction permettant de gérer les erreurs de zones {areaIds}")
        # 1. On va devoir faire modifier le template
        self.component_handler.modify_template(areaIds)
        LOGGER.debug(
            f"Template après modif {self.component_handler.get_template_key()}"
        )
        # 2. On refait tourner le template_retriever
        self.retrieve_template()
        # 3. On reprocess les periodes
        self.process_period()
        # 4. On refait les zones
        self.process_zone(self.handle_area_problems)
        # La cinquième étape est réalisée suite au précédent process_zone
        # (ayant appellé handle_area_problems).

    def process(self, component_handler: ComponentInterface) -> None:
        """process: method for processing a full self.comment according to the
        given component_handler.

        Args:
            component_handler (ComponentHandler): Object handling all the component's
                features necessary to create an appropriate comment.

        """
        self.reset()
        self.component_handler = component_handler
        self.retrieve_template()
        self.process_period()
        self.process_zone(self.handle_area_problems)
        self.process_value()


class MultiZoneAdapter:
    """MultiZoneAdapter : Temporary class having the same arguments as Lamyaa's
    TextGenerator class.

    Args:
        component_handler (ComponentInterface) : Object handling all the component's
            features necessary to create a proper comment.
    """

    def __init__(self, component_handler: ComponentInterface, monozone_access):
        """[summary]

        Args:
            component_handler (ComponentInterface): [description]
            monozone_access ([type]): Fonction permettant si besoin
               de faire appel au module monozone
        """
        self.component_handler = component_handler
        self.monozone_access = monozone_access

    def identification_cas(self, geo_id: str):
        """identification_cas: method finding the correct case to create
        the corresponding detailed comment.

        Args:
            geo_id (str): meaningless geo id

        Returns:
            str : detailed comment
        """
        LOGGER.debug(f"geo_id : {geo_id}", geo_id=geo_id)
        template_name = self.component_handler.get_template_type()
        LOGGER.debug(f"Template type {template_name}")
        multi = new_multizone(
            template_name, monozone_access=partial(self.monozone_access, geo_id=geo_id)
        )
        multi.process(self.component_handler)
        return modify_unit(start_sentence_with_capital(multi.comment))
