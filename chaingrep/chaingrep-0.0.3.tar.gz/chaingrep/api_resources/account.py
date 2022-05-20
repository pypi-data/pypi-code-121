from chaingrep.api_resources.requester import Requester
from chaingrep.exceptions import AccountParsingError, InvalidAccountError


class Account:
    def __init__(self, account, auth):
        self.account = account
        self.auth = auth

        account_len = len(account)
        account_prefix = account[0:2]

        if account_len != 42:
            raise InvalidAccountError("Account must have 42 characters.")

        if account_prefix != "0x":
            raise InvalidAccountError("Account must start with '0x'.")

    def parse_transactions(self, start=0):
        if start > 990:
            raise AccountParsingError("The maximum value for the start parameter is 990 (10000 transactions).")

        method_endpoint = f"/account/{self.account}/transactions"
        parsed_transactions = Requester(self.auth).get(method_endpoint, params={"start": start})

        status_code = parsed_transactions.get("status_code")
        response = parsed_transactions.get("response")

        if status_code != 200:
            raise AccountParsingError(response)

        return response
