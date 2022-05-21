from typing import Optional

from libsimba.simba_contract import SimbaContract
from libsimba.decorators import filter_set
from libsimba.settings import BASE_API_URL
from libsimba.simba_request import SimbaRequest

import logging

log = logging.getLogger(__name__)

# NOTE(Adam): Placed here for documentation
class QueryArgs(dict):
    """
    A python dict that may be passed to any of the simba client method calls
    If using filter sets, you should use the SearchFilter object instead

    :param format: "json"
    :type format: str
    :param limit: page size
    :type limit: int
    :param filter\[search\]: Example: filter[name__contains]=app_name
    """

    pass


class Simba:
    def __init__(self, base_api_url=BASE_API_URL):
        self.base_api_url = base_api_url  # TODO(Adam): Phase out
        SimbaRequest.base_api_url = base_api_url

    def whoami(self):
        """
        GET /user/whoami

        Retrieves information on the currently logged in user.

        :returns: User info as json
        :rtype: json
        """
        return SimbaRequest("user/whoami/", {}).send()

    def smart_contract_client(self, app_name: str, contract_name: str):
        """
        Instantiates a SimbaContract client which may be used to interact with the application smart contract and submit transactions to the blockchain.

        :param app_name: Name of the application. This must the common name and not the application UUID.
        :type app_name: str
        :type contract_name: str
        :param contract_name: Name of the contract.
        :returns: The instantiated client for the application's smart contract.
        :rtype: SimbaContract
        """
        return SimbaContract(self.base_api_url, app_name, contract_name)

    # -------------------------------------------------
    # All proceeding functions are general App getters
    # -------------------------------------------------
    """
    GET
    /v2/apps/
    list Application
    """

    @filter_set
    def list_applications(self, query_args: QueryArgs):
        """
        GET /v2/apps/

        List all applications

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of applications
        :rtype: json
        """
        return SimbaRequest("/v2/apps/", query_args).send()

    def get_application(self, app_id: str, query_args: Optional[QueryArgs] = None):
        """
        GET /v2/apps/{application}/

        Get application information

        :param app_id: Application id or name
        :type app_id: str
        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: application information
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest("/v2/apps/{}/".format(app_id), query_args).send()

    @filter_set
    def list_application_transactions(self, query_args: QueryArgs, app_id: str):
        """
        GET
        /v2/apps/{application}/transactions/

        List all transactions that have been submitted for the given application

        :param app_id: Application id or name
        :type app_id: str
        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of transactions
        :rtype: List[json]
        """
        return SimbaRequest(
            "/v2/apps/{}/transactions/".format(app_id), query_args
        ).send()

    def get_application_contract(
        self, app_id: str, contract_name: str, query_args: Optional[QueryArgs] = None
    ):
        """
        GET /v2/apps/{application}/contract/{contract_name}/

        Get contract metadata

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Information on the application contract
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/".format(app_id, contract_name), query_args
        ).send()

    @filter_set
    def list_contract_transactions(
        self, query_args: QueryArgs, app_id: str, contract_name: str
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/transactions/

        List contract transactions

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of cached transactions made against the contract
        :rtype: List[json]
        """
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/transactions/".format(app_id, contract_name),
            query_args,
        ).send()

    @filter_set
    def list_contracts(self, query_args, app_id: str):
        """
        GET
        /v2/apps/{application}/contracts/

        List contracts

        :param app_id: Application name
        :type app_id: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: Information on the application contract
        :rtype: List[json]
        """
        return SimbaRequest("/v2/apps/{}/contracts/".format(app_id), query_args).send()

    def validate_bundle(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/validate/{contract_name}/{bundle_hash}/

        Validate a previously created bundle using the contract name and bundle hash. This will examine the bundle manifest and the file hashes defined in it against the files in off chain storage, ensuring that all the referenced data has not been tampered with. The errors element will contain any validation errors encountered.

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
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
            "/v2/apps/{}/validate/{}/{}/".format(app_id, contract_name, bundle_hash),
            query_args,
        ).send()

    def get_bundle(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/

        get bundle BundleData

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param bundle_hash: The hash or UUID of the bundle
        :type bundle_hash: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Get bundle associated with the bundle hash
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/".format(
                app_id, contract_name, bundle_hash
            ),
            query_args,
        ).send()

    def get_bundle_file(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        file_name: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/filename/{file_name}/

        get bundle file BundleData

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param bundle_hash: The hash or UUID of the bundle
        :type bundle_hash: str
        :param file: The file name to fetch
        :type file: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Contents of the file
        :rtype: str
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/filename/{}/".format(
                app_id, contract_name, bundle_hash, file_name
            ),
            query_args,
        ).send()

    def get_manifest_for_bundle_from_bundle_hash(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/manifest/

        list bundle manifest BundleManifest

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param bundle_hash: The hash or UUID of the bundle
        :type bundle_hash: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Manifest object itemizing the files associated with the bundle hash
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/manifest/".format(
                app_id, contract_name, bundle_hash
            ),
            query_args,
        ).send()

    def list_contract_info(
        self, app_id: str, contract_name: str, query_args: Optional[QueryArgs] = None
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/info/

        Retrieve the Metadata Description for the contract

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Contract metadata
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/info".format(app_id, contract_name), query_args
        ).send()

    def get_instanced_contract(
        self,
        app_id: str,
        contract_name: str,
        contract_id: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/contracts/{contract_id}/

        Get detailed information about an instance of a given parent contract

        A deployed contract instance is a contract that is typically stateful, i.e., maintains properties or maps of data which has a parent contract. The parent provides the entry point for querying transactions that are submitted to instances that share the same parent. The parent contract API exposes a new endpoint which allows creating instances based on the parent. Instances can be invoked via the API endpoints that allow address or assetId identification. If an instance is created with an assetId constructor parameter, this can be used to identify the contract via the asset id value.

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The parent contract name
        :type contract_name: str
        :param contract_id: The instanced contract Id
        :type contract_id: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Contract metadata
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/contracts/{}/".format(
                app_id, contract_name, contract_id
            ),
            query_args,
        ).send()

    @filter_set
    def list_contract_instances(
        self, query_args: QueryArgs, app_id: str, contract_name: str
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/contracts/

        List contract instances

        A deployed contract instance is a contract that is typically stateful, i.e., maintains properties or maps of data which has a parent contract. The parent provides the entry point for querying transactions that are submitted to instances that share the same parent. The parent contract API exposes a new endpoint which allows creating instances based on the parent. Instances can be invoked via the API endpoints that allow address or assetId identification. If an instance is created with an assetId constructor parameter, this can be used to identify the contract via the asset id value.

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: A list of contract instances contained in the application
        :rtype: List[json]
        """
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/contracts/".format(app_id, contract_name),
            query_args,
        ).send()

    @filter_set
    def list_events(
        self, query_args: QueryArgs, app_id: str, contract_name: str, event_name: str
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/events/{event_name}/

        List all cached events for the given contract and event name

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param event_name: The event name
        :type event_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: A list of contract instances contained in the application
        :rtype: List[json]
        """
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/events/{}/".format(
                app_id, contract_name, event_name
            ),
            query_args,
        ).send()

    def get_receipt(
        self,
        app_id: str,
        contract_name: str,
        receipt_hash: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/receipt/{hash}/

        Get the receipt for a transaction

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param receipt_hash: The transaction or receipt hash (one and the same)
        :type receipt_hash: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction Receipt
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/receipt/{}/".format(
                app_id, contract_name, receipt_hash
            ),
            query_args,
        ).send()

    def get_transaction(
        self,
        app_id: str,
        contract_name: str,
        transaction_hash: str,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/transaction/{hash}/

        Get transaction details

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param transaction_hash: The transaction hash
        :type transaction_hash: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction details
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/transaction/{}/".format(
                app_id, contract_name, transaction_hash
            ),
            query_args,
        ).send()

    @filter_set
    def list_transactions_by_address(
        self,
        query_args: QueryArgs,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/address/{identifier}/{method_name}/

        List Transactions by address

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The contract address
        :type identifier: str
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
            "/v2/apps/{}/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
        ).send()

    def submit_transaction_by_address(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/contract/{contract_name}/address/{identifier}/{method_name}/

        Submit instance address method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The contract address
        :type identifier: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    @filter_set
    def list_transactions_by_asset(
        self,
        query_args: QueryArgs,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/asset/{identifier}/{method_name}/

        List transactions by asset

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The asset identifier
        :type identifier: str
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
            "/v2/apps/{}/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
        ).send()

    def submit_transaction_by_asset(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/contract/{contract_name}/asset/{identifier}/{method_name}/

        Submit instance asset method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The asset identifier
        :type identifier: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    @filter_set
    def list_transactions_by_method(
        self, query_args: QueryArgs, app_id: str, contract_name: str, method_name: str
    ):
        """
        GET
        /v2/apps/{application}/contract/{contract_name}/{method_name}/

        List contract methods

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param method_name: The method name
        :type method_name: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *search_filter* (``SearchFilter``) - Optional
        :return: List of transaction details
        :rtype: List[json]
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/{}/".format(app_id, contract_name, method_name),
            query_args,
        ).send()

    def submit_contract_method(
        self,
        app_id: str,
        contract_name: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/contract/{contract_name}/{method_name}/

        Submit a transaction to a contract method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/contract/{}/{}/".format(app_id, contract_name, method_name),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    def submit_transaction_by_address_async(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/async/contract/{contract_name}/address/{identifier}/{method_name}/

        Submit async instance address method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The contract address
        :type identifier: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/async/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    def submit_transaction_by_asset_async(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/async/contract/{contract_name}/asset/{identifier}/{method_name}/

        Submit async instance asset method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param identifier: The asset identifier
        :type identifier: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/async/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    def submit_contract_method_async(
        self,
        app_id: str,
        contract_name: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/async/contract/{contract_name}/{method_name}/

        post async method

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param method_name: The method name
        :type method_name: str
        :param inputs: Method arguments
        :type inputs: dict
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/async/contract/{}/{}/".format(
                app_id, contract_name, method_name
            ),
            query_args,
            method="POST",
        ).send(headers=headers, json_payload=inputs)

    def create_contract_instance(
        self,
        app_id: str,
        contract_name: str,
        query_args: Optional[QueryArgs] = None,
        sender_address: str = None,
    ):
        """
        POST
        /v2/apps/{application}/new/{contract_name}/

        create contract instance

        :param app_id: Application name
        :type app_id: str
        :param contract_name: The contract name
        :type contract_name: str
        :param sender_address: The user address for self signing
        :type sender_address: str

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        headers = {}
        if sender_address:
            headers["txn-sender"] = sender_address

        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/new/{}/".format(app_id, contract_name),
            query_args,
            method="POST",
        ).send(headers=headers)

    def submit_signed_transaction(
        self,
        app_id: str,
        txn_id: str,
        txn: dict,
        query_args: Optional[QueryArgs] = None,
    ):
        """
        POST
        /v2/apps/{application}/transactions/{identifier}/

        Submit signed transaction

        :param app_id: Application name
        :type app_id: str
        :param txn_id: The transaction Id that exists in the DB
        :type txn_id: str
        :param txn: The raw signed transaction
        :type txn: dict

        :param \**kwargs:
            See below

        :Keyword Arguments:
            * *query_args* (``QueryArgs``) - Optional
        :return: Transaction detail
        :rtype: json
        """
        query_args = query_args or {}
        return SimbaRequest(
            "/v2/apps/{}/transactions/{}/".format(app_id, txn_id),
            query_args,
            method="POST",
        ).send(json_payload={"transaction": txn})

    """
    POST
    /v2/apps/{application}/contract/{contract_name}/graphql/
    post gql search Application
    """
    # TODO(Adam): Add this library function for gql search
