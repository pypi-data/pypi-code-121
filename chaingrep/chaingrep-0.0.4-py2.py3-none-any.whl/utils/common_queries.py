from chaingrep.api_resources.query import Query
from chaingrep.utils.query_utils import operator


class CommonQueries:
    def __init__(self, auth):
        self.auth = auth
        self.query = Query(self.auth)

    def most_expensive_transaction(self, account):
        # ETH transaction
        self.query.query({"account": account, "gas_used": "21000"})
        most_expensive_ether_transaction = self.query.execute(sort=["gas_price", "descending"])
        most_expensive_ether_transaction = most_expensive_ether_transaction[0]

        # non-ETH transaction
        self.query.query({"account": account, "gas_used": operator.not_equal("21000")})
        most_expensive_non_ether_transaction = self.query.execute(sort=["gas_price", "descending"])
        most_expensive_non_ether_transaction = most_expensive_non_ether_transaction[0]

        transactions = {
            "ether_transaction": most_expensive_ether_transaction,
            "non_ether_transaction": most_expensive_non_ether_transaction,
        }

        return transactions

    def first_transaction(self, account):
        # ETH transaction
        self.query.query({"account": account, "gas_used": "21000"})
        first_ether_transaction = self.query.execute(sort=["timestamp", "ascending"])
        first_ether_transaction = first_ether_transaction[0]

        # non-ETH transaction
        self.query.query({"account": account, "gas_used": operator.not_equal("21000")})
        first_non_ether_transaction = self.query.execute(sort=["timestamp", "ascending"])
        first_non_ether_transaction = first_non_ether_transaction[0]

        transactions = {
            "ether_transaction": first_ether_transaction,
            "non_ether_transaction": first_non_ether_transaction,
        }

        return transactions

    # pylint: disable=inconsistent-return-statements
    def largest_eth_amount_received(self, account):
        self.query.query({"account": account, "gas_used": "21000"})
        largest_eth_amount = self.query.execute(sort=["value", "descending"])

        for transaction in largest_eth_amount:
            if account.lower() == transaction.get("transaction_metadata").get("to").lower():
                return transaction
