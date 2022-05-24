"""
@package text.comment.__init__

Module for building detailed comments
"""

from __future__ import annotations

# Standard packages
from itertools import combinations

# Own package
from mfire.utils.date import Period
from mfire.text.template import Template, TemplateRetriever
from mfire.text.period_describer import PeriodDescriber
from mfire.text.comment.component import ComponentInterface
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.comment_builder.mod", bind="text.comment_builder")


class CommentBuilder:
    """CommentBuilder : basic comment builder class which builds detailed comments
    from scratch.
    """

    def __init__(self) -> None:
        self._comment = None
        self.component_handler = None

    @property
    def comment(self) -> Template:
        """comment: comment being built and processed by the comment builder

        Returns:
            Template: comment (with a Template type instead of a simple string
                in order to profit from the formatting advantages of the Template
                type.)
        """
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        self._comment = None
        if isinstance(comment, str):
            self._comment = Template(comment)

    def reset(self) -> None:
        """reset: resets the comment and component_handler
        """
        self.comment = None
        self.component_handler = None

    def process(self, component_handler: ComponentInterface) -> None:
        """process: creates and processes a new detailed comment, accessible
        through the self.comment property

        Args:
            component_handler (ComponentInterface): Component for which
                the detailed comment is being processed.
        """
        self.reset()
        self.component_handler = component_handler


class TemplateCommentBuilder(CommentBuilder):
    """TemplateCommentBuilder: Comment Builder designed for Template retrieving
    tasks.

    Args:
        template_retriever (TemplateRetriever): Object that is able to find and
            provide a template corresponding to the self.component_handler.

    Inheritance:
        CommentBuilder
    """

    def __init__(self, template_retriever: TemplateRetriever, monozone_access) -> None:
        """

        Args:
            template_retriever (TemplateRetriever): [description]
            monozone_access (partial function): Permet d'accéder au module monozone
             si on ne trouve pas le template.
        """
        super().__init__()
        self.template_retriever = template_retriever
        self.monozone_access = monozone_access

    def retrieve_template(self) -> None:
        """retrieve_template: method that triggers the self.template_retriever
        according to the self.component_handler features.
        """
        key = self.component_handler.get_template_key()
        default = f"Echec dans la récupération du template (key={key}) (error COM-001)."
        self.comment = self.template_retriever.get(key=key, default=default)
        if self.comment == default:
            # On va passer sur le module monozone si on arrive pas
            # à retrouver le template.
            # On suppose que l'erreur est dûe au fait qu'on est revenu sur du P1_1 ?
            if self.monozone_access is not None and key == "P1_1":
                LOGGER.warning(
                    "Passing through monozone after asking for template 'P1_1'.",
                    key=key,
                    **self.component_handler.log_ids,
                )
                self.comment = self.monozone_access()
            else:
                # sinon c'est une erreur
                LOGGER.error(
                    f"Failed to retrieve template '{key}'.",
                    key=key,
                    **self.component_handler.log_ids,
                )
        else:
            # On ne compte pas le template dans les statistiques.
            LOGGER.info(
                f"Choosing template '{key}'", key=key, **self.component_handler.log_ids
            )

    def process(self, component_handler: ComponentInterface) -> None:
        """process: creates and processes a new detailed comment, accessible
        through the self.comment property

        Args:
            component_handler (ComponentInterface): Component for which
                the detailed comment is being processed.
        """
        super().process(component_handler)
        self.retrieve_template()


class PeriodCommentBuilder(CommentBuilder):
    """PeriodCommentBuilder: Comment Builder designed for processing
    period-related tags in a comment.

    Inheritance:
        CommentBuilder
    """

    def process_period(self) -> None:
        """process_period: method which processes period-related tags.
        First, it creates all the possible combinations of periods according
        to the self.component_handler.
        Then it replaces in self.comment all the period tags by their relevant
        textual descriptions.
        """
        request_time = self.component_handler.get_production_datetime()

        periods = []
        for period_name in self.component_handler.get_periods_name():
            time_list = period_name.split("_to_")
            periods += [Period(time_list[0], time_list[-1])]

        periods_table = dict()
        elements = range(len(periods))
        for i in elements:
            for combin in combinations(elements, i + 1):
                keys, values = [], []
                for j in combin:
                    keys += [str(j + 1)]
                    values += [periods[j]]
                key = "periode" + "_".join(keys)
                if f"{{{key}}}" in self.comment:
                    periods_table[key] = PeriodDescriber(request_time).describe(values)
        self.comment = self.comment.format(**periods_table)

    def process(self, component_handler: ComponentInterface) -> None:
        """process: creates and processes a new detailed comment, accessible
        through the self.comment property

        Args:
            component_handler (ComponentInterface): Component for which
                the detailed comment is being processed.
        """
        super().process(component_handler)
        self.process_period()


class ZoneCommentBuilder(CommentBuilder):
    """ZoneCommentBuilder: Comment Builder designed for processing
    zone-related tags in a comment.

    Inheritance:
        CommentBuilder
    """

    @staticmethod
    def handle_areaNameProblem(zones_table, zones, parent_function) -> None:
        """ Cette fonction permet de gérer le cas ou deux zones ont un nom similair
        Elle fait pour cela appel à la fonction de la classe supérieure
        qui est la seule à avoir l'information sur tout

        Args:
            zones_table (dict): Le dictionnaire associant les noms recherchés et
            leur dénomination
            zones (list): La liste des ids
            parent_function (func): La fonction a appeler pour résoudre le soucis.
        """
        zones_values = set(zones_table.values())
        LOGGER.debug(f"Zones dans process_zone {zones_table}")
        ids = None
        for areaName in zones_values:
            tp_list = []
            for key in zones_table.keys():
                if zones_table[key] == areaName:
                    tp_list.append(key)
            if len(tp_list) > 1:
                num_list = []
                for zone in tp_list:
                    zone = zone.replace("zone", "")
                    num_list.extend(zone.split("_"))
                LOGGER.debug(f"Les zones concernées sont {set(num_list)}")
                ids = [zones[int(num) - 1] for num in set(num_list)]
                LOGGER.debug(f"On a un soucis  {areaName} apparaissant dans {tp_list}.")
                LOGGER.debug(
                    f"Les zones à l'origine de ce soucis ont les ids suivants {ids}"
                )
                break
        if parent_function is not None and ids is not None:
            LOGGER.warning(
                f"Appel fonction de classe gérer soucis de zones {areaName}, {ids}"
            )
            parent_function(ids)
        else:
            LOGGER.error("Either parent func or ids is None. Get for ids {ids}.")

    def process_zone(self, parent_function=None) -> None:
        """process_zone: method which processes zone-related tags.
        First, it creates all the possible combinations of zones according
        to the self.component_handler.
        Then it replaces in self.comment all the zone tags by their relevant
        textual descriptions.
        """
        zones = self.component_handler.get_areas_id()
        zones_table = dict()
        elements = range(len(zones))
        for i in elements:
            for combin in combinations(elements, i + 1):
                keys, values = [], []
                for j in combin:
                    keys += [str(j + 1)]
                    values += [str(zones[j])]
                key = "zone" + "_".join(keys)
                if f"{{{key}}}" in self.comment:
                    zones_table[key] = self.component_handler.merge_area(
                        values
                    ).areaName.values[0]

        # On va verifier qu'on a pas deux zones avec un nom similaire
        zones_values = set(zones_table.values())
        if len(zones_values) != len(zones_table):
            self.handle_areaNameProblem(zones_table, zones, parent_function)

        self.comment = self.comment.format(**zones_table)

    def process(self, component_handler: ComponentInterface) -> None:
        """process: creates and processes a new detailed comment, accessible
        through the self.comment property

        Args:
            component_handler (ComponentInterface): Component for which
                the detailed comment is being processed.
        """
        super().process(component_handler)
        self.process_zone()
