"""Extract elements from XML."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import html
import ipaddress
import re

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node


def unescape(value: str | None) -> str:
    """Unescape XML entities."""
    if value is None:
        return ""
    assert value is not None

    return html.unescape(value)


def sanitize_xml(raw_xml: str) -> str:
    """Sanitize the xml."""
    regexes = (
        re.compile("(<authorizedkeys>).*?(</authorizedkeys>)"),
        re.compile("(<bcrypt-hash>).*?(</bcrypt-hash>)"),
        re.compile("(<clientcert_ca>).*?(</clientcert_ca>)"),
        re.compile("(<clientcert_crl>).*?(</clientcert_crl>)"),
        re.compile("(<ha_certificates>).*?(</ha_certificates>)"),
        re.compile("(<lighttpd_ls_password>).*?(</lighttpd_ls_password>)"),
        re.compile("(<password>).*?(</password>)"),
        re.compile("(<pre-shared-key>).*?(</pre-shared-key>)"),
        re.compile("(<prv>).*?(</prv>)"),
        re.compile("(<private-key>).*?(</private-key>)"),
        re.compile("(<radius_secret>).*?(</radius_secret>)"),
        re.compile("(<shared_key>).*?(</shared_key>)"),
        re.compile("(<ssloffloadcert>).*?(</ssloffloadcert>)"),
        re.compile("(<stats_password>).*?(</stats_password>)"),
        re.compile("(<tls>).*?(</tls>)"),
    )
    for regex in regexes:
        raw_xml = regex.sub(r"\1SANITIZED\2", raw_xml)
    return raw_xml


def is_digits_and_(data: str, and_val: str = ".") -> bool:
    """
    True if data is only digits and the and_val.
    """
    try:
        int(data)
    except ValueError:
        pass
    else:
        # Just digits
        return True

    # Get parts without the partition value.
    parts = [x for x in data.split(and_val) if x != and_val]

    try:
        [int(x) for x in parts]
    except ValueError:
        return False

    return True


def nice_address_sort(data: str, delimiter: str = " ") -> str:
    """
    Sort addresses that may consist of domains and IPv4/v6 addresses.

    Not all 'address' nodes are proper IPs and domains.
    some are ports.

    Deals with values such as 0.hostname.domain.

    TODO: Filter IPV4 and IPv6 separately.

    """
    try:
        addresses = [x.strip() for x in data.split(delimiter)]
        numeric = [x for x in addresses if len(x) > 1 and is_digits_and_(x)]
        numeric.sort(key=lambda x: ipaddress.ip_address(x.split("/")[0]))

        non_numeric = [x for x in addresses if len(x) > 1 and not is_digits_and_(x)]
        non_numeric.sort(key=str.casefold)

        result = []
        result.extend(non_numeric)
        result.extend(numeric)
        return "\n".join(result)
    except (TypeError, ValueError):
        # Not an actual address (ValueError) or mixture of IPV4 and IPV6 (TypeError).
        return data


def xml_findone(in_node: Node, el_path: str) -> Node | None:
    """
    Raise exception if more than one element is found.

    If no element is found, return None.
    """
    found = xml_findall(in_node, el_path)
    if not found:
        return None

    if len(found) > 1:
        raise NodeError(f"Found more than one result for: {el_path}.")

    return found[0]


def xml_node_exists(in_node: Node, el_path: str) -> bool:
    """
    True if node exists, else False.

    Netgate uses the existence of some XML entities to indicate value.
    """
    if in_node is None:
        return False

    node = xml_findone(in_node, el_path)
    if node is None:
        return False
    return True


def xml_findall(in_node: Node, el_path: str) -> list[Node]:
    """
    Find all instances of the XML path.

    Args:
        in_node:
            Parsed XML node.

        paths:
            Comma-delimited XML element hierarcy.
            If "pfsense" is first element, remove it.
            (etree parses "pfsense" into the "root")

        Returns:
            List of found Nodes.

    """
    path = el_path.split(",")
    if path[0] == "pfsense":
        if len(path) == 1:
            return []
        path = path[1:]
    selector = "/".join(path)

    try:
        nodes = in_node.findall(selector)
    except SyntaxError as err:
        raise NodeError(
            f"{in_node.getparent()}/{in_node.tag}. Selector: ({selector}). {err}."
        )

    return nodes
