import argparse
from django.core.management.base import BaseCommand
from django.conf import settings
from djangoldp.models import LDPSource

def isstring(target):
  if isinstance(target, str):
    return target
  return False

def list_models():
  # Improve me using apps.get_models()
  return {
    "circles": "/circles/",
    "circlesjoinable": "/circles/joinable/",
    "communities": "/communities/",
    "opencommunities": "/open-communities/",
    "communitiesaddresses": "/community-addresses/",
    "dashboards": "/dashboards/",
    "events": "/events/",
    "eventsfuture": "/events/future/",
    "eventspast": "/events/past/",
    "typeevents": "/typeevents/",
    "resources": "/resources/",
    "keywords": "/keywords/",
    "types": "/types/",
    "joboffers": "/job-offers/current/",
    "polls": "/polls/",
    "projects": "/projects/",
    "projectsjoinable": "/projects/joinable/",
    "skills": "/skills/",
    "users": "/users/"
  }

class Command(BaseCommand):
  help = 'Add another server to this one sources'

  def add_arguments(self, parser):
    parser.add_argument(
      "--target",
      action="store",
      default=False,
      type=isstring,
      help="Targeted server, format protocol://domain",
    )
    parser.add_argument(
      "--delete",
      default=False,
      nargs='?',
      const=True,
      help="Remove targeted source",
    )

  def handle(self, *args, **options):
    target = options["target"]
    models = list_models()
    if not target:
      target = settings.SITE_URL
    error_counter = 0
    if(options["delete"]):
      for attr, value in models.items():
        try:
          LDPSource.objects.filter(urlid=target+value, federation=attr).delete()
        except:
          error_counter += 1
      if error_counter > 0:
        self.stdout.write(self.style.ERROR("Can't remove: "+target))
        exit(2)
      else:
        self.stdout.write(self.style.SUCCESS("Successfully removed sources for "+target))
        exit(0)
    else:
      for attr, value in models.items():
        try:
          LDPSource.objects.create(urlid=target+value, federation=attr)
        except:
          error_counter += 1
      if error_counter > 0:
        self.stdout.write(self.style.WARNING("Source aleady exists for "+target+"\nIgnored "+str(error_counter)+"/"+str(len(models))))
        if error_counter == len(models):
          exit(1)
        exit(0)
      else:
        self.stdout.write(self.style.SUCCESS("Successfully created sources for "+target))
        exit(0)
