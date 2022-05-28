import abc
import argparse
import importlib
import inspect
import ipaddress
import logging
import os
import pkgutil
import re
import sys
from typing import Type

import requests

import mcddns.exceptions as exceptions


PROVIDER_MODULE_BUILTIN_PATH = os.path.dirname(__file__)
PROVIDER_MODULE_PREFIX = f"mcddns_"

log = logging.getLogger(__name__)


class Provider(abc.ABC):

    log = logging.getLogger(__name__)

    def options_pre(self, parser: argparse.ArgumentParser):
        pass

    def options_post(
        self, parser: argparse.ArgumentParser, options: argparse.Namespace
    ):
        pass


class AddressProvider(Provider):
    @abc.abstractmethod
    def fetch(self, options: argparse.Namespace) -> str:
        pass

    def validate(self, options: argparse.Namespace, address: str) -> bool:
        return self.is_ipv4_address(address)

    @staticmethod
    def fetch_url(url: str, timeout: int = 3) -> str:
        try:
            return requests.get(url, timeout=timeout).text.strip()
        except requests.exceptions.RequestException as e:
            log.error(e)
            return ""

    @staticmethod
    def is_ip_address(value: str) -> bool:
        value = str(value)
        try:
            ipaddress.ip_address(value)
            log.debug("Valid IP address: %s", value)
            return True
        except ValueError:
            log.error("Invalid IP address: %s", value)
            return False

    @staticmethod
    def is_ipv4_address(value: str) -> bool:
        value = str(value)
        try:
            if ipaddress.ip_address(value).version == 4:
                result = True
            else:
                result = False
        except ValueError:
            result = False

        if result:
            log.debug("Valid IPv4 address: %s", value)
        else:
            log.error("Invalid IPv4 address: %s", value)
        return result

    @staticmethod
    def is_ipv6_address(value: str) -> bool:
        value = str(value)
        try:
            if ipaddress.ip_address(value).version == 6:
                result = True
            else:
                result = False
        except ValueError:
            result = False

        if result:
            log.debug("Valid IPv6 address: %s", value)
        else:
            log.error("Invalid IPv6 address: %s", value)
        return result

    @staticmethod
    def is_hostname(value: str) -> bool:
        if len(value) > 255:
            result = False
        else:
            if value[-1] == ".":
                value = value[:-1]
            allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
            result = all(allowed.match(x) for x in value.split("."))

        if result:
            log.debug("Valid hostname: %s", value)
        else:
            log.error("Invalid hostname: %s", value)
        return result


class DNSProvider(Provider):
    @abc.abstractmethod
    def check(self, options: argparse.Namespace, address: str):
        pass

    @abc.abstractmethod
    def update(self, options: argparse.Namespace, address: str):
        pass


def import_modules(*paths: str) -> dict:
    sys.path = list(paths) + sys.path
    modules = [
        m.name
        for m in pkgutil.iter_modules()
        if m.name.startswith(PROVIDER_MODULE_PREFIX)
    ]
    return {m: importlib.import_module(m) for m in modules}


def strip_prefix(value: str, prefix: str) -> str:
    return value[len(prefix) :] if prefix and value.startswith(prefix) else value


def provider_full_name(obj: Provider) -> str:
    module = inspect.getmodule(obj)
    return (
        f"{strip_prefix(module.__name__, PROVIDER_MODULE_PREFIX)}.{obj.__name__}"
        if module
        else ""
    )


def list_providers(*types: Type) -> dict:
    valid_types = tuple(Provider.__subclasses__())

    if not [t for t in types if t]:
        types = valid_types
    else:
        invalid_types = [str(t) for t in types if t not in valid_types]
        if invalid_types:
            raise exceptions.NoSuchProviderType(
                f"Invalid provider types: {', '.join(invalid_types)}"
            )

    return {
        provider_full_name(cls): cls
        for cls in sum([t.__subclasses__() for t in types], [])
    }


def get_provider(name: str) -> Provider:
    try:
        return list_providers()[name]
    except KeyError:
        raise exceptions.NoSuchProvider(f"No such provider: {name}")
