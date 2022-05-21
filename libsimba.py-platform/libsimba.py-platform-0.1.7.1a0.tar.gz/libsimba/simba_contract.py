import json
from typing import List, Optional, Any, Dict
from libsimba.decorators import filter_set
from libsimba.simba_request import SimbaRequest
from libsimba.param_checking_contract import ParamCheckingContract


class SimbaContract(ParamCheckingContract):
    def __init__(self, base_api_url: str, app_name: str, contract_name: str):
        self.app_name = app_name
        self.contract_name = contract_name
        SimbaRequest.base_api_url = base_api_url
        self.contract_uri = "{}/contract/{}".format(self.app_name, self.contract_name)
        self.metadata = self.get_metadata()
        self.params_restricted = self.param_restrictions()

    
    def query_method(self, query_args: dict, method_name: str):
        """
        Query transactions by method

        :param method_name: The method name
        :type method_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of transaction details
        :rtype: List[json]
        """
        return SimbaRequest(
            "v2/apps/{}/{}/".format(self.contract_uri, method_name), query_args
        ).send()

    def call_method(
        self, method_name: str, inputs: dict, query_args: Optional[dict] = None
    ):
        """
        Call a contract method

        :param method_name: The method name
        :type method_name: str
        :param inputs: The method arguments
        :type inputs: dict

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        query_args = query_args or {}
        self.validate_params(method_name, inputs)
        return SimbaRequest(
            "v2/apps/{}/{}/".format(self.contract_uri, method_name),
            query_args,
            method="POST",
        ).send(json_payload=json.dumps(inputs))

    # Example files: files = {'file': open('report.xls', 'rb')}
    def call_contract_method_with_files(
        self,
        method_name: str,
        inputs: dict,
        files: Optional[dict] = None,
        query_args: Optional[dict] = None,
    ):
        """
        Call a contract method and upload off-chain files

        :param method_name: The method name
        :type method_name: str
        :param inputs: The method arguments
        :type inputs: dict
        :param files: The files in the form of {'file_1': '<raw binary>'}
        :type files: dict

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        query_args = query_args or {}
        self.validate_params(method_name, inputs)
        return SimbaRequest(
            "v2/apps/{}/{}/".format(self.contract_uri, method_name),
            query_args,
            method="POST",
        ).send(json_payload=json.dumps(inputs), files=files)

    @filter_set
    def get_transactions(self, query_args: Optional[dict] = None):
        """
        List all transactions

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of transaction details
        :rtype: List[json]
        """
        query_args = query_args or {}
        return SimbaRequest(
            "v2/apps/{}/transactions/".format(self.contract_uri), query_args
        ).send()

    def query_events(self, event_name: str, query_args: Optional[dict] = None):
        query_args = query_args or {}
        return SimbaRequest(
            "v2/apps/{}/events/{}/".format(self.contract_uri, event_name), query_args
        ).send()

    def validate_bundle_hash(self, bundle_hash: str, query_args: Optional[dict] = None):
        """
        Validate a previously created bundle using the contract name and bundle hash. This will examine the bundle manifest and the file hashes defined in it against the files in off chain storage, ensuring that all the referenced data has not been tampered with. The errors element will contain any validation errors encountered.

        :param bundle_hash: The hash or UUID of the bundle
        :type bundle_hash: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: An object containing any errors if the validation has failed.
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "v2/apps/{}/validate/{}/{}".format(
                self.app_name, self.contract_name, bundle_hash
            ),
            query_args,
        ).send()

    @filter_set
    def get_transaction_statuses(
        self, txn_hashes: List[str] = None, query_args: Optional[dict] = None
    ):
        """
        List all transactions

        This function expects either a SearchFilter with the search term `transaction_hash__in`. Example:

        search_filter = SearchFilter(transaction_hash__in='hash1,hash2,hash3')

        Or a list of txn hashes.

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``)
            * *txn_hashes* (``List[str]``)
        :return: List of transaction status details
        :rtype: List[json]
        """
        query_args = query_args or {}
        if isinstance(txn_hashes, str):
            txn_hashes = [txn_hashes]
        if "filter[transaction_hash.in]" not in query_args and txn_hashes:
            query_args["filter[transaction_hash.in]"] = ",".join(txn_hashes)
        return SimbaRequest(
            "v2/apps/{}/contract/{}/transactions".format(
                self.app_name, self.contract_name
            ),
            query_args,
        ).send()
