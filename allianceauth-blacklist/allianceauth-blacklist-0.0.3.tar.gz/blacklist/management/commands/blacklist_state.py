from django.core.management.base import BaseCommand
from allianceauth.authentication.models import State
from django.db.models import Max
from blacklist import app_settings


class Command(BaseCommand):
    help = 'Setup/Reset/Fix the Blacklist State for the Blacklist Module'

    def handle(self, *args, **options):
        self.stdout.write("Creating/Reseting/Fixing the Blacklist State for the Blacklist Module")
        blacklist_name = app_settings.BLACKLIST_STATE_NAME
        max_prio = State.objects.all().exclude(name=blacklist_name).aggregate(max_prio=Max('priority'))["max_prio"]

        priority = 6969
        if max_prio > priority:
            priority = max_prio+100

        state, created = State.objects.update_or_create(name=blacklist_name,
                                                        defaults={
                                                            "priority": priority,
                                                        })
        if created:
            self.stdout.write("Success! Created Blacklist State")
        else:
            self.stdout.write("Success! Updated Blacklist State")
