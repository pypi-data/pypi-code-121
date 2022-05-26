from nova.api.nova_client import NovaClient
from decouple import config

nova_client = NovaClient(config('NovaAPISecret'))

name = ''
candle = ''
exp_return = 0.0
real_return = 0.0


# Create
nova_client.create_strategy(
    name=name,
    candle=candle,
    avg_return_e=exp_return,
    avg_return_r=real_return
)

# Read
nova_client.read_strategy()

# Update
nova_client.update_strategy()

# Delete
nova_client.delete_strategy()
