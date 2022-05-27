import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hashflow.client import Client

OPERATIONS_ADDRESS = '0x70997970c51812dc3a010c7d01b50e0d17dc79c8'
OPERATIONS_PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'

SIGNER_ADDRESS = '0x90f79bf6eb2c4f870365e785982e1f101e93b906'
SIGNER_PRIVATE_KEY = '0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6'

LOCALHOST_NETWORK_ID = 31337
LOCALHOST_NODE = 'http://127.0.0.1:8545'

hashflow = Client(
  private_key=OPERATIONS_PRIVATE_KEY,
  network_id=LOCALHOST_NETWORK_ID,
  node=LOCALHOST_NODE
)

def test_private_pool_creation():
  hashflow.main.factory.create_pool(
    name='testpool1',
    signer=SIGNER_ADDRESS,
  )

def test_get_pools():
  pools = hashflow.main.factory.get_pools(OPERATIONS_ADDRESS)
  assert len(pools) == 1