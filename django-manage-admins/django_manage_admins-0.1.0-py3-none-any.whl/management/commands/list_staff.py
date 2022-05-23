from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "list active staff"

    def handle(self, *args, **options):
        User = get_user_model()
        staff = User.objects.filter(is_staff=True, is_active=True).order_by("username")
        self.stdout.write("\n".join([s.username for s in staff]))
