"""
Projectal profiles serve as an all-purpose key-value store for clients
to store any kind of data that interests them, targeting a specific
entity uuId (similar to metadata in other systems).

Writes always override the old dictionary entirely, so be sure to
always include the whole data instead of updating only the values
you have changed.

Notes on implementation:
Each profile has its own uuId. The profile API allows you to create
an unlimited list of profiles for the key combination; this library
abstracts away that concept and enforces only a single dictionary
with get/set functions for that key combination. This assumption
may not hold if that key combination is modified externally.
"""

from projectal import api


def get(category_key, folder_key, uuId):
    profiles = __profile_list(category_key, folder_key, uuId)
    if len(profiles) > 0:
        return profiles[0]
    else:
        # Create on first access (new profile has a uuId)
        profile = {}
        response = __profile_add(category_key, folder_key, uuId, {})
        profile['uuId'] = response[0]['uuId']
        return profile


def set(category_key, folder_key, uuId, payload):
    # Get the first profile and save to it. If one doesn't exist, create it.
    profiles = __profile_list(category_key, folder_key, uuId)
    if len(profiles) > 0:
        payload['uuId'] = profiles[0]['uuId']
        return __profile_update(category_key, folder_key, uuId, payload)

    # Create and add in one step
    response = __profile_add(category_key, folder_key, uuId, payload)
    payload['uuId'] = response[0]['uuId']
    return payload


def __profile_add(category_key, folder_key, uuId, payload):
    endpoint = '/api/profile/{}/{}/{}/add'.format(category_key, folder_key, uuId)
    return api.__request('post', endpoint, [payload])


def __profile_delete(category_key, folder_key, uuId):
    endpoint = '/api/profile/{}/{}/{}/delete'.format(category_key, folder_key, uuId)
    return api.__request('post', endpoint)


def __profile_update(category_key, folder_key, uuId, payload):
    endpoint = '/api/profile/{}/{}/{}/update'.format(category_key, folder_key, uuId)
    return api.__request('put', endpoint, [payload])


def __profile_list(category_key, folder_key, uuId):
    endpoint = '/api/profile/{}/{}/{}/list'.format(category_key, folder_key, uuId)
    return api.__request('get', endpoint)

