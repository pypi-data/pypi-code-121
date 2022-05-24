import logging
import os
import re
import shutil
from glob import glob
from pathlib import Path

from django.core.management import BaseCommand, execute_from_command_line

from .export_pos import DEFAULT_PO_TRANSFER_DIR

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import and compile all pos files in `transfer_dir`"

    def add_arguments(self, parser):
        parser.add_argument(
            "--transfer_dir",
            nargs="?",
            default=DEFAULT_PO_TRANSFER_DIR,
            help="Folder in which the po files are saved",
        )

    def handle(self, *, transfer_dir, **options):
        project_dir = Path().absolute()
        assert (
            project_dir / "manage.py"
        ).exists(), (
            "Please run this command from project root that contains the manage.py file"
        )

        # move translation files into the right folders
        print("Moving files...")
        os.chdir(project_dir / transfer_dir)
        files = glob("*.po")
        apps = []
        for file in files:
            match = re.search("(.*)_([a-z]{2}).po", file)
            if not match:
                logger.warning(f"Unexpected file {file}")
            app = match.group(1)
            lang = match.group(2)
            shutil.move(file, f"../{app}/locale/{lang}/LC_MESSAGES/django.po")
            apps.append(app)

        # compile translations
        print("Compiling translations...")
        for app in apps:
            os.chdir(project_dir / app)
            execute_from_command_line(f"manage.py compilemessages --use-fuzzy".split())
