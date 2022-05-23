import re
import requests
import uuid
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from urllib.parse import urlparse

class Command(BaseCommand):
  help = 'Create a distant user backlink and make it administrator'

  def add_arguments(self, parser):
    parser.add_argument('--urlid', type=str, default="null", help='Urlid of the distant user')

  def handle(self, *args, **options):
    if(options['urlid']):
      try:
        distant_request = requests.get(options['urlid'])
      except:
        self.stdout.write(self.style.ERROR('Error. '+options['urlid']+" is unreachable"))
        exit(1)
      if(distant_request.status_code == 404):
        self.stdout.write(self.style.ERROR('Error. '+options['urlid']+" is not found"))
        exit(1)
      else:
        try:
          distant_user = distant_request.json()
          urlid = distant_user['@id']
          email = distant_user['email']
          username = distant_user['username']
        except:
          self.stdout.write(self.style.WARNING('Error while reading '+options['urlid']))
          exit(1)
        try:
          netloc = re.sub(r'[\W_]+', '', urlparse(urlid).netloc)
          user = get_user_model().objects.update_or_create(
            urlid=urlid,
            defaults={
              'is_staff': True,
              'is_superuser': True,
              'email': email + "-" + netloc,
              'username': username + "-" + netloc
            }
          )
          self.stdout.write(self.style.SUCCESS('Successful created distant administrator: '+urlid))
        except:
          e
          self.stdout.write(self.style.WARNING('Unable to save '+urlid+" as administrator"))
        exit(0)
    else:
      self.stdout.write(self.style.WARNING('No urlid provided'))
      exit(1)
