from erp_sync.Resources.resource import Resource


class Invoices(Resource):

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
            "new": f"/companies/{super().get_company_id()}/invoices",
            "edit": f"/companies/{super().get_company_id()}/invoices",
            "read": f"/companies/{super().get_company_id()}/invoices",
            "delete": f"/companies/{super().get_company_id()}/invoices",
            "import": f"/companies/{super().get_company_id()}/import_invoices",
        }

        super().set_urls(self.urls)

        return self

    def edit(self, ledger_id=None, payload=None, method="PUT", endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def read(self, invoice_id=None, payload=None, method="GET", endpoint=None):

        self._set_urls()

        if invoice_id is not None:
            self.urls["read"] = f'{self.urls["read"]}/{invoice_id}'
            super().set_urls(self.urls)

        return super().read(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method="DELETE", endpoint=None):

        self._set_urls()

        # payload = {"type": "SalesInvoice"}

        self.urls["delete"] = f'/{self.urls["delete"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().delete(payload, method, endpoint)

    def import_data(self, ledger_id=None, date_from = None, payload=None, method="GET", endpoint=None):

        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)        
        
        if date_from is not None and date_from != '':
            self.urls["import"] = f'{self.urls["import"]}?dateFromFilter={date_from}'
            super().set_urls(self.urls)

        return super().import_data(payload, method, endpoint)

    def apply_credits(self, ledger_id=None, payload=None, method="POST", endpoint=None):

        endpoint = f'{self.urls["read"]}/{ledger_id}/apply_credits'

        return super().read(payload, method, endpoint)

    def invoice_payments(
        self, invoice_id=None, payload=None, method="GET", endpoint=None
    ):

        endpoint = f'{self.urls["read"]}/{invoice_id}/payments'

        return super().read(payload, method, endpoint)

    def credits_applied(
        self, invoice_id=None, payload=None, method="GET", endpoint=None
    ):

        endpoint = f'{self.urls["read"]}/{invoice_id}/credits_applied'

        return super().read(payload, method, endpoint)

    def invoice_types(self, endpoint="/invoice_types"):

        return super().read(endpoint=endpoint)

    def import_bills(self, invoice_id=None, payload=None, method="GET", endpoint=None):
        endpoint = f"/companies/{super().get_company_id()}/import_bills"

        if invoice_id is not None:
            endpoint = f"{endpoint}/{invoice_id}"

        return super().read(payload, method, endpoint)

    def payload(self):

        data = {
            "customer_ledger_id ": "<Enter customer id>",
            "item_ledger_id": "<Enter item id>",
            "amount": "<Enter amount>",
            "reference": "<reference>",
            "due_date": "<Enter invoice due date>",
        }

        # If client type is XERO
        if super().get_client_type() == super().XERO:
            data["chart_of_account_id"] = "<Enter chart of account id>"

        # If client type is ZOHO
        elif (
            super().get_client_type() == super().ZOHO
            or super().get_client_type() == super().QBO
        ):
            data.pop("reference")
            data.pop("due_date")

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return (
                "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
            )

        if operation == super().NEW or operation == super().UPDATE:

            data["type"] = "SalesInvoice"

            if "invoice_type" in payload.keys():
                data["type"] = payload.get("invoice_type", "SalesInvoice")

            additional_properties = payload.get("additional_properties", {})

            # If client type is ZOHO
            if super().get_client_type() == super().ZOHO:

                if "customer_ledger_id" in payload.keys():
                    data.update({"customer_id": payload.get("customer_ledger_id", "")})

                if "reference" in payload.keys():
                    data.update({"reference_number": payload.get("reference", "")})

                if "due_date" in payload.keys():
                    data.update({"due_date": payload.get("due_date", "")})

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["item_id"] = line_items[i].pop("item_ledger_id")

                    if "price" in line_items[i].keys():
                        line_items[i]["rate"] = line_items[i].pop("price")

                    if "quantity" in line_items[i].keys():
                        line_items[i]["quantity"] = line_items[i].pop("quantity")

                # if line_items has data in it
                if bool(line_items):
                    data.update({"line_items": line_items})

            # If client type is Quickbooks Online
            elif super().get_client_type() == super().QBO:

                if "customer_ledger_id" in payload.keys():
                    data.update(
                        {
                            "CustomerRef": {
                                "value": payload.get("customer_ledger_id", "")
                            }
                        }
                    )

                if "currency_code" in payload.keys():
                    data.update({
                        "CurrencyRef": {
                            "value": payload.get("currency_code", "KES")
                        }
                    })

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    line_items[i]["DetailType"] = "SalesItemLineDetail"
                    line_items[i]["Description"] = line_items[i].pop("description")
                    line_items[i]["SalesItemLineDetail"] = {}
                    line_items[i]["Amount"] = line_items[i].get(
                        "price", 0
                    ) * line_items[i].get("quantity", 0)

                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["SalesItemLineDetail"]["ItemRef"] = {"value": line_items[i].pop("item_ledger_id", 0)}

                    if "price" in line_items[i].keys():
                        line_items[i]["SalesItemLineDetail"]["UnitPrice"] = line_items[i].pop("price")

                    if "quantity" in line_items[i].keys():
                        line_items[i]["SalesItemLineDetail"]["Qty"] = line_items[i].pop("quantity")

                # if line_items has data in it
                if bool(line_items):
                    data.update({"Line": line_items})

            # If client type is SAP
            elif super().get_client_type() == super().SAP:
                header = {}

                if "customer_ledger_id" in payload.keys():
                    header.update({"CardCode": payload.get("customer_ledger_id", "")})

                if "invoice_type" in payload.keys():
                    header.update(
                        {
                            "ObjectType": data.get("type", ""),
                            "InvoiceType": data.get("type", ""),
                        }
                    )

                if "due_date" in payload.keys():
                    header.update({"DocDueDate": payload.get("due_date", "")})

                if "reference" in payload.keys():
                    header.update({"Reference": payload.get("reference", "")})

                if "DocDate" in additional_properties.keys():
                    header.update({"DocDate": additional_properties.get("DocDate", "")})

                    additional_properties.pop("DocDate")

                if "PostingDate" in additional_properties.keys():
                    header.update(
                        {"PostingDate": additional_properties.get("PostingDate", "")}
                    )

                    additional_properties.pop("PostingDate")

                if "RequiredDate" in additional_properties.keys():
                    header.update(
                        {"RequiredDate": additional_properties.get("RequiredDate", "")}
                    )

                    additional_properties.pop("RequiredDate")

                if "ValidUntil" in additional_properties.keys():
                    header.update(
                        {"ValidUntil": additional_properties.get("ValidUntil", "")}
                    )

                    additional_properties.pop("ValidUntil")

                if "DocCurrency" in additional_properties.keys():
                    header.update(
                        {"DocCurrency": additional_properties.get("DocCurrency", "")}
                    )

                    additional_properties.pop("DocCurrency")

                if "SourceNumber" in additional_properties.keys():
                    header.update(
                        {"SourceNumber": additional_properties.get("SourceNumber", "")}
                    )

                    additional_properties.pop("SourceNumber")

                if "Rounding" in additional_properties.keys():
                    header.update(
                        {"Rounding": additional_properties.get("Rounding", "")}
                    )

                    additional_properties.pop("Rounding")

                if "Remarks" in additional_properties.keys():
                    header.update({"Remarks": additional_properties.get("Remarks", "")})

                    additional_properties.pop("Remarks")

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "account_id" in line_items[i].keys():
                        line_items[i]["AcctCode"] = line_items[i].pop("account_id")
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["ItemCode"] = line_items[i].pop("item_ledger_id")
                    if "quantity" in line_items[i].keys():
                        line_items[i]["Quantity"] = line_items[i].pop("quantity")
                    if "price" in line_items[i].keys():
                        line_items[i]["UnitPrice"] = line_items[i].pop("price")
                    if "description" in line_items[i].keys():
                        line_items[i]["Description"] = line_items[i].pop("description")
                    if "tax_type" in line_items[i].keys():
                        line_items[i]["VatGroup"] = line_items[i].pop("tax_type")

                # if line_items has data in it
                if bool(line_items):
                    header.update({"Rows": line_items})

                # if header has data in it
                if bool(header):
                    data.update({"Header": header})

            # If client type is XERO
            elif super().get_client_type() == super().XERO:

                invoices = {
                    "Status": f'{additional_properties.get("Status", "AUTHORISED")}'
                }

                if "invoice_type" in payload.keys():
                    if data["type"] == "SalesInvoice":
                        invoices.update({"Type": "ACCREC"})
                    elif data["type"] == "PurchaseInvoice":
                        invoices.update({"Type": "ACCPAY"})

                if "currency_code" in payload.keys():
                    invoices.update(
                        {"CurrencyCode": payload.get("currency_code", "KES")}
                    )

                if "customer_ledger_id" in payload.keys():
                    invoices.update(
                        {
                            "Contact": {
                                "ContactID": payload.get("customer_ledger_id", "")
                            }
                        }
                    )

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "tax_type" in line_items[i].keys():
                        line_items[i]["TaxType"] = line_items[i].pop("tax_type")
                    elif "tax_type" not in line_items[i].keys():
                        line_items[i]["TaxType"] = "NONE"

                    if "price" in line_items[i].keys():
                        line_items[i]["LineAmount"] = line_items[i].pop("price")

                    if "description" in line_items[i].keys():
                        line_items[i]["Description"] = line_items[i].pop("description")

                    if "account_id" in line_items[i].keys():
                        line_items[i]["AccountID"] = line_items[i].pop("account_id")

                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["LineItemID"] = line_items[i].pop(
                            "item_ledger_id"
                        )

                    if "quantity" in line_items[i].keys():
                        line_items[i]["Quantity"] = line_items[i].pop("quantity")

                if "due_date" in payload.keys():
                    invoices.update({"DueDate": payload.get("due_date", "")})

                if "reference" in payload.keys():
                    invoices.update({"Reference": payload.get("reference", "")})

                if "Status" in additional_properties.keys():
                    additional_properties.pop("Status")

                # if line_items has data in it
                if bool(line_items):
                    invoices.update({"LineItems": line_items})

                # if invoices has data in it
                if bool(invoices):
                    data.update({"Invoices": [invoices]})

            # If client type is ODOO
            elif super().get_client_type() == super().ODOO:
                data.update(
                    {
                        "partner_id": payload.get("customer_ledger_id", ""),
                        "name": payload.get("invoice_number", ""),
                        "payment_reference": payload.get("reference", ""),
                        "state": additional_properties.get("state", "draft"),
                        "currency_id": payload.get("currency_id", 0),
                        "invoice_date_due": payload.get("due_date", ""),
                    }
                )

                if data["type"] == "SalesInvoice":
                    data.update({"move_type": "out_invoice"})
                    data.pop("type")
                elif data["type"] == "PurchaseInvoice":
                    data.update({"move_type": "in_invoice"})
                    data.pop("type")

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["product_id"] = line_items[i].pop(
                            "item_ledger_id"
                        )
                    if "quantity" in line_items[i].keys():
                        line_items[i]["quantity"] = line_items[i].pop("quantity")
                    if "price" in line_items[i].keys():
                        line_items[i]["price_unit"] = line_items[i].pop("price")
                    if "tax_id" in line_items[i].keys():
                        line_items[i]["tax_ids"] = [line_items[i].pop("tax_id")]

                    if "description" in payload.keys():
                        line_items[i].pop("description")
                    if "account_id" in payload.keys():
                        line_items[i].pop("account_id")
                    if "tax_type" in payload.keys():
                        line_items[i].pop("tax_type")

                # if line_items has data in it
                if bool(line_items):
                    data.update({"invoice_line_ids": line_items})

            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.update({
                    "customerNumber": f'{payload.get("customer_ledger_id", "")}'
                })

                line_items = payload.get("line_items", [])

                for i in range(len(line_items)):
                    if "item_ledger_id" in line_items[i].keys():
                        line_items[i]["item_id"] = line_items[i].pop(
                            "item_ledger_id"
                        )
                    if "quantity" in line_items[i].keys():
                        line_items[i]["quantity"] = line_items[i].pop("quantity")
                    if "price" in line_items[i].keys():
                        line_items[i]["unit_price"] = line_items[i].pop("price")
                    if "type" in line_items[i].keys():
                        line_items[i]["type"] = line_items[i].pop("type")
                    if "unit_of_measure" in line_items[i].keys():
                        line_items[i]["unit_of_measure"] = line_items[i].pop("unit_of_measure")

                    if "account_id" in payload.keys():
                        line_items[i].pop("account_id")
                    if "description" in payload.keys():
                        line_items[i].pop("description")
                    if "tax_type" in payload.keys():
                        line_items[i].pop("tax_type")
                    if "tax_id" in payload.keys():
                        line_items[i].pop("tax_id")

                # if line_items has data in it
                if bool(line_items):
                    data.update({"create_customer_invoice_details": line_items})
                    
            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if "resource" in payload.keys():
                    data = payload.get("resource", [])
                elif "invoices" in payload.keys():
                    data = payload.get("invoices", [])

            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]

            # confirms if data is a list
            if isinstance(data, list):

                if len(data) > 0:
                    for i in range(len(data)):
                        if "total_amount" in data[i].keys():
                            data[i]["amount"] = data[i].pop("total_amount")

            if isinstance(payload, dict):
                if "invoices" in payload.keys():
                    payload["invoices"] = data
                elif "resource" in payload.keys():
                    payload["resource"] = data

            super().set_response(payload)

            return self
