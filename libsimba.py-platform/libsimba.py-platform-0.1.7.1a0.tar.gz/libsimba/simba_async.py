from typing import Optional

from libsimba.simba_contract_async import SimbaContractAsync
from libsimba.decorators import filter_set
from libsimba.settings import BASE_API_URL
from libsimba.simba_request import SimbaRequest
from libsimba.simba import Simba, QueryArgs

import logging

log = logging.getLogger(__name__)


class SimbaAsync(Simba):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def whoami(self):
        return await SimbaRequest("user/whoami/").send_async()

    def smart_contract_client(self, app_name, contract_name):
        return SimbaContractAsync(self.base_api_url, app_name, contract_name)

    # -------------------------------------------------
    # All proceeding functions are general App getters
    # -------------------------------------------------
    """
    GET
    /v2/apps/
    list Application
    """

    @filter_set
    async def list_applications(self, query_args: dict):
        return await SimbaRequest("/v2/apps/", query_args).send_async()

    """
    GET
    /v2/apps/{application}/
    retrieve Application
    """

    async def retrieve_application(
        self, app_id: str, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/".format(app_id), query_args
        ).send_async()

    """
    GET
    /v2/apps/{application}/transactions/
    list application transactions Transaction
    """

    @filter_set
    async def list_application_transactions(self, query_args: dict, app_id: str):
        return await SimbaRequest(
            "/v2/apps/{}/transactions/".format(app_id), query_args
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/
    get contract MetadataDeployedContract
    """

    async def get_application_contract(
        self, app_id: str, contract_name: str, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/".format(app_id, contract_name), query_args
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/transactions/
    list contract transactions Transaction
    """

    @filter_set
    async def list_contract_transactions(
        self, query_args: dict, app_id: str, contract_name: str
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/transactions/".format(app_id, contract_name),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contracts/
    list contracts ExtendedDeployedContract
    """

    @filter_set
    async def list_contracts(self, query_args: dict, app_id: str):
        return await SimbaRequest(
            "/v2/apps/{}/contracts/".format(app_id), query_args
        ).send_async()

    """
    GET
    /v2/apps/{application}/validate/{contract_name}/{bundle_hash}/
    validate bundle BundleValidation
    """

    async def validate_bundle(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/validate/{}/{}/".format(app_id, contract_name, bundle_hash),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/
    get bundle BundleData
    """

    async def get_bundle(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/".format(
                app_id, contract_name, bundle_hash
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/filename/{file_name}/
    get bundle file BundleData
    """

    async def get_bundle_file(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        file_name,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/filename/{}/".format(
                app_id, contract_name, bundle_hash, file_name
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/bundle/{bundle_hash}/manifest/
    list bundle manifest BundleManifest
    """

    async def get_manifest_for_bundle_from_bundle_hash(
        self,
        app_id: str,
        contract_name: str,
        bundle_hash: str,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/bundle/{}/manifest/".format(
                app_id, contract_name, bundle_hash
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/info/
    list contract info ContractInfo
    """

    async def list_contract_info(
        self, app_id: str, contract_name: str, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/info".format(app_id, contract_name), query_args
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/contracts/{contract_id}/
    get contract instance DeployedContractInstance
    """

    async def get_instanced_contract(
        self,
        app_id: str,
        contract_name: str,
        contract_id: str,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/contracts/{}/".format(
                app_id, contract_name, contract_id
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/contracts/
    list contract instances DeployedContractInstance
    """

    @filter_set
    async def list_contract_instances(
        self, query_args: dict, app_id: str, contract_name: str
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/contracts/".format(app_id, contract_name),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/events/{event_name}/
    list events TransactionEvent
    """

    @filter_set
    async def list_events(
        self, query_args: dict, app_id: str, contract_name: str, event_name: str
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/events/{}/".format(
                app_id, contract_name, event_name
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/receipt/{hash}/
    get receipt TransactionReceipt
    """

    async def get_receipt(
        self,
        app_id: str,
        contract_name: str,
        receipt_hash: str,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/receipt/{}/".format(
                app_id, contract_name, receipt_hash
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/transaction/{hash}/
    get transaction TransactionDetail
    """

    async def get_transaction(
        self,
        app_id: str,
        contract_name: str,
        transaction_hash: str,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/transaction/{}/".format(
                app_id, contract_name, transaction_hash
            ),
            query_args,
        ).send_async()

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/address/{identifier}/{method_name}/
    list instance address method ContractMethod
    """

    @filter_set
    async def list_transactions_by_address(
        self,
        query_args: QueryArgs,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
        ).send_async()

    """
    POST
    /v2/apps/{application}/contract/{contract_name}/address/{identifier}/{method_name}/
    post instance address method ContractMethod
    """

    async def submit_transaction_by_address(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/asset/{identifier}/{method_name}/
    list instance asset method ContractMethod
    """

    @filter_set
    async def list_transactions_by_asset(
        self,
        query_args: QueryArgs,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
        ).send_async()

    """
    POST
    /v2/apps/{application}/contract/{contract_name}/asset/{identifier}/{method_name}/
    post instance asset method ContractMethod
    """

    async def submit_transaction_by_asset(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    GET
    /v2/apps/{application}/contract/{contract_name}/{method_name}/
    list method ContractMethod
    """

    @filter_set
    async def list_transactions_by_method(
        self, query_args: QueryArgs, app_id: str, contract_name: str, method_name: str
    ):
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/{}/".format(app_id, contract_name, method_name),
            query_args,
        ).send_async()

    """
    POST
    /v2/apps/{application}/contract/{contract_name}/{method_name}/
    post method ContractMethod
    """

    async def submit_contract_method(
        self,
        app_id: str,
        contract_name: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/contract/{}/{}/".format(app_id, contract_name, method_name),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/async/contract/{contract_name}/address/{identifier}/{method_name}/
    post async instance address method ContractMethod
    """

    async def submit_transaction_by_address_async(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/async/contract/{}/address/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/async/contract/{contract_name}/asset/{identifier}/{method_name}/
    post async instance asset method ContractMethod
    """

    async def submit_transaction_by_asset_async(
        self,
        app_id: str,
        contract_name: str,
        identifier: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/async/contract/{}/asset/{}/{}/".format(
                app_id, contract_name, identifier, method_name
            ),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/async/contract/{contract_name}/{method_name}/
    post async method ContractMethod
    """

    async def submit_contract_method_async(
        self,
        app_id: str,
        contract_name: str,
        method_name: str,
        inputs: dict,
        query_args: Optional[dict] = None,
    ):
        return await SimbaRequest(
            "/v2/apps/{}/async/contract/{}/{}/".format(
                app_id, contract_name, method_name
            ),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/new/{contract_name}/
    create contract instance ContractInstance
    """

    async def create_contract_instance(
        self, app_id: str, contract_name: str, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            "/v2/apps/{}/new/{}/".format(app_id, contract_name),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/transactions/{identifier}/
    submit signed transaction SignedTransaction
    """
    # TODO(Adam): Make a transaction object to assist the user. Right now it's just a dict
    async def submit_signed_transaction(
        self, app_id: str, txn_id: str, txn: dict, query_args: Optional[dict] = None
    ):
        query_args = query_args or {}
        return await SimbaRequest(
            " /v2/apps/{}/transactions/{}/".format(app_id, txn_id),
            query_args,
            method="POST",
        ).send_async(json_payload=inputs)

    """
    POST
    /v2/apps/{application}/contract/{contract_name}/graphql/
    post gql search Application
    """
    # TODO(Adam): Add this library function for gql search
