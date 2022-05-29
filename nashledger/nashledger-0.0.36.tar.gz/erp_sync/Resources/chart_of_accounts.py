from erp_sync.Resources.resource import Resource


class ChartOfAccounts(Resource):

    urls = {}

    def set_client_id(self, client_id):
        super().set_client_id(client_id)
        self._set_urls()
        return self

    def set_company_id(self, company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/chart_of_accounts",
            "edit": f"/companies/{super().get_company_id()}/chart_of_accounts",
            "read": f"/companies/{super().get_company_id()}/chart_of_accounts",
            "delete": f"/companies/{super().get_company_id()}/chart_of_accounts",
            "import": f"/companies/{super().get_company_id()}/import_chart_of_accounts"
        }

        super().set_urls(self.urls)

        return self

    def read(self, chart_of_account_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if chart_of_account_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{chart_of_account_id}'

            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method='DELETE', endpoint=None):

        self._set_urls()

        self.urls["delete"] = f'/{self.urls["delete"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().delete(payload, method, endpoint)

    def import_data(self, ledger_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)

        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "account_name": "<Enter unique name>",
            "account_type": "<Enter account type> e.g "
        }

        # If client type is Quickbooks Online
        if super().get_client_type() == super().QBO:

            data["account_type"] = f'{data ["account_type"]} Accounts Receivable'

        # If client type is ZOHO
        elif super().get_client_type() == super().ZOHO:

            data["account_type"] = f'{data ["account_type"]} cash'

        # If client type is XERO
        elif super().get_client_type() == super().XERO:

            data["account_type"] = f'{data ["account_type"]} CURRENT'

            data.update({
                        "additional_properties": {
                            "BankAccountNumber": "<required if account_type is BANK> e.g 19626"
                        }
                        })

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO:

                if 'account_name' in payload.keys():
                    data.update({
                        "Name": payload.get("account_name", "")
                    })

                if 'account_type' in payload.keys():
                    data.update({
                        "AccountType": payload.get("account_type", "")
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                data = payload

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                if operation == super().NEW:
                    data.update({
                        "Code": super().generate_code()
                    })
                elif operation == super().UPDATE:
                    if 'Code' in additional_properties.keys():
                        data.update({
                            "Code": additional_properties.get("Code", "")
                        })

                if 'account_name' in payload.keys():
                    data.update({
                        "Name": payload.get("account_name", "")
                    })

                if 'account_type' in payload.keys():
                    data.update({
                        "Type": payload.get("account_type", "")
                    })

                if 'Status' in additional_properties.keys():
                    data.update({
                        "Status": additional_properties.get("Status", "ACTIVE")
                    })

                    additional_properties.pop("Status")

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                if 'account_name' in payload.keys():
                    data.update({
                        "name": payload.get("account_name", "")
                    })
                if 'account_code' in payload.keys():
                    data.update({
                        "code": payload.get("account_code", "")
                    })
                if 'account_type' in payload.keys():
                    data.update({
                        "user_type_id": int(payload.get("account_type", 0))
                    })

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    data = payload.get("resource", [])
                
            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]
            
            # confirms if data is a list
            if isinstance(data, list):
                if len(data) > 0:
                    for i in range(len(data)):
                        if 'name' in data[i].keys():
                            data[i]['account_name'] = data[i].pop('name')
                        
            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    payload["resource"] = data
            else:
                payload = data

            super().set_response(payload)

            return self