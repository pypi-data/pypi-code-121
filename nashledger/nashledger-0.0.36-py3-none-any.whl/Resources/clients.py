from erp_sync.Resources.resource import Resource
from erp_sync.Resources.client_types import ClientTypes
from erp_sync.Resources.customer import Customer
from erp_sync.Resources.company import Company
from erp_sync.Resources.items import Items
from erp_sync.Resources.taxes import Taxes
from erp_sync.Resources.chart_of_accounts import ChartOfAccounts
from erp_sync.Resources.currencies import Currencies
from erp_sync.Resources.bank_accounts import BankAccounts
from erp_sync.Resources.bank_transactions import BankTransactions
from erp_sync.Resources.bank_transfers import BankTransfers
from erp_sync.Resources.payments import Payments
from erp_sync.Resources.bill_payments import BillPayments
from erp_sync.Resources.bill_invoices import BillInvoices
from erp_sync.Resources.invoices import Invoices
from erp_sync.Resources.users import Users
from erp_sync.Resources.records import Records
from erp_sync.Resources.uploads import Uploads
from erp_sync.Resources.banks import Banks
from erp_sync.Resources.vendors import Vendors

class Client(Resource):

    _resources = {
        "ClientTypes": ClientTypes(),
        "Customer": Customer(),
        "Vendors": Vendors(),
        "Company": Company(),
        "Items": Items(),
        "Taxes": Taxes(),
        "ChartOfAccounts": ChartOfAccounts(),
        "Currencies": Currencies(),
        "Banks": Banks(),
        "BankAccounts": BankAccounts(),
        "BankTransactions": BankTransactions(),
        "BankTransfers": BankTransfers(),
        "Payments": Payments(),
        "BillPayments": BillPayments(),
        "BillInvoices": BillInvoices(),
        "Invoices": Invoices(),
        "Users": Users(),
        "Records": Records(),
        "Uploads": Uploads()
    }

    # use the nash object to confirm if the user accessing the client is logged in
    _nash = None

    urls = {}

    def __init__(self, nash, client_id=-1):
        self._nash = nash
        self._resources["Users"] = Users(self._nash)
        super().__init__("ClientsAPI", self._nash.get_headers(), self._nash.get_params())
        self.set_client_id(client_id)
        self._set_urls()

    def resource(self, resource_name):
        resource = self._resources[resource_name].set_client_id(super().get_client_id(
        )).set_company_id(super().get_company_id()).set_client_type(super().get_client_type())

        if resource_name == "Uploads":

            headers = self._nash.get_headers()

            if isinstance(headers, dict):
                if 'Content-Type' in headers.keys():
                    headers.pop("Content-Type")

            resource.set_headers(headers)
        else:
            resource.set_headers(self._nash.get_headers())

        return resource

    def get_resources(self):
        return list(self._resources.keys())

    def _set_urls(self):

        self.urls = {
            "new": f"/clients",
            "edit": f"/clients/{super().get_client_id()}",
            "read": f"/clients",
            "delete": f"/clients/{super().get_client_id()}",
        }

        super().set_urls(self.urls)

        return self

    def delete(self, payload=None, erp_id=None):

        self._set_urls()

        if erp_id is not None:
            self.urls["edit"] = f'{self.urls["edit"]}/{erp_id}'
            super().set_urls(self.urls)

        return super().delete(payload)

    def edit(self, payload=None, erp_id=None, method='PUT', endpoint=None):

        self._set_urls()

        if erp_id is not None:
            self.urls["edit"] = f'{self.urls["edit"]}/{erp_id}'
            super().set_urls(self.urls)

        return super().edit(payload)

    def read(self, erp_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if erp_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{erp_id}'
            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

    def new(self, payload=None, method='POST', endpoint="/clients", add_client=True):
        # set data to pass to ruby url
        # set response here
        # set client id here
        # self.set_client_id()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        response = super().new(payload, method, endpoint).response()
        if response["status_code"] == 200:

            self.set_client_id(response["response_data"]["id"])

            self._set_urls()

            # if add_client:
            #     response["add_client"] = self._nash.user().add_client(
            #         payload={
            #             "client_id": [super().get_client_id()]
            #         }
            #     ).response()

            #     response["add_company"] = self._nash.user().add_company(
            #         payload={
            #             "company_id": [super().get_company_id()]
            #         }
            #     ).response()

            super().set_response(response)

        return self

    def get_callback_url(self, erp_id=None, payload=None, method='GET', endpoint='/authenticate/url'):

        if erp_id is None:

            erp_id = super().get_client_id()

        return super().read(payload, method, endpoint=f'{self.urls["new"]}/{erp_id}{endpoint}')

    def get_webhook_url(self, erp_id=None, payload=None, method='GET', endpoint='/hooks/url'):

        if erp_id is None:

            erp_id = super().get_client_id()

        return super().read(payload, method, endpoint=f'{self.urls["new"]}/{erp_id}{endpoint}')

    def authenticate(self, erp_id=None, payload=None, method='POST', endpoint='/authenticate'):

        if erp_id is None:

            erp_id = super().get_client_id()

        return super().read(payload, method, endpoint=f'{self.urls["new"]}/{erp_id}{endpoint}')

    def check_token(self, erp_id=None, payload=None, method='GET', endpoint='/authenticate/token'):

        if erp_id is None:

            erp_id = super().get_client_id()

        return super().read(payload, method, endpoint=f'{self.urls["new"]}/{erp_id}{endpoint}')

    def client_types(self, client_type_id=None):

        return self.resource("ClientTypes").read(client_type_id=client_type_id)

    def set_company_id(self, company_id=None):

        if company_id is not None:
            response = self.resource("Company").read(
                company_id=company_id).response()

            if bool(response):
                super().set_client_id(response.get("client_id", None))
                super().set_client_type(response.get("client_type_id", None))
                self._set_urls()

        return super().set_company_id(company_id)
