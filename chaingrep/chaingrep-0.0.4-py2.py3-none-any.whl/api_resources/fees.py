from chaingrep.api_resources.requester import Requester


class Fees:
    def __init__(self, auth):
        self.auth = auth

    def next_block(self):
        method_endpoint = "/fees/estimation/next"
        parsed_transaction = Requester(self.auth).get(method_endpoint)

        response = parsed_transaction.get("response")

        return response
