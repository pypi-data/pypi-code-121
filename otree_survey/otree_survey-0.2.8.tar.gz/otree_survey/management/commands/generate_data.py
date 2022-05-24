import logging
import os
from pathlib import Path

from django.conf import settings, global_settings
from django.core.management.base import BaseCommand
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

import otree.common
import otree.export
import otree.session
from otree.models import Participant
from otree.bots.runner import run_bots
from otree.session import SESSION_CONFIGS_DICT

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Based on otree.management.commands.bots and otree.bots.runner
    """

    help = "Generates test data using oTree test"

    def add_arguments(self, parser):
        parser.add_argument(
            "session_config_names",
            nargs="*",
            help="If omitted, all sessions in SESSION_CONFIGS are run",
        )
        parser.add_argument(
            "--num_participants",
            type=int,
            nargs="?",
            default=1,
            help="Number of participants",
        )
        parser.add_argument(
            "--export_path",
            nargs="?",
            default="_gendata",
            help="Folder in which the CSVs are saved",
        )
        parser.add_argument(
            "--participant_labels",
            nargs="*",
            help="Participant labels for bots, number has to match num_participants",
        )

    def prepare_global_state(self):
        """Copied from otree.management.commands.bots"""
        settings.WHITENOISE_AUTOREFRESH = True
        otree.common.patch_migrations_module()
        settings.STATICFILES_STORAGE = global_settings.STATICFILES_STORAGE

    def handle(
        self,
        *,
        verbosity,
        session_config_names,
        num_participants,
        export_path,
        participant_labels,
        **options,
    ):
        # prepare state and db
        # copied from otree.management.commands.bots
        self.prepare_global_state()
        setup_test_environment()
        old_config = setup_databases(
            interactive=False, verbosity=verbosity, aliases={"default"}
        )

        try:
            if not session_config_names:
                session_config_names = SESSION_CONFIGS_DICT.keys()

            # run bots
            # copied from otree.management.commands.bots, added participant_labels
            if participant_labels:
                assert (
                    len(participant_labels) == num_participants
                ), "Length of participant_labels has to match num_participants"
            else:
                participant_labels = [f"bot_{i}" for i in range(num_participants)]

            for config_name in session_config_names:
                try:
                    config = SESSION_CONFIGS_DICT[config_name]
                except KeyError:
                    # important to alert the user, since people might be trying to enter app names.
                    msg = f"No session config with name '{config_name}'."
                    raise Exception(msg) from None

                # changed: use only first case
                case_number = 0
                logger.info(
                    "Creating '{}' session (test case {})".format(
                        config_name, case_number
                    )
                )
                session = otree.session.create_session(
                    session_config_name=config_name,
                    num_participants=(num_participants),
                )

                # added: participant labels
                participants = Participant.objects.filter(session=session)
                assert len(participants) == num_participants
                for i, participant in enumerate(participants):
                    participant.label = participant_labels[i]
                    participant.save()

                run_bots(session, case_number=case_number)
                logger.info("Bots completed session")

            # export
            # copied from otree.management.commands.bots, added custom exports
            os.makedirs(export_path, exist_ok=True)
            for app in settings.INSTALLED_OTREE_APPS:
                model_module = otree.common.get_models_module(app)
                if model_module.Player.objects.exists():
                    fpath = Path(export_path, "{}.csv".format(app))
                    with fpath.open("w", encoding="utf8") as fp:
                        otree.export.export_app(app, fp)
                    # added: custom export
                    if hasattr(model_module, "custom_export"):
                        custom_fpath = Path(export_path, "{}_custom.csv".format(app))
                        with custom_fpath.open("w", encoding="utf8") as fp:
                            otree.export.custom_export_app(app, fp)
            fpath = Path(export_path, "all_apps_wide.csv")
            with fpath.open("w", encoding="utf8") as fp:
                otree.export.export_wide(fp)
            logger.info('Exported CSV to folder "{}"'.format(export_path))

        finally:
            teardown_databases(old_config, verbosity=verbosity)
            teardown_test_environment()
