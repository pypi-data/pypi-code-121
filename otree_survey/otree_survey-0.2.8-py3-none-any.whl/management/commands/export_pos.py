import logging
import os
import shutil
from pathlib import Path

from django.core.management import BaseCommand, execute_from_command_line

logger = logging.getLogger(__name__)

DEFAULT_PO_TRANSFER_DIR = "po_transfer"


class Command(BaseCommand):
    help = "Export po files for translation"

    def add_arguments(self, parser):
        parser.add_argument(
            "app",
            nargs="+",
            help="App (folder) name",
        )
        # could make lang optional and use languages from settings module
        parser.add_argument(
            "--lang",
            "-l",
            nargs="*",
            help="Language (de, fr, ...); always put after app name(s)",
        )
        parser.add_argument(
            "--transfer_dir",
            nargs="?",
            default=DEFAULT_PO_TRANSFER_DIR,
            help="Folder in which the po files are saved",
        )

    def handle(self, app, *, lang, transfer_dir, **options):
        apps, langs = app, lang

        project_dir = Path().absolute()
        assert (
            project_dir / "manage.py"
        ).exists(), (
            "Please run this command from project root that contains the manage.py file"
        )

        # update translation files
        for app in apps:
            print(f"Updating files for {app}...")
            for lang in langs:
                os.chdir(project_dir / app)
                exit_status = execute_from_command_line(
                    f"manage.py makemessages -l {lang}".split()
                )
                if exit_status:
                    raise RuntimeError(f"Could not makemessages for {app} and {lang}")

        # copy translation files into transfer folder
        print("Copying files...")
        os.chdir(project_dir)
        for app in apps:
            for lang in langs:
                shutil.copy(
                    f"{app}/locale/{lang}/LC_MESSAGES/django.po",
                    f"{transfer_dir}/{app}_{lang}.po",
                )
