from mfire.settings import get_logger
from mfire.text.base import BaseBuilder, BaseSelector
from mfire.text.template import TemplateRetriever

# Logging
LOGGER = get_logger(name="base_selector.mod", bind="base_selector")


class TemplateBuilder(BaseBuilder):
    """ TemplateBuilder qui doit renvoyer une clé de template
    """

    def find_template_key(self, selector: BaseSelector) -> str:
        return selector.compute(self.reduction)

    def retrieve_template(
        self, key: str, template_retriever: TemplateRetriever
    ) -> None:
        """retrieve_template: method that triggers the self.template_retriever
        according to the reducer features.
        """
        # dans branche suivante
        # default = f"Echec dans la récupération du template
        # (key={key})(error COM-001). "
        #
        # self._text = template_retriever.get(
        #     key=key, default=default, pop_method="random"
        # )
        self._text = ""
