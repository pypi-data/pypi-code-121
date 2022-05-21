import logging
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from j2fa.models import TwoFactorSession

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Resets 2FA attempt counter for a specific user"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("usernames", type=str, nargs="*")
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **kwargs):
        User = get_user_model()
        qs = User.objects.all()
        if kwargs["usernames"]:
            qs = qs.filter(username__in=kwargs["usernames"])
        elif not kwargs["all"]:
            print("Nothing to do: <usernames> or --all is required")
            return
        TwoFactorSession.objects.filter(user__in=qs).delete()
        logger.info("2FA sessions reset")
