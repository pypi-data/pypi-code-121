'''
  DjangoLDP Check Integrity Command & Importer
  Usage `./manage.py check_integrity --help`

  This command does import every `check_integrity.py` of every DJANGOLDP_PACKAGES
  Allowed methods:
    `add_arguments(parser)`: Allows to create new arguments to this command
    `check_integrity(options)`: Do your own checks on the integrity
  
  Examples on `djangoldp/check_integrity.py`
'''

from django.core.management.base import BaseCommand
from django.conf import settings
from importlib import import_module
import requests

class Command(BaseCommand):
  help = "Check the datas integrity"

  def add_arguments(self, parser):

    import_module('djangoldp.check_integrity').add_arguments(parser)

    for package in settings.DJANGOLDP_PACKAGES:
      try:
          import_module('{}.check_integrity'.format(package)).add_arguments(parser)
      except:
          pass

  def handle(self, *args, **options):

    import_module('djangoldp.check_integrity').check_integrity(options)

    for package in settings.DJANGOLDP_PACKAGES:
      try:
          import_module('{}.check_integrity'.format(package)).check_integrity(options)
      except:
          pass

    exit(0)
