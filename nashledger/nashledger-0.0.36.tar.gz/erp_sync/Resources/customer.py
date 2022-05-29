from erp_sync.Resources.resource import Resource


class Customer(Resource):

    urls = {}

    def set_client_type(self, client_type_id):
        super().set_client_type(client_type_id)
        return self

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
            "new": f"/companies/{super().get_company_id()}/customers",
            "edit": f"/companies/{super().get_company_id()}/customers",
            "read": f"/companies/{super().get_company_id()}/customers",
            "delete": f"/companies/{super().get_company_id()}/customers",
            "import": f"/companies/{super().get_company_id()}/import_customers"
        }

        super().set_urls(self.urls)

        return self

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def read(self, customer_id=None, payload=None, method='GET', endpoint=None):

        self._set_urls()

        if customer_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{customer_id}'
            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

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

    def import_vendors(self, ledger_id=None, payload=None, method='GET', endpoint=None):

        endpoint = f"/companies/{super().get_company_id()}/import_vendors"

        if ledger_id is not None:
            endpoint = f'{endpoint}/{ledger_id}'

        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "type": "<Enter either customer or vendor>",
            "title": "Mr",
                    "first_name": "<Enter first name>",
                    "last_name": "<Enter last name>",
                    "email": "<Enter email address>",
                    "phone": "<Enter phone number>",
                    "mobile": "<Enter mobile number>",
                    "designation": "<Enter designation e.g. Sales Executive>",
                    "department": "<Enter department e.g. Sales and Marketing>"
        }

        if super().get_client_type() == super().XERO:

            data["type"] = "<Enter either True (for vendor) or False (for customer)>"

        data.update({
            "additional_properties": {
                "help": "Optional data are passed inside this object, the format should be specific to the ERP. View ERP documentation for more details, below are examples of optional data",
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

                if 'type' in payload.keys():
                    data.update({
                        "type": payload.get("type", "customer")
                    })

                if 'title' in payload.keys():
                    data.update({
                        "Title": payload.get("title", "")
                    })

                if 'first_name' in payload.keys() and 'last_name' in payload.keys():
                    data.update({
                        "FullyQualifiedName": f'{payload.get("first_name","")} {payload.get("last_name","")}',
                        "DisplayName": f'{payload.get("first_name","")} {payload.get("last_name","")}',
                        "GivenName": payload.get("first_name", ""),
                        "MiddleName": payload.get("last_name", ""),
                        "FamilyName": payload.get("last_name", "")
                    })

                if 'email' in payload.keys():
                    data.update({
                        "PrimaryEmailAddr": {
                            "Address": payload.get("email", ""),
                        }
                    })

                if 'phone' in payload.keys():
                    data.update({
                        "PrimaryPhone": {
                            "FreeFormNumber": payload.get("phone", ""),
                        }
                    })

            # If client type is SAP
            elif super().get_client_type() == super().SAP:
                bp_information = {
                    "CardType": "CUSTOMER",
                }
                if 'first_name' in payload.keys() and 'last_name' in payload.keys():
                    bp_information.update({
                        "CardName": f'{payload.get("first_name","")} {payload.get("last_name","")}'
                    })

                if 'phone' in payload.keys():
                    bp_information.update({
                        "Telephone1": payload.get("phone", ""),
                        "Telephone2": payload.get("phone", "")
                    })

                if 'mobile' in payload.keys():
                    bp_information.update({
                        "MobilePhone": payload.get("mobile", "")
                    })

                if 'email' in payload.keys():
                    bp_information.update({
                        "Email": payload.get("email", "")
                    })

                if 'tax_pin' in payload.keys():
                    bp_information.update({
                        "KRAPIN": payload.get("tax_pin", "")
                    })

                if 'customer_code' in payload.keys():
                    bp_information.update({
                        "CardCode": payload.get("customer_code", "")
                    })

                if 'GroupCode' in additional_properties.keys():
                    bp_information.update({
                        "GroupCode": additional_properties.get("GroupCode", {})
                    })

                    additional_properties.pop("GroupCode")

                if 'Fax' in additional_properties.keys():
                    bp_information.update({
                        "Fax": additional_properties.get("Fax", {})
                    })

                    additional_properties.pop("Fax")

                if 'phone2' in additional_properties.keys():
                    bp_information.update({
                        "Telephone2": additional_properties.get("phone2", {})
                    })

                    additional_properties.pop("phone2")

                data.update({
                    "BPInformation": bp_information
                })
            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                contact_persons = {}

                if 'type' in payload.keys():
                    data.update({
                        "contact_type": payload.get("type", "customer")
                    })

                if 'title' in payload.keys():
                    data.update({
                        "salutation": payload.get("title", "")
                    })

                if 'first_name' in payload.keys() and 'last_name' in payload.keys():
                    data.update({
                        "contact_name": f'{payload.get("first_name","")} {payload.get("last_name","")}'
                    })

                    contact_persons.update({
                        "first_name": payload.get("first_name", ""),
                        "last_name": payload.get("last_name", "")
                    })

                if 'email' in payload.keys():
                    contact_persons.update({
                        "email": payload.get("email", "")
                    })

                if 'phone' in payload.keys():
                    contact_persons.update({
                        "phone": payload.get("phone", "")
                    })

                if 'mobile' in payload.keys():
                    contact_persons.update({
                        "mobile": payload.get("mobile", "")
                    })

                if 'designation' in payload.keys():
                    contact_persons.update({
                        "designation": payload.get("designation", "")
                    })

                if 'department' in payload.keys():
                    contact_persons.update({
                        "department": payload.get("department", "")
                    })

                if 'is_primary_contact' in payload.keys():
                    contact_persons.update({
                        "is_primary_contact": True
                    })

                if 'enable_portal' in payload.keys():
                    contact_persons.update({
                        "enable_portal": True
                    })

                data.update({
                    "contact_persons": [contact_persons]
                })

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                contacts = {}

                if 'type' in payload.keys():
                    contacts.update({
                        "IsSupplier": payload.get("type", False)
                    })

                if 'first_name' in payload.keys() and 'last_name' in payload.keys():
                    contacts.update({
                        "Name": f'{payload.get("first_name","")} {payload.get("last_name","")}',
                        "FirstName": payload.get("first_name", ""),
                        "LastName": payload.get("last_name", ""),
                        "ContactStatus": additional_properties.get("ContactStatus", "ACTIVE"),
                        "IsSupplier": additional_properties.get("IsSupplier", False)
                    })

                    if 'ContactStatus' in additional_properties.keys():
                        additional_properties.pop("ContactStatus")

                    if 'IsSupplier' in additional_properties.keys():
                        additional_properties.pop("IsSupplier")

                if 'email' in payload.keys():
                    contacts.update({
                        "EmailAddress": payload.get("email", "")
                    })

                if 'phone' in payload.keys():
                    contacts.update({
                        "Phones": [
                            {
                                "PhoneType": additional_properties.get("PhoneType", "MOBILE"),
                                "PhoneNumber": payload.get("phone", ""),
                                "PhoneAreaCode": additional_properties.get("PhoneAreaCode", "254")
                            }
                        ]
                    })

                    if 'PhoneType' in additional_properties.keys():
                        additional_properties.pop("PhoneType")

                    if 'PhoneAreaCode' in additional_properties.keys():
                        additional_properties.pop("PhoneAreaCode")

                if bool(contacts):
                    data["Contacts"] = [contacts]

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                data.update({
                    "name": f'{payload.get("first_name", "")} {payload.get("last_name", "")}',
                    "display_name": f'{payload.get("first_name", "")} {payload.get("last_name", "")}',
                    "email": f'{payload.get("email", "")}',
                    "active":True
                })
            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "name": f'{payload.get("first_name", "")} {payload.get("last_name", "")}',
                    "email": f'{payload.get("email", "")}',
                    "city": f'{payload.get("city", "")}',
                    "phoneNumber": f'{payload.get("phone", "")}',
                    "address": f'{payload.get("address", "")}',
                })

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            if 'customers' in payload.keys():
                data = payload.get("customers", [])
            elif 'resource' in payload.keys():
                data = payload.get("resource", [])

            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]

            # confirms if data is a list
            if isinstance(data, list):

                if len(data) > 0:

                    for i in range(len(data)):
                        if 'family_name' in data[i].keys():
                            data[i]['first_name'] = data[i].pop('family_name')

                        if 'given_name' in data[i].keys():
                            data[i]['last_name'] = data[i].pop('given_name')

            if 'customers' in payload.keys():
                payload["customers"] = data
            elif 'resource' in payload.keys():
                payload["resource"] = data

            super().set_response(payload)

            return self
