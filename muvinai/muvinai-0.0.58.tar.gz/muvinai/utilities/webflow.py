import requests
from pprint import pprint

# ASOCIATE ENVIRONMENT - PRODUCTION
apikey = '700df702fdaee7e441b3d57d712e05cd70687c6bf6ff7898d505132c7b0f1255'
asociate_id = '6006f5bf87d96d2131258ef0'


header = {"Authorization": "Bearer " + apikey,
          "accept-version": "1.0.0",
          "Content-Type": "application/json",
          "Accept": "*/*",
          "Cache-Control": "no-cache",
          "Host": "api.webflow.com",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive"}


url = 'https://api.webflow.com/'


def get_collections():
    r = requests.get(url + f'sites/{asociate_id}/collections', headers=header)
    return r.json()


def get_schema(collection_id):
    r = requests.get(url + f'collections/{collection_id}', headers=header)
    return r.json()


def get_sites():
    r = requests.get(url + 'sites', headers=header)
    return r.text


def get_items(collection_id):
    r = requests.get(url + f'collections/{collection_id}/items', headers=header)
    response = r.json()
    items = response["items"]
    missing_items = response["total"] - response["count"]
    reached_items = response["count"]
    while missing_items > 0:
        offset = reached_items
        r = requests.get(url + f'collections/{collection_id}/items?offset={offset}', headers=header)
        response = r.json()
        missing_items = missing_items - response["count"]
        reached_items = reached_items + response["count"]
        items.extend(response["items"])
    return items


def get_item(collection_id, item_id):
    r = requests.get(url + f'collections/{collection_id}/items/{item_id}', headers=header)
    response = r.json()
    return response

