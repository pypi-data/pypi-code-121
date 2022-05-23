import subprocess
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from postgres_lock.lock import PostgresLock


class Command(BaseCommand):
    help = "Run a command inside a Postgres lock"

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument("command", nargs="+", help="Command to run inside the advisory lock.")

        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. Defaults to the "default" database.',
        )
        parser.add_argument(
            "--try",
            action="store_true",
            help="Try and acquire a lock, but fail immediately if the lock cannot be acquired.",
        )
        parser.add_argument(
            "--ignore-fail",
            action="store_true",
            help="Ignore failure if a lock cannot be acquired (return a successful exit code).",
        )
        parser.add_argument(
            "--shared",
            action="store_true",
            help="Acquire a lock which can be shared with other sessions.",
        )
        parser.add_argument("--name", help="Use a specific lock name for this command.")

    def execute(self, *args, **options):
        with PostgresLock(
            name=options["name"],
            try_=options["try"],
            shared=options["shared"],
            using=options["database"],
        ) as acquired:
            if acquired:
                completed = subprocess.run(options["command"])
                # Raise the return code of the child process if an error occurs
                if completed.returncode != 0:
                    sys.exit(completed.returncode)
            elif options["ignore_fail"]:
                self.stderr.write("Unable to acquire lock")
            else:
                raise CommandError("Unable to acquire lock")
