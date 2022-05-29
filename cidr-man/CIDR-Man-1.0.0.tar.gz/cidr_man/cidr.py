from copy import deepcopy
from enum import IntEnum
from functools import lru_cache
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, _BaseNetwork
from socket import inet_pton, AF_INET, AF_INET6, inet_ntop
from typing import Union, Tuple


class Version(IntEnum):
    v4 = 4
    v6 = 6


class CIDR:
    __prefix_len: int
    __max_prefix: int
    __ip: int
    __ip_str: str
    __packed: bytes
    __version: Version
    _is_global: bool
    _is_link_local: bool
    _is_loopback: bool
    _is_multicast: bool
    _is_private: bool
    _is_reserved: bool

    def __init__(
        self,
        net: Union[
            str, int, bytes, IPv4Network, IPv6Network, IPv4Address, IPv6Address, None
        ] = None,
        version: Version = None,
        prefix_len: int = -1,
    ):
        _version = Version.v4
        _prefix_len = -1
        discovered = False
        if net is not None:
            if isinstance(net, str):
                _version, self.__ip, _prefix_len = _convert_str(net)
                discovered = True
            elif isinstance(net, int):
                self.__ip = net
            elif isinstance(net, bytes):
                _version, self.__ip = _convert_bytes(net)
                _prefix_len = max_prefix(_version)
                discovered = True
            else:
                _version, self.__ip, _prefix_len = _convert_builtin(net)
                discovered = True
            if version is None:
                self.__version = _version
            else:
                self.__version = version
            if prefix_len == -1:
                self.__prefix_len = (
                    _prefix_len if discovered else max_prefix(self.__version)
                )
            else:
                self.__prefix_len = prefix_len
        else:
            self.__prefix_len = 0
            self.__version = Version.v4
            self.__ip = 0
        self.__max_prefix = max_prefix(self.__version)
        self.__packed = None
        self.__ip_str = None
        self._is_global = None
        self._is_link_local = None
        self._is_loopback = None
        self._is_multicast = None
        self._is_private = None
        self._is_reserved = None

    @property
    def ip(self):
        return self.__ip

    @property
    def num_addresses(self):
        return 2 ** (self.__max_prefix - self.__prefix_len)

    @property
    def prefix_len(self):
        return self.__prefix_len

    @property
    def prefixlen(self):
        return self.__prefix_len

    @property
    def max_prefixlen(self):
        return self.__max_prefix

    @property
    def version(self):
        return self.__version

    @property
    def network_address(self) -> "CIDR":
        if self.__prefix_len != self.__max_prefix:
            return self.__class__(self.__ip, self.__version)
        return self.copy()

    @property
    def broadcast_address(self) -> "CIDR":
        if self.__prefix_len != self.__max_prefix:
            prefix_len = self.__prefix_len
            mask = 1 << (self.__max_prefix - prefix_len)
            return self.__class__(self.__ip ^ (mask - 1), self.__version)

    @property
    def netmask(self) -> "CIDR":
        mask = ((1 << self.__prefix_len) - 1) << (self.__max_prefix - self.__prefix_len)
        return self.__class__(mask, self.__version)

    @property
    def first_address(self) -> "CIDR":
        if self.__prefix_len != self.__max_prefix:
            return self.__class__(self.__ip + 1, self.__version)
        return self.copy()

    @property
    def last_address(self) -> "CIDR":
        if self.__prefix_len != self.__max_prefix:
            return self.__class__(int(self.broadcast_address) - 1, self.__version)
        return self.copy()

    @property
    def compressed(self) -> str:
        if self.__prefix_len != self.__max_prefix:
            return f"{self._ip_str}/{self.__prefix_len}"
        return self._ip_str

    @property
    def packed(self):
        if self.__packed is None:
            length = _byte_length(self.version)
            self.__packed = self.__ip.to_bytes(length, "big", signed=False)
        return self.__packed

    def subnets(self) -> Tuple["CIDR", "CIDR"]:
        return self.left, self.right

    @property
    def left(self) -> "CIDR":
        prefix_len = self.__prefix_len + 1
        return self.__class__(self.__ip, self.__version, prefix_len)

    @property
    def right(self) -> "CIDR":
        prefix_len = self.__prefix_len + 1
        mask = 1 << (self.__max_prefix - prefix_len)
        return self.__class__(self.__ip ^ mask, self.__version, prefix_len)

    def subnet_of(
        self,
        other: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return other.contains(self)

    def contains(
        self,
        subnet: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ) -> bool:
        if not isinstance(subnet, self.__class__):
            subnet = self.__class__(subnet)
        if self.__version != subnet.version:
            raise ValueError("ip version mismatch")
        if self.__prefix_len > subnet.prefix_len:
            return False
        mask = self.__max_prefix - self.__prefix_len
        return (self.__ip >> mask) == (subnet.ip >> mask)

    @property
    def is_global(self):
        if self._is_global is not None:
            return self._is_global
        for net in RESERVED:
            if net.version == self.__version and net.contains(self):
                self._is_global = False
                return False
        for net in PRIVATE:
            if net.version == self.__version and net.contains(self):
                self._is_global = False
                return False
        for net in OTHER:
            if net.version == self.__version and net.contains(self):
                self._is_global = False
                return False
        self._is_global = True
        return True

    @property
    def is_private(self):
        if self._is_private is not None:
            return self._is_private
        for net in PRIVATE:
            if net.version == self.__version and net.contains(self):
                self._is_private = True
                return True
        self._is_private = False
        return False

    @property
    def is_reserved(self):
        if self._is_reserved is not None:
            return self._is_reserved
        for net in RESERVED:
            if net.version == self.__version and net.contains(self):
                self._is_reserved = True
                return True
        self._is_reserved = False
        return False

    @property
    def is_link_local(self):
        if self._is_link_local is not None:
            return self._is_link_local
        for net in LINK_LOCAL:
            if net.version == self.__version and net.contains(self):
                self._is_link_local = True
                return True
        self._is_link_local = False
        return False

    @property
    def is_loopback(self):
        if self._is_loopback is not None:
            return self._is_loopback
        for net in LOOPBACK:
            if net.version == self.__version and net.contains(self):
                self._is_loopback = True
                return True
        self._is_loopback = False
        return False

    @property
    def is_multicast(self):
        if self._is_multicast is not None:
            return self._is_multicast
        for net in MULTICAST:
            if net.version == self.__version and net.contains(self):
                self._is_multicast = True
                return True
        self._is_multicast = False
        return False

    @property
    def reverse_pointer(self):
        if self.__version == Version.v4:
            reverse_nibbles = [f"{n:i}" for n in self.packed[::-1]]
            if self.__prefix_len < self.__max_prefix:
                n = -1 * (self.prefix_len // 8)
                reverse_nibbles = reverse_nibbles[n:]
            return f"{'.'.join(reverse_nibbles)}.in-addr.arpa"
        reverse_nibbles = []
        for byte in self.packed[::-1]:
            high_bits = byte >> 4
            low_bits = byte - (high_bits << 4)
            reverse_nibbles.append(f"{low_bits:x}")
            reverse_nibbles.append(f"{high_bits:x}")
            if self.__prefix_len < self.__max_prefix:
                n = -1 * (self.prefix_len // 8)
                reverse_nibbles = reverse_nibbles[n:]
        return f"{'.'.join(reverse_nibbles)}.ip6.arpa"

    def copy(self) -> "CIDR":
        return deepcopy(self)

    def __contains__(
        self,
        subnet: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ) -> bool:
        return self.contains(subnet)

    def __int__(self):
        return self.__ip

    def __str__(self):
        return self.compressed

    def __repr__(self):
        return f"CIDR({self.compressed})"

    def __bytes__(self):
        return self.packed

    def __lt__(
        self,
        other: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ):
        if self.__version != other.version:
            raise ValueError("ip version mismatch")
        return self.contains(other) and not other.contains(self)

    def __eq__(
        self,
        subnet: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ):
        if not isinstance(subnet, self.__class__):
            subnet = self.__class__(subnet)
        return (
            self.__version == subnet.version
            and self.__prefix_len == subnet.prefix_len
            and self.__ip == subnet.ip
        )

    def __gt__(
        self,
        other: Union[
            "CIDR", str, int, IPv4Network, IPv6Network, IPv4Address, IPv6Address
        ],
    ):
        return other.contains(self) and not self.contains(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def _ip_str(self):
        if self.__ip_str is None:
            self.__ip_str = inet_ntop(_af(self.__version), self.packed)
        return self.__ip_str


@lru_cache(2)
def max_prefix(version: Version):
    return 32 if version == Version.v4 else 128


@lru_cache(2)
def _af(version: Version):
    return AF_INET if version == Version.v4 else AF_INET6


@lru_cache(2)
def _byte_length(version: Version):
    return 4 if version == Version.v4 else 16


@lru_cache(None)
def _convert_str(net: str) -> Tuple[Version, int, int]:
    parts = net.split("/")
    ip: bytes
    if len(parts) == 2:
        ip_s, prefix_s = parts
        prefix = int(prefix_s)
    else:
        ip_s = parts[0]
        prefix = None
    if "." in ip_s:
        version = Version.v4
        ip = inet_pton(AF_INET, ip_s)
        prefix = prefix if prefix is not None else 32
    else:
        version = Version.v6
        ip = inet_pton(AF_INET6, ip_s)
        prefix = prefix if prefix is not None else 128
    return version, int.from_bytes(ip, "big", signed=False), prefix


@lru_cache(None)
def _convert_builtin(
    net: Union[IPv4Network, IPv6Network, IPv4Address, IPv6Address]
) -> Tuple[Version, int, int]:
    version = Version(net.version)
    if isinstance(net, _BaseNetwork):
        ip = int(net.network_address)
        prefix = net.prefixlen
    else:
        ip = int(net)
        prefix = 32 if version == Version.v4 else 128
    return version, ip, prefix


@lru_cache(None)
def _convert_bytes(net: bytes) -> Tuple[Version, int]:
    if len(net) == 4:
        version = Version.v4
    else:
        version = Version.v6
    return version, int.from_bytes(net, "big", signed=False)


LINK_LOCAL = [CIDR("169.254.0.0/16"), CIDR("fe80::/10")]
LOOPBACK = [CIDR("127.0.0.0/8"), CIDR("::1/128")]
CARRIER = [CIDR("192.0.0.0/29"), CIDR("100.64.0.0/10"), CIDR("2002::/16")]
DOCUMENTATION = [
    CIDR("192.0.2.0/24"),
    CIDR("198.51.100.0/24"),
    CIDR("203.0.113.0/24"),
    CIDR("2001:db8::/32"),
    CIDR("233.252.0.0/24"),
]
PRIVATE = [
    CIDR("10.0.0.0/8"),
    CIDR("172.16.0.0/12"),
    CIDR("192.168.0.0/16"),
    CIDR("198.18.0.0/15"),
    CIDR("2001::/32"),
    CIDR("fc00::/7"),
    CIDR("64:ff9b:1::/48"),
    CIDR("2001:2::/48"),
    CIDR("100::/64"),
    *CARRIER,
    *LINK_LOCAL,
    *LOOPBACK,
    *DOCUMENTATION,
]
RESERVED = [CIDR("240.0.0.0/4"), CIDR("::ffff:0:0/96"), *LOOPBACK]
MULTICAST = [CIDR("224.0.0.0/4"), CIDR("233.252.0.0/24"), CIDR("ff00::/8")]
OTHER = [CIDR("192.0.0.0/24"), CIDR("2001::/23"), CIDR("2001:10::/28")]
