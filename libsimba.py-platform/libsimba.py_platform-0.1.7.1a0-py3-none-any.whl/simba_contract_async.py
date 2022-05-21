import json
from typing import List, Optional
from libsimba.simba_request import SimbaRequest
from libsimba.simba_contract import SimbaContract


class SimbaContractAsync(SimbaContract):
    def __init__(self, base_api_url: str, app_name: str, contract_name: str):
        super().__init__(base_api_url, app_name, contract_name)
        self.async_contract_uri = "{}/async/contract/{}".format(
            self.app_name, self.contract_name
        )

    async def query_method(self, method_name: str, query_args: Optional[dict] = None):
        query_args = query_args or {}
        return await SimbaRequest(
            "v2/apps/{}/{}/".format(self.contract_uri, method_name), query_args
        ).send_async()

    async def call_method(
        self, method_name: str, inputs: dict, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        self.validate_params(method_name, inputs)
        return await SimbaRequest(
            "v2/apps/{}/{}/".format(self.async_contract_uri, method_name),
            query_args,
            method="POST",
        ).send_async(json_payload=json.dumps(inputs))

    # Example files: files = {'file': open('report.xls', 'rb')}
    async def call_contract_method_with_files(
        self,
        method_name: str,
        inputs: dict,
        files=None,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        self.validate_params(method_name, inputs)
        return await SimbaRequest(
            "v2/apps/{}/{}/".format(self.async_contract_uri, method_name),
            query_args,
            method="POST",
        ).send_async(json_payload=json.dumps(inputs), files=files)

    async def get_transactions(self, query_args: Optional[dict] = None):
        query_args = query_args or {}
        return await SimbaRequest(
            "v2/apps/{}/transactions/".format(self.contract_uri), query_args
        ).send_async()

    async def query_events(self, event_name: str, query_args: Optional[dict] = None):
        query_args = query_args or {}
        return await SimbaRequest(
            "v2/apps/{}/events/{}/".format(self.contract_uri, event_name), query_args
        ).send()

    async def validate_bundle_hash(
        self, bundle_hash: str, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "v2/apps/{}/validate/{}/{}".format(
                self.app_name, self.contract_name, bundle_hash
            ),
            query_args,
        ).send_async()

    async def get_transaction_statuses(
        self, txn_hashes: List[str] = None, query_args: Optional[dict] = None
    ):
        # transaction status for a list of txn hashes
        # filter[transaction_hash.in] can be a key in query_args, or the txn_hashes param
        # if filter is not in the query_args, and txn_hashes is given,
        # this method correctly formats the filter string in query_args
        query_args = query_args or {}
        if isinstance(txn_hashes, str):
            txn_hashes = [txn_hashes]
        if "filter[transaction_hash.in]" not in query_args and txn_hashes:
            query_args["filter[transaction_hash.in]"] = ",".join(txn_hashes)
        return await SimbaRequest(
            "v2/apps/{}/contract/{}/transactions".format(
                self.app_name, self.contract_name
            ),
            query_args,
        ).send_async()
