import pickle
from _socket import timeout

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import OAuth2WebServerFlow

from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler
from sdc_dp_helpers.google_search_console.config_managers import get_config
from sdc_dp_helpers.google_search_console.utils import date_range


class CustomGSCReader:
    """
    Custom Google Search Console Reader
    """

    def __init__(self, config_path=None, **kwargs):
        if config_path is not None:
            self.config = get_config(config_path, fmt="yml")
            self.credentials = kwargs["credentials"]

        if config_path is None:
            self.credentials = get_config(kwargs["credentials"], fmt="json")

        self.scopes = kwargs.get(
            "scopes",
            (
                "https://www.googleapis.com/auth/webmasters.readonly",
                "https://www.googleapis.com/auth/webmasters",
            ),
        )
        self.discovery_uri = kwargs.get(
            "discovery_uri",
            ("https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest"),
        )
        self.oauth_scope = kwargs.get(
            "oath_scope", "https://www.googleapis.com/auth/webmasters.readonly"
        )
        self.redirect_uri = kwargs.get("redirect_uri", "urn:ietf:wg:oauth:2.0:oob")

        self.data_set = []

    def generate_authentication(
        self, auth_file_location="gsc_credentials.pickle"
    ) -> None:
        """
        A user friendly method to generate a .pickle file for future authentication.
        For the first time, you would need to log in with your web browser based on
        this web authentication flow. After that, it will save your credentials in
        a pickle file. Every subsequent time you run the script, it will use the
        “pickled” credentials stored in credentials.pickle to build the
        connection to Search Console.
        """
        flow = OAuth2WebServerFlow(
            self.credentials["installed"].get("client_id"),
            self.credentials["installed"].get("client_secret"),
            self.oauth_scope,
            self.redirect_uri,
        )
        authorize_url = flow.step1_get_authorize_url()
        print(f"Go to the following link in your browser: {authorize_url}")
        code = input("Enter verification code: ").strip()
        credentials = flow.step2_exchange(code)
        pickle.dump(credentials, open(auth_file_location, "wb"))

    def _get_service(self) -> build:
        """
        Makes use of the .pickle cred file to establish a webmaster connection.
        """
        with open(self.credentials, "rb") as _file:
            credentials = pickle.load(_file)

        return build(
            "searchconsole", "v1", credentials=credentials, cache_discovery=False
        )

    @request_handler(wait=1, backoff_factor=0.5)
    @retry_handler(
        exceptions=(timeout, HttpError),
        total_tries=5,
        initial_wait=60,
        backoff_factor=5,
    )
    def _query_handler(self, service, request, site_url):
        """
        Run the API request that consumes a request payload and site url.
        This separates the request with the request handler from the rest of the logic.
        """
        return service.searchanalytics().query(siteUrl=site_url, body=request).execute()

    def run_query(self):
        """
        Consumes a .yaml config file and loops through the date and url
        to return relevant data from GSC API.
        """
        service: build = self._get_service()
        start_date: str = self.config.get("start_date")
        end_date: str = self.config.get("end_date")
        dimensions: list = self.config.get("dimensions")

        print(
            f"Gathering data between given dates {start_date} and {end_date}. "
            f"Querying for Site Url: {self.config.get('site_url')}."
        )

        dimension_data_set = {}
        # split request by date to reduce 504 errors
        for dimension in dimensions:
            for date in date_range(start_date=start_date, end_date=end_date):
                print(f"Querying at date: {date} for dimension: {dimension}.")
                # run until none is returned or there is no more data in rows
                row_index = 0
                while True:
                    dim_query_set = list(dict.fromkeys(["date", dimension]))
                    response = self._query_handler(
                        service=service,
                        request={
                            "startDate": date,
                            "endDate": date,
                            "dimensions": dim_query_set,
                            "metrics": self.config.get("metrics"),
                            "type": self.config.get("type"),
                            "rowLimit": self.config.get("row_limit", 25000),
                            "startRow": row_index * self.config.get("row_limit", 25000),
                            "aggregationType": self.config.get(
                                "aggregation_type", "auto"
                            ),
                            "dimensionFilterGroups": self.config.get(
                                "dimension_filter_groups", []
                            ),
                            "dataState": self.config.get("data_state", "final"),
                        },
                        site_url=self.config.get("site_url"),
                    )

                    if response is None:
                        print("Response is None, exiting process...")
                        break
                    if "rows" not in response:
                        print("No more data in given row, moving on....")
                        break

                    # added additional data that the api does not provide
                    for row in response["rows"]:
                        dataset = {
                            "site_url": self.config.get("site_url"),
                            # keeping original search_type name for reporting
                            "search_type": self.config.get("type"),
                        }

                        # get dimension data keys and values
                        dataset.update(
                            dict(
                                zip(
                                    dim_query_set,
                                    row.get("keys", []),
                                )
                            )
                        )

                        # get metrics data
                        for metric in self.config.get("metrics", []):
                            dataset[metric] = row.get(metric)

                        if dimension not in dimension_data_set:
                            dimension_data_set[dimension] = []
                        dimension_data_set[dimension].append(dataset)
                    row_index += 1

            self.data_set.append(dimension_data_set)

        return self.data_set[0]
