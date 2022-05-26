import os, ast, json, requests

from datetime import datetime
from xero import Xero
from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import request_handler
from sdc_dp_helpers.xero import auth_handler as pixie
from sdc_dp_helpers.xero.config_managers import get_config
from sdc_dp_helpers.xero.writers import CustomS3JsonWriter


class CustomXeroReader:
    """
    Custom Xero Reader
    """

    def __init__(self, **kwargs):
        self.config_path = kwargs.get("config_path")
        self.creds_path = kwargs.get("creds_path")

        self.config = get_config(self.config_path)

        self.config.from_date = self.config.get(
            "from_date", datetime.now().strftime("%Y-%m-01")
        )
        self.config.to_date = self.config.get(
            "from_date", datetime.now().strftime("%Y-%m-%d")
        )

        self.client_id = self.creds.get("client_id", None)
        self.refresh_token_bucket = self.config.get("refresh_token_bucket")
        self.refresh_token_path = self.config.get("refresh_token_path")
        self.auth_token = pixie.get_auth_token(
            self.client_id,
            {
                "token_path": self.refresh_token_path,
                "bucket_name": self.refresh_token_bucket,
                "local_token_path": self.creds_path,
            },
            None,  # "default" #"ritdu-sdc-eu1"
        )
        self.auth_token.tenant_ids = self.confg.get("tenant_ids", [])

        self.writer = CustomS3JsonWriter()

    # def update_refresh_token(self):
    #     """
    #     Write the refresh token to s3 to be used in the next Auth run.
    #     """
    #     self.writer.write_to_s3(
    #         data=self.auth_token,
    #         filename=f"{self.client_id}_auth_token",
    #         suffix="json",
    #     )

    def traverse_reports(self):
        """
        Loops through reports in the config to pull each of them
        """
        for report_name in self.config.get("reports", []):
            if report_name not in [
                "BalanceSheet",
                "ProfitAndLoss",
                # "TrialBalance", #not pulling this atm
                "AgedPayablesByContact",
                "AgedReceivablesByContact",
            ]:
                raise ValueError(report_name + " is not supported or does not exist.")

            data_set = self.fetch_report(
                {
                    "from_date": self.config.get("from_date"),
                    "to_date": self.config.get("to_date"),
                    "report_name": self.config.get("report_name"),
                }
            )

            self.writer.write_to_s3(
                data_set,
                {
                    "data_variant": "reports",
                    "collection_name": report_name,
                    "tenant_name": data_set.get("Reports").get("ReportTitles")[1],
                    "date": datetime.strptime(
                        data_set.report.get("Reports")
                        .get("ReportTitles")[3]
                        .split(" to ")[0]
                        .strip(),
                        "%d %B %Y",
                    ).strftime("%Y_%m_%d"),
                },
            )
        return data_set

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0.1)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    def fetch_report(self, xero_client, request: dict):
        """
        This method accepts Parameters
            report_name: the report name as per Xero API endpoint
            from_date: the start_date of the report
            to_date: the end date of the report
        and returns the report for those parameters using the requests module to access the API directly
        """
        # unpack request
        report_name = request["report_name"]
        from_date = request["from_date"]
        to_date = request["to_date"]
        tracking_category = request["tracking_category"]
        filter_items = (
            None if "filter_items" not in request.keys() else request["filter_items"]
        )

        my_headers = {
            "Authorization": "Bearer " + self.xero_client.token["access_token"],
            "Xero-Tenant-Id": self.auth_token.tenant_id,
            "Accept": "application/json",
        }
        my_params = {
            "fromDate": from_date,
            "toDate": to_date,
            "trackingCategoryID": tracking_category["TrackingCategoryID"],
        }
        my_params.update(filter_items)
        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Reports/" + report_name,
            params=my_params,
            headers=my_headers,
        )
        # response.text = response.text.strip("'<>() ").replace('\'', '\"')
        # print(response.text)
        report = json.loads(
            response.text.replace("\r", "").replace("\n", "").strip("'<>() ")
        )
        report = {
            "tenantId": self.auth_token.tenant_id,
            "trackingCategoryId": tracking_category["TrackingCategoryID"],
            "report": report,
            "from_date": from_date,
            "to_date": to_date,
        }
        return json.dumps(report)

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0.1)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    def run_request(self, xero_client, api_object, request):
        """
        Run the API request that consumes a request payload and site url.
        This separates the request with the request handler from the rest of the logic.
        """
        # ToDo: Handle API Errors
        api_call = getattr(xero_client, api_object)
        return api_call.filter(
            from_date=request.get("from_date", None),
            to_date=request.get("to_date", None),
            page=request.get("page", None),
        )

    def fetch_modules(self):
        """
        Consumes a .yaml config file and loops through the date and url
        to return relevant data from Xero API.
        """
        self.xero_creds = pixie.refresh_auth_token()
        xero = Xero(self.xero_creds)

        from_date = self.config.get("from_date", None)
        to_date = self.config.get("to_date", None)
        data_set = []

        for api_object in self.config.get("modules", []):
            if api_object not in [
                "contacts",
                "accounts",
                "invoices",
                "banktransactions",
                "manualjournals",
                "purchaseorders",
            ]:
                raise ValueError(api_object + " is not supported or does not exist.")
            prev_response = None
            page = 1

            while True:
                response = self.run_request(
                    xero_client=xero,
                    api_object=api_object,
                    request={"from_date": from_date, "to_date": to_date, "page": page},
                )
                if len(response) < 1:
                    break
                elif response == prev_response:
                    break
                else:
                    data_set.append(json.dumps(ast.literal_eval(response)))

                # ensure the token is still fresh
                self.xero_creds = pixie.refresh_auth_token()

                prev_response = response
                page += 1

    def run_main(self):
        """
        As dictated by the config;
        This function fetches all modules and reports requested based on the config
        """
        if getattr(self.config, "modules", None):
            self.fetch_modules()

        if getattr(self.config, "reports", None):
            self.traverse_reports()
