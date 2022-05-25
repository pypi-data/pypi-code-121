import urllib.parse

from lxml import etree
from lxml.etree import CDATA


class UspsAddress:
    def __init__(self, address1, address2, city, state, zip5):
        self.address1 = address1 or ''
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip5 = zip5

    def build_xml(self, api_user_id):

        xml = etree.Element("AddressValidateRequest", {"USERID": f"{api_user_id}"})

        # Revision=1 instructs to return all fields
        etree.SubElement(xml, "Revision").text = "1"

        # ID is provided for response if we wanted to verify multiple addresses at once
        addr = etree.SubElement(xml, "Address", {"ID": "0"})
        etree.SubElement(addr, "Address1").text = CDATA(
            urllib.parse.quote(self.address1.encode("utf-8"))
        )
        etree.SubElement(addr, "Address2").text = CDATA(
            urllib.parse.quote(self.address2.encode("utf-8"))
        )
        etree.SubElement(addr, "City").text = CDATA(
            urllib.parse.quote(self.city.encode("utf-8"))
        )
        etree.SubElement(addr, "State").text = CDATA(
            urllib.parse.quote(self.state.encode("utf-8"))
        )
        etree.SubElement(addr, "Zip5").text = self.zip5
        etree.SubElement(addr, "Zip4").text = ""

        return xml
