"""
@package text.comment.monozone

Module retrieving text templates
"""

# Standard packages
from __future__ import annotations

# Own package
from mfire.settings import TEMPLATES_FILENAMES, Settings
from mfire.text.comment.component import ComponentInterface
from mfire.text.comment.comment_builder import (
    TemplateCommentBuilder,
    PeriodCommentBuilder,
)
from mfire.text.template import read_file
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.comment.monozone.mod", bind="text.comment.monozone")


def new_monozone() -> MonoZone:
    """new_monozone: temporary function that creates a full MonoZone
    CommentBuilder out of the box.

    Returns:
        MonoZone: new monozone comment builder object.
    """
    return MonoZone(read_file(TEMPLATES_FILENAMES[Settings().language]["monozone"]))


class MonoZone(TemplateCommentBuilder, PeriodCommentBuilder):
    """MonoZone: specific CommentBuilder for handling 'monozone' types of
    components.

    Args:
        template_retriever (TemplateRetriever): Object that is able to find and
            provide a template corresponding to the self.component_handler.

    Inheritance:
        TemplateCommentBuilder
        PeriodCommentBuilder
    """

    def process(self, component_handler: ComponentInterface) -> str:
        """process: method for processing a full self.comment according to the
        given component_handler.

        Args:
            component_handler (ComponentInterface): Object handling all the component's
                features necessary to create an appropriate comment.
        """
        self.reset()
        self.component_handler = component_handler
        self.retrieve_template()
        self.process_period()
        return self.comment
