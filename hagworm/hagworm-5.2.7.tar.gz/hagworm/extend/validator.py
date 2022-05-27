# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import re


####################
# ASC可见字符验证

REGEX_ASC_VISIBLE = re.compile(r'^[\x21-\x7e]$')


def asc_visible(val):

    global REGEX_ASC_VISIBLE

    return True if REGEX_ASC_VISIBLE.match(val) else False


####################
# UUID验证

REGEX_UUID = re.compile(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')


def uuid(val):

    global REGEX_UUID

    return True if REGEX_UUID.match(val) else False


####################
# 邮箱验证

REGEX_EMAIL = re.compile(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')


def email(val):

    global REGEX_EMAIL

    return True if REGEX_EMAIL.match(val) else False


####################
# 域名验证

REGEX_DOMAIN = re.compile(
    r'^(?:[a-zA-Z0-9]'  # First character of the domain
    r'(?:[a-zA-Z0-9-_]{0,61}[A-Za-z0-9])?\.)'  # Sub domain + hostname
    r'+[A-Za-z0-9][A-Za-z0-9-_]{0,61}'  # First 61 characters of the gTLD
    r'[A-Za-z]$'  # Last character of the gTLD
)


def domain(val):

    global REGEX_DOMAIN

    return True if REGEX_DOMAIN.match(val) else False


####################
# URL验证

_IP_MIDDLE_OCTET = r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))'
_IP_LAST_OCTET = r'(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))'

REGEX_URL = re.compile(
    r"^"
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
    # user:pass authentication
    r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + _IP_MIDDLE_OCTET + r"{2}" + _IP_LAST_OCTET + r")|"
    r"(?:(?:169\.254|192\.168)" + _IP_MIDDLE_OCTET + _IP_LAST_OCTET + r")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + _IP_MIDDLE_OCTET + _IP_LAST_OCTET + r"))"
    r"|"
    # private & local hosts
    r"(?P<private_host>"
    r"(?:localhost))"
    r"|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + _IP_MIDDLE_OCTET + r"{2}"
    r"" + _IP_LAST_OCTET + r")"
    r"|"
    # IPv6 RegEx from https://stackoverflow.com/a/17871737
    r"\[("
    # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
    # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,7}:|"
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    r")\]|"
    # host name
    r"(?:(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)"
    # domain name
    r"(?:\.(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:(?:xn--[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]{2,})|"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff]{2,}))"
    r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:/[-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    r"(?:\?\S*)?"
    # fragment
    r"(?:#\S*)?"
    r"$",
    re.UNICODE | re.IGNORECASE
)


def url(val):

    global REGEX_URL

    return True if REGEX_URL.match(val) else False


####################
# mac地址验证

REGEX_MAC_ADDR = re.compile(r'^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')


def mac_addr(val):

    global REGEX_MAC_ADDR

    return True if REGEX_MAC_ADDR.match(val) else False


####################
# IP地址验证

def ipv4(val):

    groups = val.split(r'.')

    if len(groups) != 4 or any(not x.isdigit() for x in groups):
        return False

    return all(0 <= int(part) < 256 for part in groups)


def ipv4_cidr(val):

    try:
        prefix, suffix = val.split(r'/', 2)
    except ValueError:
        return False

    if not ipv4(prefix) or not suffix.isdigit():
        return False

    return 0 <= int(suffix) <= 32


def ipv6(val):

    ipv6_groups = val.split(r':')

    if len(ipv6_groups) == 1:
        return False

    ipv4_groups = ipv6_groups[-1].split(r'.')

    if len(ipv4_groups) > 1:

        if not ipv4(ipv6_groups[-1]):
            return False

        ipv6_groups = ipv6_groups[:-1]

    else:

        ipv4_groups = []

    max_groups = 6 if ipv4_groups else 8

    if len(ipv6_groups) > max_groups:
        return False

    count_blank = 0

    for part in ipv6_groups:

        if not part:
            count_blank += 1
            continue

        try:
            num = int(part, 16)
        except ValueError:
            return False
        else:
            if not 0 <= num <= 65536:
                return False

    if count_blank < 2:
        return True
    elif count_blank == 2 and not ipv6_groups[0] and not ipv6_groups[1]:
        return True

    return False


def ipv6_cidr(val):

    try:
        prefix, suffix = val.split(r'/', 2)
    except ValueError:
        return False

    if not ipv6(prefix) or not suffix.isdigit():
        return False

    return 0 <= int(suffix) <= 128
