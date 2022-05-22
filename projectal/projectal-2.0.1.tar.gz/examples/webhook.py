import os
from pprint import pprint

import projectal

projectal.api_base = os.environ.get('PROJECTAL_URL')
projectal.api_username = os.environ.get('PROJECTAL_USERNAME')
projectal.api_password = os.environ.get('PROJECTAL_PASSWORD')

print('Creating webhooks')
# Send event every time a project is created
projectal.Webhook.create({
    'entity': 'PROJECT',
    'action': 'CREATE',
    'url': 'https://webhook1.example.com'
})
# Send event every time a project is updated
projectal.Webhook.create({
    'entity': 'PROJECT',
    'action': 'UPDATE',
    'url': 'https://webhook1.example.com'
})

# See all existing webhooks
print('Listing webhooks')
for webhook in projectal.Webhook.list():
    pprint(webhook)

# This will trigger an event to https://webhook1.example.com
projectal.Project.create({'name': 'Test Webhook Project Create'})
# With a payload like this:
# {
#   "entity" : "PROJECT",
#   "action" : "CREATE",
#   "uuId" : "722f6388-7a68-401e-ade9-36f65c94ecb1",
#   "eventTime" : 1643862748949,
#   "author" : "9f4c6571-3615-437e-9ae3-ce25909481db"
# }

