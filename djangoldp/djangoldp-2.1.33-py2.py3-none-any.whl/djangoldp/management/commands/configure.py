from django.core import management
from django.conf import settings
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

class Command(BaseCommand):

    help = 'Initialize the DjangoLDP backend'

    def add_arguments(self, parser):

        """Define the same arguments as the ones in CLI."""

        parser.add_argument('--with-admin', nargs='?', type=str, help='Create an administrator user.')
        parser.add_argument('--email', nargs='?', type=str, help='Provide an email for administrator.')
        parser.add_argument('--with-dummy-admin', action='store_true', help='Create a default "admin" user with "admin" password.')

    def handle(self, *args, **options):

        """Wrapper command around default django initialization commands."""

        try:
            # migrate data
            management.call_command('migrate', interactive=False)

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Data migration failed: {e}'))

        if options['with_dummy_admin']:
            try:
                # create a default super user
                from django.contrib.auth import get_user_model
                User = get_user_model()
                User.objects.create_superuser('admin', 'admin@example.org', 'admin')

            except (ValidationError, IntegrityError):
                self.stdout.write('User "admin" already exists. Skipping...')
                pass

        elif options['with_admin']:
            try:
                # call default createsuperuser command
                management.call_command('createsuperuser', '--noinput', '--username', options['with_admin'], '--email', options['email'])

            except CommandError as e:
                self.stdout.write(self.style.ERROR(f'Superuser {e}'))
                pass

        #try:
        #    # creatersakey
        #    management.call_command('creatersakey', interactive=False)

        #except CommandError as e:
        #    self.stdout.write(self.style.ERROR(f'RSA key creation failed: {e}'))
