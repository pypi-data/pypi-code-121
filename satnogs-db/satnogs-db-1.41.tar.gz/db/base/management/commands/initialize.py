"""SatNOGS DB django management command to initialize a new database"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """django management command to initialize a new database"""
    help = 'Create initial fixtures'

    def handle(self, *args, **options):
        # Migrate
        self.stdout.write("Creating database...")
        call_command('migrate')

        # Initial data
        self.stdout.write("Creating fixtures...")
        call_command('loaddata', 'modes')
        call_command('loaddata', 'operators')
        call_command('loaddata', 'satelliteidentifiers')
        call_command('loaddata', 'satelliteentries')
        call_command('loaddata', 'satellites')
        call_command('loaddata', 'transmitters')
        call_command('loaddata', 'telemetries')
        self.stdout.write("Fetching TLEs...")
        call_command('update_all_tle')

        # Create superuser
        self.stdout.write("Creating a superuser...")
        call_command('createsuperuser')
