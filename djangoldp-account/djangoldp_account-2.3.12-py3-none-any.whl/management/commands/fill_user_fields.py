from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from djangoldp.models import Model

class Command(BaseCommand):
  help = 'Duplicate username on first and last name'

  def handle(self, *args, **options):
    first_name = 0
    last_name = 0
    for user in get_user_model().objects.all():
      if(not Model.is_external(user)):
        if(user.first_name == ""):
          first_name += 1
          user.first_name = user.username
        if(user.last_name == ""):
          last_name += 1
          user.last_name = user.username
        user.save()
        

    self.stdout.write(self.style.SUCCESS('Filled '+str(first_name)+' empty first names and '+str(last_name)+' empty last names.'))
