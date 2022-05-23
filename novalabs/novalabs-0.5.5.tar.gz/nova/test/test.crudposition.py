from nova.api.nova_client import NovaClient
from decouple import config

nova_client = NovaClient(config('NovaAPISecret'))


data = nova_client.read_positions()



for x in data['positions']:
    nova_client.delete_positions(x['_id'])

