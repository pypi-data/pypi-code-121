from chaingrep.api_resources import Account, Query, Transaction
from chaingrep.auth import ChaingrepAuth


class Chaingrep:
    def __init__(self, api_key):
        self.auth = ChaingrepAuth(api_key=api_key)

    def transaction(self, transaction_hash):
        return Transaction(transaction_hash, self.auth)

    def account(self, address):
        return Account(address, self.auth)

    def query(self):
        return Query(self.auth)
