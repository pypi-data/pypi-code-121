import json

from django.core.management.base import BaseCommand, CommandError

from story.models import Story


class Command(BaseCommand):
    help = 'Exports a story for the cordova app'

    def handle(self, *args, **options):
        stories = []
        for story in Story.objects.all():
            stories.append(story.to_dict())

        with open("client/www/stories.json", "w") as fh:
            fh.write(json.dumps(stories))
