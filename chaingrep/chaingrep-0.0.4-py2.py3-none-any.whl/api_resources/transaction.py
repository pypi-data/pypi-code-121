from chaingrep.api_resources.requester import Requester
from chaingrep.exceptions import InvalidTransactionHashError, TransactionParsingError, TransactionSimulationError


class Transaction:
    def __init__(self, transaction_hash, auth):
        self.transaction_hash = transaction_hash
        self.auth = auth

        transaction_hash_len = len(transaction_hash)
        transaction_hash_prefix = transaction_hash[0:2]

        if transaction_hash_len != 66:
            raise InvalidTransactionHashError("Transaction hash must have 66 characters.")

        if transaction_hash_prefix != "0x":
            raise InvalidTransactionHashError("Transaction hash must start with '0x'.")

    def parse(self):
        method_endpoint = f"/transaction/{self.transaction_hash}"
        parsed_transaction = Requester(self.auth).get(method_endpoint)

        status_code = parsed_transaction.get("status_code")
        response = parsed_transaction.get("response")

        if status_code != 200:
            raise TransactionParsingError(f"{response}.")

        return response


class RawTransaction:
    def __init__(self, raw_transaction, auth):
        self.raw_transaction = dict(raw_transaction)
        self.auth = auth

    def simulate(self):
        method_endpoint = "/transaction/simulation"
        response = Requester(self.auth).post(method_endpoint, body=self.raw_transaction)

        status_code = response.get("status_code")
        response = response.get("response")

        if status_code != 200:
            raise TransactionSimulationError(response)

        return response
