import json

import hashflow.util as utils
from hashflow.main import Main



class Client(object):
  
    def __init__(
        self,
        private_key,
        network_id,
        node=None
    ):
        self.private_key = utils.normalize_private_key(private_key)
        self.public_address = utils.private_key_to_address(self.private_key)
        self.network_id = network_id
        self.main = Main(
            node=node,
            private_key=self.private_key,
            public_address=self.public_address,
            network_id=self.network_id
        )
