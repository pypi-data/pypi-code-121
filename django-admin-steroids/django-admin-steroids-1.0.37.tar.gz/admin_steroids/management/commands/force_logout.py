import sys
import logging

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<user ids or emails>'
    help = 'Forces a specific user to log back in by deleting their session records.'

    def add_arguments(self, parser):
        parser.add_argument('users', nargs='*', help='User IDs or emails.')
        parser.add_argument('--all', action='store_true', default=False, help='If given, all users will be logged out.')

    def handle(self, *users, **options):
        if options['all']:
            # Logout all users.
            qs = Session.objects.all()
            total = qs.count()
            i = 0
            for r in qs.iterator():
                i += 1
                sys.stdout.write(f'\rDeleting session {i} of {total}...')
                sys.stdout.flush()
                r.delete()
            print('')

        else:
            # Logout only specific users.
            users = options['users']
            for user in users:

                logger.info('Looking up user %s...', user)
                if user.isdigit():
                    user = get_user_model().objects.get(id=int(user))
                else:
                    user = get_user_model().objects.get(email=user)

                qs = Session.objects.all()
                total = qs.count()
                i = 0
                for s in qs.iterator():
                    i += 1
                    sys.stdout.write(f'\rChecking user session {i} of {total}...')
                    sys.stdout.flush()
                    if s.get_decoded().get('_auth_user_id') == user.id:
                        s.delete()

        logger.info('Done!')
