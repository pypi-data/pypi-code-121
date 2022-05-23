# ----------------------------------------------------------------------------
# Description    : Name/address resolution logic
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import re
import socket
import logging
import ipaddress
from collections import namedtuple
from typing import Optional, Union
from qblox_instruments.pnp import PlugAndPlay


# -- definitions -------------------------------------------------------------

# Port definitions for direct connections to an instrument.
MAIN_SCPI_PORT = 5025
MAIN_CFG_PORT = 5026
MAIN_ZMQ_RR_PORT = 20802
MAIN_ZMQ_PS_PORT = 20803

# Port definitions forwarded by the CMM to modules in the cluster, for direct
# module connections if needed.
MODULE_SCPI_PORT_OFFSET = 25000
MODULE_CFG_PORT_OFFSET = 26000
MODULE_ZMQ_RR_PORT_OFFSET = 23000
MODULE_ZMQ_PS_PORT_OFFSET = 24000

# Slot index of the CMM.
CMM_SLOT_INDEX = 0

# Structure returned by resolve(). See resolve() for more information.
AddressInfo = namedtuple(
    "AddressInfo",
    [
        "protocol",
        "address",
        "slot_index",
        "scpi_port",
        "cfg_port",
        "zmq_rr_port",
        "zmq_ps_port",
    ],
)

AddressInfo.__doc__ = """
Connection information structure. Can be constructed from an instrument
identifier via resolve().
"""

AddressInfo.protocol.__doc__ = """
:str: The protocol that must be used to connect. Can be:

 - ``"ip"`` for a normal IP-based connection; or
 - ``"pnp"`` when the device is not accessible due to IP address
   misconfiguration.
"""

AddressInfo.address.__doc__ = """
:str: IP address string for IP connections, or the device serial number for
plug & play.
"""

AddressInfo.slot_index.__doc__ = """
:Optional[int]: For clusters, this specifies which specific module to connect
to, if any. If None, the whole cluster will be treated as a single instrument.
For Pulsar devices, this should always be None.
"""

AddressInfo.scpi_port.__doc__ = """
:int: The port number for SCPI connections.
"""

AddressInfo.cfg_port.__doc__ = """
:int: The port number for configuration manager connections.
"""

AddressInfo.zmq_rr_port.__doc__ = """
:int: The port number for Qblox native ZeroMQ/CBOR REQ-REP connections.
"""

AddressInfo.zmq_ps_port.__doc__ = """
:int: The port number for Qblox native ZeroMQ/CBOR PUB-SUB connections.
"""


# -- functions ---------------------------------------------------------------

def _populate_ports(
    protocol: str,
    address: str,
    slot_index: Optional[int]
) -> AddressInfo:
    """
    Helper function for resolve(). Populates an :class:`~AddressInfo`
    structure with port information.

    Parameters
    ----------
    protocol: str
        Protocol, as determined by resolve().
    address: str
        IP address, as determined by resolve().
    slot_index: Optional[int]
        Slot index to retrieve port numbers for, or None to get the default
        port numbers.

    Returns
    -------
    AddressInfo
        The completed address information structure.
    """
    if slot_index is None or slot_index == CMM_SLOT_INDEX:
        return AddressInfo(
            protocol,
            address,
            slot_index,
            MAIN_SCPI_PORT,
            MAIN_CFG_PORT,
            MAIN_ZMQ_RR_PORT,
            MAIN_ZMQ_PS_PORT,
        )
    else:
        return AddressInfo(
            protocol,
            address,
            slot_index,
            MODULE_SCPI_PORT_OFFSET + slot_index,
            MODULE_CFG_PORT_OFFSET + slot_index,
            MODULE_ZMQ_RR_PORT_OFFSET + slot_index,
            MODULE_ZMQ_PS_PORT_OFFSET + slot_index,
        )


# ----------------------------------------------------------------------------
def resolve(identifier: Union[str, AddressInfo]) -> AddressInfo:
    """
    Converts a device identifier to an IP address or (if only reachable via
    plug and play) a serial number. For IP connections, also returns the ports
    that the device should be listening on.

    Parameters
    ----------
    identifier: Union[str, AddressInfo]
        If a string, this can be one of the following things:

         - ``"[ip://]<ip-address>[/#]"``,
         - ``"[pnp://]<device-name>[/#]"``,
         - ``"[pnp://]<serial-number>[/#]"``, or
         - ``"[ip://]<hostname>[/#]"``,

        where:

         - ``<ip-address>`` is a valid IPv4 or IPv6 address for the device to
           be resolved;
         - ``<device-name>`` is the customer-specified name of the instrument
           (programmed into it with qblox-cfg, qblox-pnp, or the
           ``set_name()`` method);
         - ``<serial-number>`` is the serial number of the instrument;
         - ``<hostname>`` is a hostname that will resolve to the IP address of
           the instrument via DNS (some routers support this if the device
           connects via DHCP; the hostname requested by the device will be its
           customer-specified name in lowercase, using dashes (``-``) for
           sequences of non-alphanumeric characters);
         - either ``ip://`` or ``pnp://`` may be prefixed to disambiguate
           between the various methods of device identification, if necessary;
           and
         - the optional ``/#`` suffix may be used for cluster devices to
           return information for a specific cluster module, where ``#`` is
           the slot index of the module.

        The four identification methods will be attempted in the sequence
        shown.

        If an :class:`~AddressInfo` object is passed as input, this function
        simply returns it as-is.

    Returns
    -------
    AddressInfo
        Address information structure.

    Raises
    ------
    ValueError
        If the identifier is invalid.
    RuntimeError
        If we failed to determine what this identifier is.
    """

    # Fallthrough if input is already a resolved address.
    if isinstance(identifier, AddressInfo):
        return identifier

    # Store the full identifier string for error messages.
    full_identifier = identifier

    # Properly log what we're doing.
    logger = logging.getLogger("resolver")
    logger.info('Resolving device identifier "%s"...', full_identifier)

    # Split off slot index suffix, if specified.
    if re.match(".*/[0-9]+$", identifier):
        identifier, slot_index = identifier.rsplit("/", maxsplit=1)
        slot_index = int(slot_index)
        logger.info(
            "Restricting connection to module in slot %d only.",
            slot_index
        )
    else:
        slot_index = None

    # Split off protocol hint.
    *hint, identifier = identifier.split("://", maxsplit=1)
    if hint:
        hint = hint[0]
        if hint not in ("pnp", "ip"):
            raise ValueError("protocol hint prefix must be pnp:// or ip://")
    else:
        hint = None

    # See if this is an IP address.
    if hint != "pnp":
        try:

            # Below line will throw a parse error if identifier is not a valid
            # IP address.
            ipaddress.ip_address(identifier)

            # No error, so this is an IP address.
            logger.info(
                '"%s" is a valid IP address; skipping name resolution.',
                identifier
            )
            return _populate_ports("ip", identifier, slot_index)

        except ValueError:
            pass

    # See if we can reach this device via plug & play.
    if hint != "ip":
        logger.info(
            'Trying to resolve "%s" as device name or serial number '
            "via plug & play...",
            identifier,
        )
        data = None
        try:
            with PlugAndPlay() as p:
                data = p.describe(identifier)
        except Exception:
            pass
        if data is not None:
            remote_ip = data.get("identity", {}).get("ip", None)
            local_ip_and_prefix = data.get("connected_via", None)
            if remote_ip is not None and local_ip_and_prefix is not None:
                local_net = ipaddress.IPv4Network(local_ip_and_prefix, strict=False)
                remote_net = ipaddress.IPv4Network("{}/32".format(remote_ip), strict=False)
                if local_net.overlaps(remote_net):

                    # Resolved via plug & play, but device should be
                    # accessible via regular TCP connections.
                    logger.info(
                        'Found "%s" at IP address %s via plug & play',
                        identifier,
                        remote_ip,
                    )
                    return _populate_ports("ip", remote_ip, slot_index)

                else:

                    # IP misconfiguration, only plug & play is available. Use
                    # serial number instead of whatever the device responded
                    # to if possible.
                    logger.warning(
                        'Found "%s" at IP address %s via %s, but that won\'t '
                        "work; only plug & play connectivity is available",
                        identifier,
                        remote_ip,
                        local_ip_and_prefix,
                    )
                    address = data.get("identity", {}).get("ser", identifier)
                    return _populate_ports("pnp", address, slot_index)

    # See if we can resolve the identifier via DNS.
    if hint != "pnp":
        logger.info('Trying to resolve "%s" via DNS lookup...', identifier)
        try:

            # Below line will throw a parse error if identifier is not a valid
            # IP address.
            data = socket.getaddrinfo(identifier, None)
            if data:
                remote_ip = data[0][4][0]
                logger.info(
                    'Found "%s" at IP address %s via DNS lookup',
                    identifier,
                    remote_ip
                )
                return _populate_ports("ip", remote_ip, slot_index)

        except OSError:
            pass

    raise RuntimeError(
        'Failed to resolve "{}" as something we can connect to'.format(full_identifier)
    )
