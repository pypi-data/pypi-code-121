import re

from pigeonly_address.usps.client import UspsClient, UspsClientError


class StandardizeAddressError(Exception):
    pass


def standardize_country(country):
    if country.lower().strip().replace(".", "") in (
        "us",
        "usa",
        "united states",
        "united states of america",
    ):
        return "US"
    return country


def _isolate_po_box(line_one, line_two):
    """This helps USPS identity PO Box addresses when cluttered up.

    Example
    line_one: Smart Communication / PADOC
    line_two: SCI Houtzdale - PO Box 33028

    Return
    line_one: Smart Communication / PADOC SCI Houtzdale -
    line_two: PO Box 33028
    """
    pattern = re.compile(r"\bp(ost)?\.?\s?(o|0)\.?(ffice)?\s?box\s\w+", re.IGNORECASE)
    # Only do this if line_two. USPS should detect if everything is on line_one.
    # This is only to handle cases where the most pertinent info is on line_two
    if line_two:
        # Search for PO Box on line_two and isolate it if exists.
        match = re.search(pattern, line_two)
        if match:
            po_box = match.group(0)
            line_two_remainder = line_two.replace(po_box, "")
            line_one += f"; {line_two_remainder}"
            line_two = po_box
    return line_one, line_two


def _clean_line_one_two(line_one, line_two):
    line_one, line_two = _isolate_po_box(line_one, line_two)
    return line_one, line_two


class AddressService:
    def __init__(self, usps_api_key):
        self.usps_api_key = usps_api_key

    def standardize_address(
            self, name, line_one, city, governing_district, postal_code, country, line_two=None
    ):
        """

        :param name:
        :param line_one:
        :param city:
        :param governing_district:
        :param postal_code:
        :param country:
        :param line_two:
        :return:
        """
        country = standardize_country(country)
        if country != "US":
            raise StandardizeAddressError("Country must be 'US'")
        line_one, line_two = _clean_line_one_two(line_one, line_two)

        try:
            usps_results = UspsClient(self.usps_api_key).verify_address(
                address1=line_two,
                address2=line_one,
                city=city,
                state=governing_district,
                zip5=postal_code,
            )
        except UspsClientError as e:
            raise StandardizeAddressError(str(e))

        standardized_addr = {
            "name": name.strip().upper(),
            "line_one": usps_results["Address2"],
            "line_two": usps_results.get("Address1"),
            "city": usps_results.get("City"),
            "governing_district": usps_results.get("State"),
            "postal_code": usps_results.get("Zip5"),
            "country": "US",
            "meta": None,
        }
        if usps_results.get("ReturnText"):
            standardized_addr["meta"] = {}
            standardized_addr["meta"]["message"] = usps_results.get("ReturnText")

        return standardized_addr
