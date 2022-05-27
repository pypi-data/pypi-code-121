from django.core.management.base import BaseCommand

from ...models import ContactSet


def get_input(text):
    """wrapped input to enable unit testing / patching"""
    return input(text)


class Command(BaseCommand):
    help = "Create standing request for alts with standing in game"

    def _create_requests(self):
        created_counter = (
            ContactSet.objects.latest().generate_standing_requests_for_blue_alts()
        )
        self.stdout.write(f"Created a total of {created_counter} standing requests.")

    def handle(self, *args, **options):
        self.stdout.write(
            "This command will automatically create accepted standings requests for "
            "alt characters on Auth that already have blue standing in-game."
        )
        user_input = get_input("Are you sure you want to proceed? (Y/n)?")
        if user_input == "Y":
            self.stdout.write("Starting update. Please stand by.")
            self._create_requests()
            self.stdout.write(self.style.SUCCESS("Process completed!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted"))
