
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from promium.base import Element
from promium.helpers import ParseUrl


class Link(Element):

    @property
    def href(self):
        return self.get_attribute("href")

    @property
    def parse_url(self):
        """
        Using parse_url to parse href. Can get attributes:
        - scheme
        - host
        - sub_domain
        - port
        - path
        - params
        - query
        - fragment
        - product_id
        """
        return ParseUrl(self.href)

    @property
    def response(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=[502, 503, 504],
            method_whitelist=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session.get(self.href, verify=False, timeout=10)

    @property
    def get_status_code(self):
        """Gets status requests code from link"""
        return self.response.status_code
