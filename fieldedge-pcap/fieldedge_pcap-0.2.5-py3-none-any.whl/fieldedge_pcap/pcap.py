"""A utility to parse and generate relevant metrics for analysis of a PCAP file.

Uses the `pyshark` package for capture and analysis.

* Goal is WAN data reduction, focus is on packet size and application type.
* Ignore/filter out local traffic e.g. ARP
* Identify repeating patterns based on size and application protocol
to derive an interval...can it be done less frequently or by proxy?
e.g. DNS cache, local NTP
* If payload can be read (unencrypted) does it change often...could threshold
report by exception be used with a less frequent update pushed?

"""
import asyncio
import io
import json
import logging
import os
import statistics
import sys
import traceback
from datetime import datetime
from enum import Enum
from multiprocessing import Queue
from pathlib import Path

import pyshark
from pyshark.capture.capture import TSharkCrashException
from pyshark.packet.packet import Packet as SharkPacket

_log = logging.getLogger(__name__)

LOCALNET_172 = str(os.getenv('LOCALNET_172', True)) == 'True'
LOCALNET_192 = str(os.getenv('LOCALNET_192', True)) == 'True'
DEBUG_PACKET_NUMBER = int(os.getenv('DEBUG_PACKET_NUMBER', 0))
DEBUG_VERBOSE = str(os.getenv('DEBUG_VERBOSE', False)).lower() == 'true'


class EthernetProtocol(Enum):
    """Mappings for Ethernet packet types."""
    ETH_TYPE_EDP = 0x00bb  # Extreme Networks Discovery Protocol
    ETH_TYPE_PUP = 0x0200  # PUP protocol
    ETH_TYPE_IP = 0x0800  # IP protocol
    ETH_TYPE_ARP = 0x0806  # address resolution protocol
    ETH_TYPE_AOE = 0x88a2  # AoE protocol
    ETH_TYPE_CDP = 0x2000  # Cisco Discovery Protocol
    ETH_TYPE_DTP = 0x2004  # Cisco Dynamic Trunking Protocol
    ETH_TYPE_REVARP = 0x8035  # reverse addr resolution protocol
    ETH_TYPE_8021Q = 0x8100  # IEEE 802.1Q VLAN tagging
    ETH_TYPE_8021AD = 0x88a8  # IEEE 802.1ad
    ETH_TYPE_QINQ1 = 0x9100  # Legacy QinQ
    ETH_TYPE_QINQ2 = 0x9200  # Legacy QinQ
    ETH_TYPE_IPX = 0x8137  # Internetwork Packet Exchange
    ETH_TYPE_IP6 = 0x86DD  # IPv6 protocol
    ETH_TYPE_PPP = 0x880B  # PPP
    ETH_TYPE_MPLS = 0x8847  # MPLS
    ETH_TYPE_MPLS_MCAST = 0x8848  # MPLS Multicast
    ETH_TYPE_PPPOE_DISC = 0x8863  # PPP Over Ethernet Discovery Stage
    ETH_TYPE_PPPOE = 0x8864  # PPP Over Ethernet Session Stage
    ETH_TYPE_LLDP = 0x88CC  # Link Layer Discovery Protocol
    ETH_TYPE_TEB = 0x6558  # Transparent Ethernet Bridging


class KnownTcpPorts(Enum):
    """Mappings for common registered/known application layer TCP ports."""
    SMTP = 25
    HTTP = 80
    HTTP_TLS = 443
    DNS = 53
    FTP = 20
    FTPC = 21
    TELNET = 23
    IMAP = 143
    RDP = 3389
    SSH = 22
    HTTP2 = 8080
    MODBUS = 502
    MODBUS_TLS = 802
    MQTT = 1883
    MQTT_TLS = 8883
    MQTT_SOCKET = 9001
    DOCKERAPI = 2375
    DOCKERAPI_TLS = 2376
    SRCP = 4303
    COAP = 5683
    COAP_TLS = 5684
    DNP2 = 19999
    DNP = 20000
    IEC60870 = 2404


class KnownUdpPorts(Enum):
    """Mappings for common registered/known application layer TCP ports."""
    SNMP = 161
    DNS = 53
    DHCP_QUERY = 67
    DHCP_RESPONSE = 68
    NTP = 123


def _get_src_dst(packet: SharkPacket) -> 'tuple[str,str]':
    """Returns the packet source and destination hosts as a tuple.
    
    Args:
        packet: A pyshark Packet
    
    Returns:
        A tuple with (source, destination) IP addresses
    """
    if hasattr(packet, 'arp'):
        return (str(packet.arp.src_proto_ipv4), str(packet.arp.dst_proto_ipv4))
    elif hasattr(packet, 'ip'):
        return (str(packet.ip.src), str(packet.ip.dst))
    elif hasattr(packet, 'ipv6'):
        # return (str(packet.ipv6.src), str(packet.ipv6.dst))
        raise NotImplementedError(f'IPV6 unsupported')
    else:
        raise NotImplementedError(f'Unable to determine src/dst'
                                  f' for {packet.highest_layer}')


def _get_ports(packet: SharkPacket) -> tuple:
    """Returns the transport source and destination ports as a tuple.
    
    Args:
        packet: A pyshark Packet

    Returns:
        A tuple with (source, destination) ports (TCP or UDP)
    """
    if packet.transport_layer:
        srcport = int(packet[packet.transport_layer].srcport)
        dstport = int(packet[packet.transport_layer].dstport)
    elif hasattr(packet, 'icmp') and packet['icmp'].udp_port:
        srcport = int(packet['icmp'].udp_srcport)
        dstport = int(packet['icmp'].udp_dstport)
    else:
        raise ValueError('Unable to determine transport'
                            f' for {packet.highest_layer} packet')
    return (srcport, dstport)


def _get_application(packet: SharkPacket) -> str:
    """Returns the application layer descriptor.
    
    If the port is a registered port it will return a caps string.

    Args:
        packet: A pyshark Packet

    Returns:
        A string with the application layer protocol e.g. `TCP_MQTTS`
    """
    highest_layer: str = packet.highest_layer
    transport_layer: str = ''
    if packet.transport_layer:
        transport_layer = packet.transport_layer
    else:
        try:
            transport_layer = str(packet.layers[2].layer_name).upper()
        except Exception as err:
            _log.error(err)
    application = ''
    if hasattr(packet[highest_layer], 'app_data_proto'):
        application = str(packet[highest_layer].app_data_proto).upper()
    if transport_layer:
        if not application:
            (srcport, dstport) = _get_ports(packet)
            ports_lookup = None
            if transport_layer == 'TCP':
                ports_lookup = KnownTcpPorts
            elif transport_layer == 'UDP':
                ports_lookup = KnownUdpPorts
            if ports_lookup:
                known_ports = tuple(item.value for item in ports_lookup)
                if srcport in known_ports:
                    application = ports_lookup(srcport).name
                elif dstport in known_ports:
                    application = ports_lookup(dstport).name
            else:
                if transport_layer != highest_layer:
                    application = highest_layer.upper()
                else:
                    application += f'{dstport}'
        application = f'{transport_layer}_{application}'
    # identified workarounds for observed pyshark/tshark app_data_proto
    if not application:
        application = f'{str(packet.highest_layer).upper()}_UNKNOWN'
    application = application.replace('HTTP-OVER-TLS', 'HTTP_TLS')
    if highest_layer == 'TLS' and not application.endswith('_TLS'):
        application += '_TLS'
    if not (application.startswith('TCP_') or application.startswith('UDP_')):
        _log.warning(f'Transport layer unknown for packet {packet.number}')
    return application


def is_valid_ip(ip_addr: str) -> bool:
    """Returns true if the string represents a valid IPv4 address.
    
    Args:
        ip_addr: The IP address being qualified
    
    Returns:
        True if it has 4 parts separated by `.` with each part in range 0..255
    """
    if not(isinstance(ip_addr, str)):
        return False
    if (len(ip_addr.split('.')) == 4 and
        (int(x) in range (0,256) for x in ip_addr.split('.'))):
        return True
    return False


def is_private_ip(ip_addr: str) -> bool:
    """Returns true if the IPv4 address is in the private range.
    
    Args:
        ip_addr: The IP address being qualified
    
    Returns:
        True if the address is in the private range(s)
    
    Raises:
        ValueError if the address is invalid
    """
    if not is_valid_ip(ip_addr):
        raise ValueError(f'IP address must be a valid IPv4 x.x.x.x')
    if (ip_addr.startswith('10.') or
        (ip_addr.startswith('172.') and
        int(ip_addr.split('.')[1]) in range(16, 32)) or
        ip_addr.startswith('192.168.')):
        return True
    return False


def _is_localnet_172(addr: str) -> bool:
    if (addr.startswith('172.') and
        int(addr.split('.')[1] in range(16, 31 + 1))):
        return True
    return False


def _is_localnet_192(addr: str) -> bool:
    if addr.startswith('192.168.'):
        return True
    return False


def _is_same_subnet(src: str, dst: str) -> bool:
    src_parts = src.split('.')
    dst_parts = dst.split('.')
    for part in range(0, 3):
        if src_parts[part] != dst_parts[part]:
            return False
    return True


def _is_multicast(addr: str) -> bool:
    MULTICAST_RANGE = (224, 239 + 1)
    first_octet = int(addr.split('.')[0])
    if first_octet == 255:
        return True
    elif first_octet in range(MULTICAST_RANGE[0], MULTICAST_RANGE[1]):
        return True
    return False


def _is_local_traffic(packet: SharkPacket) -> bool:
    """Returns true if the source is on the LAN and destinations are cast.
    
    Args:
        packet: A pyshark Packet capture
    
    Returns:
        True if both addresses are in the LAN range 192.168.x.y 
    """
    src, dst = _get_src_dst(packet)
    if LOCALNET_172:
        if (_is_localnet_172(src) and _is_localnet_172(dst) and
            _is_same_subnet(src, dst)):
            # if DEBUG_VERBOSE:
            #     _log.debug(f'Local LAN packet {src} -> {dst}')
            return True
        if ((_is_localnet_172(src) and _is_multicast(dst)) or
            (_is_multicast(src) and _is_localnet_172(dst))):
            # if DEBUG_VERBOSE:
            #     _log.debug(f'Local multicast packet {src} -> {dst}')
            return True
    if LOCALNET_192:
        if (_is_localnet_192(src) and _is_localnet_192(dst) and
            _is_same_subnet(src, dst)):
            # if DEBUG_VERBOSE:
            #     _log.debug(f'Local LAN packet {src} -> {dst}')
            return True
        if ((_is_localnet_192(src) and _is_multicast(dst)) or
            (_is_multicast(src) and _is_localnet_192(dst))):
            # if DEBUG_VERBOSE:
            #     _log.debug(f'Local multicast packet {src} -> {dst}')
            return True
    if _is_multicast(src) and _is_multicast(dst):
        # if DEBUG_VERBOSE:
        #     _log.debug(f'Local multicast packet {src} -> {dst}')
        return True
    return False


def _is_tcp_reset(packet: SharkPacket) -> bool:
    # TODO: look for RST flag
    raise NotImplementedError


def _check_flags(packet: SharkPacket) -> 'dict|None':
    # TODO: tcp.analysis.flags && !tcp.analysis.window_update && !tcp.analysis.keep_alive && !tcp.analysis.keep_alive_ack
    # TODO: tcp.analysis.retransmission
    IGNORE = [
        'analysis_flags',
    ]
    if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'analysis_flags'):
        bad_packet = {}
        for attr in dir(packet.tcp):
            if attr.startswith('analysis_') and attr not in IGNORE:
                bad_packet[attr] = getattr(packet.tcp, attr)
        return bad_packet


def _clean_path(pathname: str) -> str:
    """Adjusts relative and shorthand filenames for OS independence.
    
    Args:
        pathname: The full path/to/file
    
    Returns:
        A clean file/path name for the current OS and directory structure.
    """
    if pathname.startswith('$HOME/'):
        pathname = pathname.replace('$HOME', str(Path.home()), 1)
    elif pathname.startswith('~/'):
        pathname = pathname.replace('~', str(Path.home()), 1)
    if os.path.isdir(os.path.dirname(pathname)):
        return os.path.realpath(pathname)
    else:
        raise ValueError(f'Directory {os.path.dirname(pathname)} not found')


class SimplePacket:
    """A simplified packet representation.
    
    Attributes:
        a_b (bool): Direction of travel relative to parent conversation
        application (str): The analysis-derived application
        highest_layer (str): The highest Wireshark-derived packet layer
        timestamp (float): The unix timestamp of the capture to 3 decimal places
        size (int): Size in bytes
        transport (str): The transport type
        src (str): Source IP address
        dst (str): Destination IP address
        srcport (int): Source port
        dstport (int): Destination port
        bad_packet (dict): Metadata present if the packet is suspected to be bad

    """
    def __init__(self, packet: SharkPacket, parent_hosts: tuple) -> None:
        self._parent_hosts = parent_hosts
        self.timestamp = round(float(packet.sniff_timestamp), 3)
        self.size = int(packet.length)
        self.transport = packet.transport_layer
        if packet.transport_layer:
            self.transport = packet.transport_layer
            self.stream_id = str(packet[self.transport].stream)
        elif hasattr(packet, 'icmp') and packet['icmp'].udp_port:
            self.transport = 'UDP'
            self.stream_id = str(packet['icmp'].udp_stream)
        else:
            raise ValueError('Unable to determine transport'
                                f' for {packet.highest_layer} packet')
        self.src, self.dst = _get_src_dst(packet)
        self.srcport, self.dstport = _get_ports(packet)
        self.highest_layer = str(packet.highest_layer).upper()
        self.application = _get_application(packet)
        self.a_b = True if self.src == self._parent_hosts[0] else False
        self.bad_packet = _check_flags(packet)


class Conversation:
    """Encapsulates all traffic between two endpoints.
    
    Attributes:
        application: The dominant application layer
        hosts: A tuple of IP addresses (host A, host B)
        a_b: The count of transactions from host A to host B
        b_a: The count of transactions from host B to host A
        stream_id: The stream ID from the tshark capture
        transport: The transport used e.g. TCP, UDP
        ports: A list of transport ports used e.g. [1883]
        start_ts: The unix timestamp of the first packet sent
        packets: A list of all the packets summarized
        packet_count: The size of the packets list
        bytes_total: The total number of bytes in the conversation
        bad_packet_count: The number of suspected bad packets
            (includes retransmit)
        bytes_bad: The byte count of the suspected bad packets
            (includes retransmitted bytes)
        retransmit_count: The number of suspected retransmitted packets
        bytes_retransmit: The total retransmitted bytes

    """
    def __init__(self, packet: SharkPacket = None, number: int = None):
        self.number = number
        self.application: str = None
        self.hosts: tuple = None
        self.a_b: int = 0
        self.b_a: int = 0
        self.stream_id: str = None
        self.transport: str = None
        self.ports: list = []
        self.packets: 'list[SimplePacket]' = []
        self.packet_count: int = 0
        self.bad_packet_count: int = 0
        self.retransmit_count: int = 0
        self.bytes_total: int = 0
        self.bytes_bad: int = 0
        self.bytes_retransmit: int = 0
        self.start_ts: float = None
        if packet is not None:
            self.packet_add(packet)
    
    def __repr__(self) -> str:
        return json.dumps(vars(self), indent=2)

    def is_packet_in_flow(self, packet: SharkPacket) -> bool:
        """Returns True if the packet is between the object's hosts.
        
        Args:
            packet: A pyshark Packet capture
        
        Returns:
            True if the packet source and destination are the hosts.
        """
        if self.hosts is None:
            return False
        (src, dst) = _get_src_dst(packet)
        if _is_local_traffic(packet):
            return False
        stream_id = None
        if packet.transport_layer:
            transport = packet.transport_layer
            try:
                stream_id = packet[transport].stream
            except AttributeError as err:
                _log.exception(f'{err}')
        elif hasattr(packet, 'icmp') and packet['icmp'].udp_stream:
            stream_id = packet['icmp'].udp_stream
        if (src in self.hosts and dst in self.hosts and
            stream_id is not None and
            stream_id == self.stream_id):
            return True
        return False
    
    def packet_add(self, packet: SharkPacket) -> bool:
        """Adds the packet summary and metadata to the Conversation.
        
        Args:
            packet: A pyshark Packet capture
        
        Returns:
            True if the packet was added to the Conversation.
        
        Raises:
            ValueError if the packet is missing transport_layer or has a
                different transport or stream ID than the conversation.

        """
        if not(isinstance(packet, SharkPacket)):
            raise ValueError('packet is not a valid pyshark Packet')
        if self.hosts is None:
            self.hosts = _get_src_dst(packet)
        elif not(self.is_packet_in_flow(packet)):
            _log.warning(f'Packet {packet.number} not in flow {self.number}')
            return False
        try:
            simple_packet = SimplePacket(packet, self.hosts)
        except Exception as err:
            _log.error(err)
            raise err
        isotime = datetime.utcfromtimestamp(simple_packet.timestamp).isoformat()[0:23]
        if DEBUG_VERBOSE:
            _log.debug(f'Adding packet {packet.number}'
                       f' to conversation {self.number or 0}:'
                       f'{isotime}|{simple_packet.application}|'
                       f'({simple_packet.transport}.{simple_packet.stream_id}'
                       f':{simple_packet.dstport})'
                       f'|{simple_packet.size} bytes'
                       f'|{simple_packet.src}-->{simple_packet.dst}')
        if simple_packet.src == self.hosts[0]:
            self.a_b += 1
        else:
            self.b_a += 1
        if self.transport is None:
            self.transport = simple_packet.transport
        if simple_packet.srcport not in self.ports:
            self.ports.append(simple_packet.srcport)
        if simple_packet.dstport not in self.ports:
            self.ports.append(simple_packet.dstport)
        if self.stream_id is None:
            self.stream_id = simple_packet.stream_id
        elif simple_packet.stream_id != self.stream_id:
            err = (f'Packet {packet.number} expected stream {self.stream_id}'
                   f' but got {simple_packet.stream_id}')
            _log.error(err)
            raise ValueError(err)
        self.packet_count += 1
        self.bytes_total += simple_packet.size
        if self.start_ts is None:
            self.start_ts = simple_packet.timestamp
        try:
            if simple_packet.bad_packet:
                if 'analysis_retransmission' in simple_packet.bad_packet:
                    self.retransmit_count += 1
                    self.bytes_retransmit += simple_packet.size
                self.bad_packet_count += 1
                self.bytes_bad += simple_packet.size
                if DEBUG_VERBOSE:
                    _log.debug(f'Bad packet {packet.number}'
                               f' ({simple_packet.bad_packet})')
            self.packets.append(simple_packet)
            if self.application is None:
                self.application = simple_packet.application
            elif self.application != simple_packet.application:
                _log.warning(f'Packet {packet.number}'
                             f' expected application {self.application}'
                             f' but got {simple_packet.application}')
            return True
        except Exception as err:
            _log.exception(err)
            raise err
        
    @staticmethod
    def _get_intervals_by_length(packets_by_size: dict) -> dict:
        intervals = {}
        for packet_size in packets_by_size:
            packet_list: list[SimplePacket] = packets_by_size[packet_size]
            intervals[packet_size] = None
            if len(packet_list) == 1:
                application = packet_list[0].application
                application += f'_{packet_size}B'
                intervals[application] = None
                del intervals[packet_size]
                continue
            is_same_application = True   # starting assumption
            for i, packet in enumerate(packet_list):
                if i == 0:
                    # skip the first one since we are looking for time between
                    continue
                if (packet_list[i - 1].application != packet.application):
                    is_same_application = False
                this_interval = (
                    packet.timestamp - packet_list[i - 1].timestamp
                )
                if intervals[packet_size] is None:
                    intervals[packet_size] = this_interval
                else:
                    intervals[packet_size] = (round((intervals[packet_size] +
                                              this_interval) / 2, 3))
            if is_same_application:
                application = packet_list[0].application
            else:
                application = 'mixed'
            application += f'_{packet_size}B'
            intervals[application] = intervals[packet_size]
            del intervals[packet_size]
        return intervals
    
    def data_series_packet_size(self) -> list:
        """Generates a data series with timestamp and packet size.

        Example: [(12345.78, 42), (12355.99, 42)]

        Returns:
            A list of tuples consisting of (unix_timestamp, size_bytes)

        """
        series = []
        for packet in self.packets:
            datapoint = (packet.timestamp, packet.size)
            series.append(datapoint)
        return series

    def data_series_packet_size_good_bad(self) -> 'tuple[list, list]':
        good_series = []
        bad_series = []
        for packet in self.packets:
            datapoint = (packet.timestamp, packet.size)
            if not packet.bad_packet:
                good_series.append(datapoint)
            else:
                bad_series.append(datapoint)
        return (good_series, bad_series)

    def group_packets_by_size(self) -> tuple:
        """Creates dictionaries keyed by similar packet size and direction.
        
        Returns:
            A tuple with 2 dictionaries representing flows A-B and B-A.
            In each dictionary the keys are the packet size and the value
                is a list of the packets of that size.

        """
        packets_a_b = {}
        packets_b_a = {}
        lengths = []
        for packet in self.packets:
            if packet.a_b:
                if packet.size not in packets_a_b:
                    packets_a_b[packet.size] = list()
                packets_a_b[packet.size].append(packet)
            else:
                if packet.size not in packets_b_a:
                    packets_b_a[packet.size] = list()
                packets_b_a[packet.size].append(packet)
            lengths.append(packet.size)
        return (packets_a_b, packets_b_a)

    def intervals(self) -> dict:
        """Analyzes the conversation and returns metrics in a dictionary.
        
        Returns:
            A dictionary including:
                * A (str): The host IP that initiated the conversation
                * B (str): The host IP opposite to A
                * AB_intervals (dict): A dictionary with grouped packet size
                average repeat interval A to B in seconds
                * AB_intervals (dict): A dictionary with grouped packet size
                average repeat interval B to A in seconds

        """
        # sort by direction and packet size
        packets_a_b, packets_b_a = self.group_packets_by_size()
        # TODO: dominant packet list based on quantity * size
        return {
            'hosts': self.hosts,
            'AB_intervals': self._get_intervals_by_length(packets_a_b),
            'BA_intervals': self._get_intervals_by_length(packets_b_a)
        }


class PacketStatistics:
    """Encapsulates packet-level statistics from a capture over time.
    
    Attributes:
        conversations (list): A list of Conversation elements for analyses.
        packet_count (int): The total number of packets
        bytes_total (int): The total amount of data in bytes

    """
    def __init__(self,
                 source_filename: str = None,
                 ) -> None:
        """Creates a PacketStatistics object.
        
        Args:
            source_filename: An optional tie to the source pcap file

        """
        self._source_filename: str = source_filename
        self.conversations: list[Conversation] = []
        self._packet_count: int = 0
        self._unhandled_packet_types: list = []
        self._unhandled_packet_count: int = 0
        self._local_packet_count: int = 0
        self._bytes_total: int = 0
        self._unhandled_bytes: int = 0
        self._local_bytes: int = 0
        self._first_packet_ts: float = None
        self._last_packet_ts: float = None
    
    @property
    def packet_count(self) -> int:
        return self._packet_count
    
    @property
    def bytes_total(self) -> int:
        return self._bytes_total
    
    @property
    def duration(self) -> int:
        duration = int(self._last_packet_ts - self._first_packet_ts)
        if self._source_filename is not None:
            fileparts = str(self._source_filename.split('.pcap')[0]).split('_')
            try:
                file_duration = int(fileparts[len(fileparts) - 1])
                duration = max(file_duration, duration)
            except:
                pass
        return duration
    
    def packet_add(self, packet: SharkPacket) -> None:
        """Adds a packet to the statistics for analyses.
        
        Args:
            packet: A pyshark Packet object.

        """
        self._packet_count += 1
        self._bytes_total += int(packet.length)
        ts = round(float(packet.sniff_timestamp), 3)
        if self._first_packet_ts is None:
            self._first_packet_ts = ts
        self._last_packet_ts = ts
        if hasattr(packet, 'arp'):
            self._process_arp(packet)
        elif hasattr(packet, 'tcp') or hasattr(packet, 'udp'):
            self._process_ip(packet)
        elif hasattr(packet, 'icmp'):
            self._process_ip(packet)
        else:
            self._process_unhandled(packet)
    
    def _process_arp(self, packet: SharkPacket):
        arp_desc = f'{packet.arp.src_proto_ipv4}-->{packet.arp.dst_proto_ipv4}'
        if not _is_local_traffic(packet):
            _log.warning(f'Non-local ARP packet {arp_desc}')
        else:
            if DEBUG_VERBOSE:
                _log.debug(f'Local ARP {arp_desc} (ignored from statistics)')

    def _process_ip(self, packet: SharkPacket):
        in_conversation = False
        if _is_local_traffic(packet):
            if DEBUG_VERBOSE:
                _log.debug(f'Ignoring packet {packet.number} local traffic')
            self._local_packet_count += 1
            self._local_bytes += int(packet.length)
            return
        for conversation in self.conversations:
            if conversation.is_packet_in_flow(packet):
                conversation.packet_add(packet)
                in_conversation = True
                break
        if not in_conversation:
            conversation_number = len(self.conversations) + 1
            if DEBUG_VERBOSE:
                _log.debug(f'Found new conversation ({conversation_number})')
            conversation = Conversation(packet, conversation_number)
            self.conversations.append(conversation)

    def _process_unhandled(self, packet: SharkPacket):
        packet_type = packet.highest_layer
        self._unhandled_packet_count += 1
        self._unhandled_bytes += int(packet.length)
        if packet_type not in self._unhandled_packet_types:
            _log.warning(f'Packet {packet.number}'
                         f' unhandled packet type {packet_type}')
            self._unhandled_packet_types.append(packet_type)

    def data_series_application_size(self, split_bad: bool = False) -> dict:
        """Returns a set of data series by conversation application.
        
        Example: {'MQTT': [(12345.67, 42)]}

        Args:
            split_bad: if True will split out bad packets as a series.

        Returns:
            A dictionary with keys showing the application and values are
                tuples with (unix_timestamp, size_in_bytes)

        """
        multi_series = {}
        for conversation in self.conversations:
            app = conversation.application
            if app in multi_series:
                multi_series[app] = (multi_series[app] +
                    conversation.data_series_packet_size())
            else:
                multi_series[app] = conversation.data_series_packet_size()
            multi_series[app].sort(key=lambda tup: tup[0])
        return multi_series

    def analyze_conversations(self) -> dict:
        """Analyzes all conversations to produce a summary.
        
        Returns:
            A dict with keys as unique host pairs "('A', 'B')" summary dict:
                {
                    count: `int`,
                    applications: `list[str]`,
                    start_times: `list[float]`,
                    packet_intervals: {
                        AB_intervals: {
                            '<transport>_<protocol>_<bytesize>': `int`|`None`,
                        },
                        BA_intervals: {
                            '<transport>_<protocol>_<bytesize>': `int`|`None`,
                        }
                    },
                    repeat_mean: `int`,
                    repeat_stdev: `int`
                }

        """
        results = {}
        for conversation in self.conversations:
            hosts_str = str(conversation.hosts)
            intervals = conversation.intervals()
            intervals.pop('hosts', None)
            bad_packet_count = conversation.bad_packet_count
            if hosts_str not in results:
                results[hosts_str] = {
                    'count': 1,
                    'applications': [conversation.application],
                    'start_times': [conversation.start_ts],
                    'packet_intervals': intervals,
                    'bytes': conversation.bytes_total,
                    'bad_packet_count': bad_packet_count,
                    'bytes_bad': conversation.bytes_bad,
                    'retransmit_count': conversation.retransmit_count,
                    'retransmit_bytes': conversation.bytes_retransmit,
                }
            else:
                results[hosts_str]['count'] += 1
                app = conversation.application
                if app not in results[hosts_str]['applications']:
                    results[hosts_str]['applications'].append(app)
                results[hosts_str]['start_times'].append(conversation.start_ts)
                prior = results[hosts_str]['packet_intervals']
                results[hosts_str]['packet_intervals'] = {**prior, **intervals}
                results[hosts_str]['bad_packet_count'] += bad_packet_count
        for key in results:
            times = results[key]['start_times']
            results[key]['repeat_mean'] = None
            results[key]['repeat_stdev'] = None
            if len(times) == 1:
                continue
            intervals = []
            for i, ts in enumerate(times):
                if i == 0:
                    continue
                intervals.append(ts - times[i - 1])
            if len(intervals) > 1:
                results[key]['repeat_mean'] = int(statistics.mean(intervals))
                results[key]['repeat_stdev'] = int(statistics.stdev(intervals))
        return results
    
    def unique_host_pairs(self) -> 'list[tuple]':
        """Lists unique host pairs as tuples."""
        results = []
        for conversation in self.conversations:
            if conversation.hosts not in results:
                results.append(conversation.hosts)
        return results


def _get_event_loop() -> tuple:
    loop_is_new = False
    try:
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    except RuntimeError as err:
        if 'no running event loop' not in f'{err}':
            raise err
        loop = asyncio.new_event_loop()
        loop_is_new = True
    asyncio.set_event_loop(loop)
    asyncio.get_child_watcher().attach_loop(loop)
    return loop, loop_is_new


def process_pcap(filename: str,
                 display_filter: str = None,
                 queue: Queue = None,
                 debug: bool = False,
                 ) -> PacketStatistics:
    """Processes a PCAP file to create metrics for conversations.

    To run in the background use a multiprocessing.Process and Queue:
    ```
    import multiprocessing
    import queue

    q = multiprocessing.Queue()
    kwargs = {
        'filename': filename,
        'display_filter': display_filter,
        'queue': q,
    }
    process = multiprocessing.Process(target=process_pcap,
                                      name='packet_capture',
                                      kwargs=kwargs)
    process.start()
    while process.is_alive():
        try:
            while True:
                packet_statistics = q.get(block=False)
        except queue.Empty:
            pass
    process.join()
    ```
    
    Args:
        filename: The path/name of the PCAP file
        display_filter: An optional tshark display filter
        queue: An optional multiprocessing Queue (e.g. required for Flask)
        debug: Enables pyshark debug output
    
    Returns:
        A PacketStatistics object with data and analytics functions.

    """
    packet_stats = PacketStatistics(source_filename=filename)
    file = _clean_path(filename)
    loop: asyncio.AbstractEventLoop = None
    loop_is_new = False
    if queue is not None:
        loop, loop_is_new = _get_event_loop()
    capture = pyshark.FileCapture(input_file=file,
                                  display_filter=display_filter,
                                  eventloop=loop)
    capture.set_debug(debug)
    packet_number = 0
    handled_exceptions = []
    for packet in capture:
        assert isinstance(packet, SharkPacket)
        packet_number += 1
        # DEV: Uncomment below for specific step-through troubleshooting
        if DEBUG_PACKET_NUMBER and packet_number == DEBUG_PACKET_NUMBER:
            _log.info(f'Investigate packet: {int(packet.number)}')
        try:
            packet_stats.packet_add(packet)
        except NotImplementedError as err:
            if str(err) not in handled_exceptions:
                sio = io.StringIO()
                ei = sys.exc_info()
                tb = ei[2]
                traceback.print_exception(ei[0], ei[1], tb, None, sio)
                s = sio.getvalue()
                sio.close()
                stack = s.split('\n')
                #: each stack call is 2 lines, the last 2 lines are the error
                #:   so the last call meta is 4-deep and the call itself 3-deep
                last_call = stack[-4:-2]
                err_prefix = 'pyshark'
                if 'fieldedge_pcap/pcap.py' in last_call[0]:
                    err_prefix = 'fieldedge_pcap'
                _log.warning(f'{err_prefix} (packet {packet.number}): {err}')
                handled_exceptions.append(str(err))
        except TSharkCrashException as err:
            _log.error(f'tshark (packet {packet_number}): {err}')
            break
        except:
            #TODO: better error capture e.g. appears to have been cut short use editcap
            # https://tshark.dev/share/pcap_preparation/
            _log.exception(f'Packet {packet_number} processing ERROR')
            break
    capture.close()
    if loop_is_new:
        loop.close()
    if queue is not None:
        queue.put(packet_stats)
    else:
        return packet_stats


def pcap_filename(duration: int, interface: str = '') -> str:
    """Generates a pcap filename using datetime of the capture start.
    
    The datetime is UTC, and the duration is in seconds.

    Returns:
        A string formatted as `capture_YYYYmmddTHHMMSS_DDDDD.pcap`.

    """
    dt = datetime.utcnow().isoformat().replace('-', '').replace(':', '')[0:15]
    filename = f'capture_{dt}_{duration}' + f'_{interface}' if interface else ''
    return f'{filename}.pcap'


def create_pcap(interface: str = 'eth1',
                duration: int = 60,
                filename: str = None,
                target_directory: str = '$HOME',
                queue: Queue = None,
                debug: bool = False,
                ) -> str:
    """Creates a packet capture file of a specified interface.

    A subdirectory is created in the `target_directory`, if none is specified it
    stores to the user's home directory.
    The subdirectory name is `capture_YYYYmmdd`.
    The filename can be specified or `capture_YYYYmmddTHHMMSS_DDDDD.pcap`
    format will be used.
    To run in the background use a multiprocessing.Process and Queue:
    ```
    queue = multiprocessing.Queue()
    kwargs = {
        'interface': my_interface,
        'duration': my_duration,
        'filename': pcap_filename(duration),
        'target_directory': parent_folder,
        'queue': queue,
    }
    capture_process = multiprocessing.Process(target=create_pcap,
                                              name='packet_capture',
                                              kwargs=kwargs)
    capture_process.start()
    capture_process.join()
    capture_file = queue.get()
    ```

    Often times the packet capture process will result in a corrupted file or
    have duplicate packets.
    To check for corruption run `tshark -r <capture_file>` which will have a
    returncode 2 if corrupt, and stderr will include
    'appears to have been cut short'.
    To fix a corrupted file run `editcap <capture_file> <capture_file>` which
    should have a returncode 0.
    
    Args:
        interface: The interface to capture from e.g. `eth1`
        duration: The duration of the capture in seconds
        target_directory: The path to save the capture to
        finish_event: A threading Event that gets set when capture is complete

    Returns:
        The full file/path name if no event is passed in.

    """
    if filename is None:
        filename = pcap_filename(duration)
    target_directory = _clean_path(target_directory)
    subdir = f'{target_directory}/{filename[0:len("capture_YYYYmmdd")]}'
    filepath = f'{subdir}/{filename}'
    if not os.path.isdir(subdir):
        os.makedirs(subdir)
    loop: asyncio.AbstractEventLoop = None
    loop_is_new = False
    if queue is not None:
        loop, loop_is_new = _get_event_loop()
    capture = pyshark.LiveCapture(interface=interface,
                                  output_file=filepath,
                                  eventloop=loop)
    capture.set_debug(debug)
    capture.sniff(timeout=duration)
    capture.close()
    if loop_is_new:
        loop.close()
    if queue is not None:
        queue.put(filepath)
    else:
        return filepath
