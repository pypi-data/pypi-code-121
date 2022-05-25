import urllib3
import json
site = urllib3.PoolManager()

def floorprice(collection):
    if collection == "":
        print('error while getting data, you have to provide collection name for example pysea.floorprice(collection="collection-name-here")')
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['floor_price'])
        except:
            print("Something went wrong while getting the data.")


def marketcap(collection):
    if collection == "":
        print("you have to provide collection name for example pysea.marketcap(collection='collection-name-here')")
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['market_cap'])
        except:
            print("Something went wrong while getting the data.")


def averageprice(collection):
    if collection == "":
        print('error while getting data, you have to provide collection name for example pysea.averageprice(collection="collection-name-here")')
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['average_price'])
        except:
            print("Something went wrong while getting the data.")

def totalsales(collection):
    if collection == "":
        print('error while getting data, you have to provide collection name for example pysea.totalsales(collection="collection-name-here")')
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['total_sales'])
        except:
            print("Something went wrong while getting the data.")

def numowners(collection):
    if collection == "":
        print('error while getting data, you have to provide collection name for example pysea.numowners(collection="collection-name-here")')
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['num_owners'])
        except:
            print("Something went wrong while getting the data.")


def sales(collection, time):
    if collection == "":
        print('error while getting data, you have to provide collection name for example pysea.sales(collection="collection-name-here")')
    else:
        try:
            collectioninfostats = site.request('GET', f'https://api.opensea.io/collection/{collection}/stats?format=json')
            print(json.loads(collectioninfostats.data.decode('utf-8'))['stats']['num_owners'])
        except:
            print("Something went wrong while getting the data.")


