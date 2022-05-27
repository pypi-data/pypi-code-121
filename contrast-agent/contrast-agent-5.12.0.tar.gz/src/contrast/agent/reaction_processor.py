# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.disable_reaction import DisableReaction
from contrast.api.settings_pb2 import Reaction

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class ReactionProcessor(object):
    @staticmethod
    def process(application_settings, settings):
        if not settings.config.is_service_bypassed:
            if (
                application_settings is None
                or settings is None
                or application_settings.reactions is None
                or len(application_settings.reactions) == 0
            ):
                return

            for reaction in application_settings.reactions:
                logger.debug("Received the following reaction: %s", reaction.operation)

                if reaction.operation == Reaction.DISABLE:
                    DisableReaction.run(settings)

        elif isinstance(application_settings, list):
            ts_reactions = application_settings

            for reaction in ts_reactions:
                operation = reaction.get("operation", "")
                msg = reaction.get("message", "")

                logger.debug(
                    "Received the following reaction: %s %s",
                    operation,
                    msg,
                    direct_to_teamserver=1,
                )

                if operation == DisableReaction.NAME:
                    DisableReaction.run(settings)
