'''
  DjangoLDP Check Integrity
  Usage `./manage.py check_integrity --help`
'''
from django.apps import apps
from django.conf import settings
from djangoldp.models import LDPSource
from urllib.parse import urlparse
import requests

# Helper command for argument type checking
def is_string(target):
  if isinstance(target, str):
    return target
  return False

# Helper command to check status code of a target
def is_alive(target, status_code = 200):
  return requests.get(target).status_code == status_code

# Add argument to the `check_integrity` command
def add_arguments(parser):
  parser.add_argument(
    "--ignore",
    action="store",
    default=False,
    type=is_string,
    help="Ignore any server, comma separated",
  )
  parser.add_argument(
    "--ignore-faulted",
    default=False,
    nargs="?",
    const=True,
    help="Ignore eventual faulted",
  )
  parser.add_argument(
    "--ignore-404",
    default=False,
    nargs="?",
    const=True,
    help="Ignore eventual 404",
  )
  parser.add_argument(
    "--fix-faulted-resources",
    default=False,
    nargs="?",
    const=True,
    help="Fix faulted resources",
  )
  parser.add_argument(
    "--fix-404-resources",
    default=False,
    nargs="?",
    const=True,
    help="Fix 404 resources",
  )
  parser.add_argument(
    "--fix-offline-servers",
    default=False,
    nargs="?",
    const=True,
    help="Remove resources from offline servers",
  )

# Define our own checks
def check_integrity(options):

  models = apps.get_models()

  ignored = set()
  if(options["ignore"]):
    for target in options["ignore"].split(","):
      ignored.add(urlparse(target).netloc)

  if(len(ignored) > 0):
    print("Ignoring servers:")
    for server in ignored:
      print("- "+server)

  resources = set()
  resources_map = dict()
  base_urls = set()

  for model in models:
    for obj in model.objects.all():
      if hasattr(obj, "urlid"):
        if(obj.urlid):
          if(not obj.urlid.startswith(settings.BASE_URL)):
            url = urlparse(obj.urlid).netloc
            if(url not in ignored):
              resources.add(obj.urlid)
              resources_map[obj.urlid] = obj
              base_urls.add(url)

  if(len(base_urls) > 0):
    print("Found "+str(len(resources_map))+" distant resources on "+str(len(models))+" models")
    print("Servers that I have backlinks to:")
    for server in base_urls:
      print("- "+server)
  else:
    print("I don't have any backlink")

  source_urls = set()
  for source in LDPSource.objects.all():
    source_urls.add(urlparse(source.urlid).netloc)

  if(len(source_urls) > 0):
    print("Servers that I'm allowed to get federated to:")
    for server in source_urls:
      print("- "+server)
  else:
    print("I'm not federated")

  difference_servers = base_urls.difference(source_urls)
  if(len(difference_servers) > 0):
    print("Servers that I should not get aware of:")
    for server in difference_servers:
      print("- "+server)

    # Handle faulted resources
    if(not options["ignore_faulted"]):
      faulted_resources = set()
      for server in difference_servers:
        for resource in resources:
          if(urlparse(resource).netloc in server):
            faulted_resources.add(resource)

      if(len(faulted_resources) > 0):
        print("Resources in fault:")
        for resource in faulted_resources:
          print("- "+resource)
      else:
        print("No resource are in fault")

      if(options["fix_faulted_resources"]):
        for resource in faulted_resources:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed faulted resources")
      else:
        print("Fix them with `./manage.py check_integrity --fix-faulted-resources`")
  else:
    print("I accept datas for every of those servers")

  # Handle 404 resources
  if(not options["ignore_404"]):
    resources_404 = set()
    resources_servers_offline = set()
    for resource in resources:
      try:
        if(is_alive(resource, 404)):
          resources_404.add(resource)
      except:
        resources_servers_offline.add(resource)

    if(len(resources_404) > 0):
      print("Faulted resources, 404:")
      for resource in resources_404:
        print("- "+resource)
      if(options["fix_404_resources"]):
        for resource in resources_404:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed 404 resources")
      else:
        print("Fix them with `./manage.py check_integrity --fix-404-resources`")

    if(len(resources_servers_offline) > 0):
      print("Faulted resources, servers offline:")
      for resource in resources_servers_offline:
        print("- "+resource)
      if(options["fix_offline_servers"]):
        for resource in resources_servers_offline:
          try:
            resources_map[resource].delete()
          except:
            pass
        print("Fixed resources on offline servers")
      else:
        print("Fix them with `./manage.py check_integrity --fix-offline-servers`")

    else:
      print("No 404 in known resources")