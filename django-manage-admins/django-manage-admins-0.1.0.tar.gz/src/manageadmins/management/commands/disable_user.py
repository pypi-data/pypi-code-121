from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "disable user"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        um = get_user_model()
        try:
            u = um.objects.get(username=options["username"])
            u.is_active = False
            u.save()
        except um.DoesNotExist:
            pass
