import json

import requests
import xmltodict
from lxml import etree

from pigeonly_address.usps.address import UspsAddress


class UspsClientError(Exception):
    pass


class UspsClient:
    BASE_URL = "https://secure.shippingapis.com/ShippingAPI.dll?API=Verify"

    def __init__(self, api_user_id):
        self.api_user_id = api_user_id

    def _get_url(self, xml):
        xml_str = etree.tostring(xml, encoding="iso-8859-1").decode()
        # xml_str = etree.tostring(xml, encoding="iso-8859-1", pretty_print=True).decode()
        return f"{self.BASE_URL}&XML={xml_str}"

    def verify_address(self, address2, city, state, zip5, address1=None):
        """
        Verify an address with USPS

        https://www.usps.com/business/web-tools-apis/address-information-api.htm#_Toc39492056

        :param address:
        :return:
        """
        address = UspsAddress(
            address1=address1, address2=address2, city=city, state=state, zip5=zip5
        )
        xml = address.build_xml(self.api_user_id)
        url = self._get_url(xml)
        results = self._make_request(url)
        if results.get("Error"):
            print(
                "It's likely this error is because of a bad request, not a bad address."
            )
            raise UspsClientError(results["Error"]["Description"])
        address_results = results["AddressValidateResponse"]["Address"]
        if address_results.get("Error"):
            raise UspsClientError(f"{address_results['Error']['Description']}.")
        return address_results

    def _make_request(self, url):
        xml_response = requests.get(url)
        results = json.loads(json.dumps(xmltodict.parse(xml_response.content)))
        return results
