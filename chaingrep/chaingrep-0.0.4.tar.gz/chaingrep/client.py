from chaingrep.api_resources import Account, Fees, Query, RawTransaction, Transaction
from chaingrep.auth import ChaingrepAuth
from chaingrep.utils.common_queries import CommonQueries


class Chaingrep:
    def __init__(self, api_key):
        self.auth = ChaingrepAuth(api_key=api_key)

    def transaction(self, transaction_hash):
        return Transaction(transaction_hash, self.auth)

    def raw_transaction(self, transaction):
        return RawTransaction(transaction, self.auth)

    def account(self, address):
        return Account(address, self.auth)

    def query(self):
        return Query(self.auth)

    def common_queries(self):
        return CommonQueries(self.auth)

    def fees(self):
        return Fees(self.auth)
