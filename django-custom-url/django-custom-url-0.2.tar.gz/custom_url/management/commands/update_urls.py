import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from custom_url.models import CustomUrl


class Command(BaseCommand):
    help = 'Create or update urls.py with the urls created in the database'

    def handle(self, *args, **options):
        q = CustomUrl.objects.all()
        try:
            with open(os.path.join(Path(__file__).resolve().parent.parent.parent, 'urls.py'), 'w+') as f:
                f.write(f'from django.urls import path\n')
                f.write(f'from custom_url import views\n\n')
                f.write(f'urlpatterns = [\n')
                for url in q:
                    f.write(f"\tpath('{url.url}', views.CustomUrlView.as_view()),\n")
                f.write(f']\n')
            
            self.stdout.write(self.style.SUCCESS('custom_url urls.py was updated'))

        except:
            self.stderr.write(self.style.ERROR("urls.py couldn't be opened"))
            raise CommandError("urls.py couldn't be opened")