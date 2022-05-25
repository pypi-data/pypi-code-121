from nova.api.nova_client import NovaClient
from decouple import config
from binance.client import Client


nova_client = NovaClient(config('NovaAPISecret'))


# For testing
def get_binance_pairs():
    binance_client = Client(config("BinanceAPIKey"), config("BinanceAPISecret"))
    all_pair = binance_client.futures_position_information()
    list_pair = []
    for pair in all_pair:
        if 'USDT' in pair['symbol']:
            list_pair.append(pair['symbol'].replace('USDT', '/USDT'))
    return list_pair


# list_pair = get_binance_pairs()


# Create
def create_new_pair(pairs: list):
    for pair in pairs:
        nova_client.create_pairs(pair=pair)


# Read
def read_pairs():
    return nova_client.read_pairs()


# Update
def update_pairs():
    pass


# Delete
def delete_pair(pairs: list):
    for pair in pairs:
        nova_client.delete_pairs(pair_id=pair['_id'])
    pass





