'''File for handling all operations relating to the Bundle resource'''

import uuid
from fhir.resources.bundle import Bundle


def generateBundle(bundle_entries: list, type: str = 'collection') -> dict:
    '''Generate Bundle Resource from resource entries'''
    if type == 'transaction':
        formatted_entries = [{
            'fullUrl': entry['resourceType'] + '/' + entry['id'], 'resource': entry, 'request': {'method': 'POST', 'url': entry['resourceType']}
        } for entry in bundle_entries]
    else:
        formatted_entries = [{
            'fullUrl': entry['resourceType'] + '/' + entry['id'], 'resource': entry
        } for entry in bundle_entries]

    bundle_data = {
        'id': str(uuid.uuid4()),
        'type': type,
        'entry': formatted_entries
    }

    bundle_resource = Bundle(**bundle_data)
    return dict(bundle_resource.dict())
