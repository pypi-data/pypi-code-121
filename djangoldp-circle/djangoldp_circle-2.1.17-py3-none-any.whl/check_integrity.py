from django.conf import settings
from django.contrib.auth import get_user_model
from djangoldp_circle.models import CircleMember
from djangoldp.check_integrity import is_alive
from urllib.parse import urlparse

def add_arguments(parser):
  parser.add_argument(
    "--ignore-circle-members",
    default=False,
    nargs="?",
    const=True,
    help="Ignore circle members related check",
  )

def check_integrity(options):
  print('---')
  print("DjangoLDP Circle")
  if(not options["ignore_circle_members"]):

    ignored = set()
    if(options["ignore"]):
      for target in options["ignore"].split(","):
        ignored.add(urlparse(target).netloc)

    resources_404 = set()
    resources_servers_offline = set()
    resources_map = dict()

    for obj in CircleMember.objects.all():
      resources_map[obj.urlid] = obj
      if hasattr(obj, "user"):
        if(obj.user.urlid):
          if(not obj.user.urlid.startswith(settings.BASE_URL)):
            url = urlparse(obj.user.urlid).netloc
            if(url not in ignored):
              try:
                if(is_alive(obj.user.urlid, 404)):
                  resources_404.add(obj.urlid)
              except:
                resources_servers_offline.add(obj.urlid)
        else:
          resources_404.add(obj.urlid)
      if hasattr(obj, "circle"):
        if(obj.circle.urlid):
          if(not obj.circle.urlid.startswith(settings.BASE_URL)):
            url = urlparse(obj.circle.urlid).netloc
            if(url not in ignored):
              try:
                if(is_alive(obj.circle.urlid, 404)):
                  resources_404.add(obj.urlid)
              except:
                resources_servers_offline.add(obj.urlid)
        else:
          resources_404.add(obj.urlid)

    if(len(resources_404) > 0):
      print("Faulted circle memberships, 404:")
      for resource in resources_404:
        print("- "+resource)
      if(options["fix_404_resources"]):
        for resource in resources_404:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed 404 circle memberships")
      else:
        print("Fix them with `./manage.py check_integrity --fix-404-resources`")

    if(len(resources_servers_offline) > 0):
      print("Faulted circle memberships, servers offline:")
      for resource in resources_servers_offline:
        print("- "+resource)
      if(options["fix_offline_servers"]):
        for resource in resources_servers_offline:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed circle memberships on offline servers")
      else:
        print("Fix them with `./manage.py check_integrity --fix-offline-servers`")

    if(len(resources_servers_offline) == 0 and len(resources_404) == 0):
      print('Everything goes fine')

  else:
    print("Ignoring djangoldp-circle checks")