"""
  network.py
 
  Copyright (C) 2022 by RStudio, PBC
 
"""
import jupyterlab_rsw.process as ps

import os
import re
from typing import Callable, Dict, List

# TCP File Field Indices
LOCAL_ADDR_IND = 1 # TCP Local Address Field
STATE_IND = 3 # TCP State Field
UID_IND = 7 # TCP Uid Field
INODE_IND = 9 # TCP INode Field

TCP_LISTEN_STATE = '0A' # TCP LISTEN State

class TcpInfo:
  def __init__(self, address: str, port: int):
    self.address: str = address
    self.port: int = int(port, 16)

  def to_string(self) -> str:
    return self.address + ':' + self.port

  def equals(self, other) -> bool:
    return self.address == other.address and self.port == other.port

class ListeningProcess:
  def __init__(self, pid: int, name: str, args: List[str], addresses: List[TcpInfo], wd: str):
    self.pid = pid
    self.name = name
    self.args = args
    self.addresses = addresses
    self.wd = wd

  def to_string(self) -> str:
    res = f"({self.pid}) {self.name} {' '.join(self.args)}"
    for val in self.addresses:
      res += f'\n{val.to_string()}'
    return res

async def get_listening_processes() -> List[ListeningProcess]:
    # try/except blocks are used because we've seen environments where /proc/net/tcp6 did not exist
    # that caused the extension to fail to parse either file
    try:
        with open('/proc/net/tcp') as f:
            tcp_data = f.read()
    except:
        tcp_data = ''
    
    try:
        with open('/proc/net/tcp6') as f:
            tcp6_data = f.read()
    except:
        tcp6_data = ''

    net_info: Dict[int, TcpInfo] = parse_tcp_info(tcp_data, tcp6_data)

    processes: List[ps.Process] = await ps.get_processes()
    listeners: List[ListeningProcess] = []

    if processes is None:
        return listeners

    for proc in processes:
        listen_info: List[TcpInfo] = []
        for inode in proc.inodes:
            if inode in net_info:
                listen_info.append(net_info.get(inode))

        if len(listen_info) > 0:
            listeners.append(ListeningProcess(proc.pid, proc.name, proc.args, listen_info, proc.wd))

    return listeners

def parse_tcp_info(ipv4Contents: str, ipv6Contents: str) -> Dict[int, TcpInfo]:
    curr_uid = os.geteuid()
    ipv4_lines: List[str] = ipv4Contents.splitlines()
    ipv6_lines: List[str] = ipv6Contents.splitlines()

    result: Dict[int, TcpInfo] = {}

    def process_line(line: str, index: int, address_parser: Callable[[str], TcpInfo]) -> Dict[int, TcpInfo]:
        # Skip the first line, it's a header.
        if index == 0 or len(line.strip()) == 0:
            return
    
        # If there aren't at least as many fields as are needed to get the inode value, skip self line.
        fields: List[str] = line.strip().split()
        if len(fields) < INODE_IND + 1:
            print(f'Failed to parse line of /proc/net/tcp or /proc/net/tcp6: {line}')
            return
    
        uid = fields[UID_IND].strip()
        if uid is None or not uid.isnumeric():
            print(f'Failed to parse user ID from line of /proc/net/tcp or /proc/net/tcp6: {line}')
            return
        elif int(uid) != curr_uid:
            # This line doesn't belong to the current user so it's not relevant. Skip it.
            return
    
        info: TcpInfo = address_parser(fields[LOCAL_ADDR_IND])
        if not info:
            print(f'Failed to parse address from line of /proc/net/tcp or /proc/net/tcp6: {line}')
            return
    
        inode_val: int = fields[INODE_IND].strip()
        if inode_val is None:
            print(f'Failed to parse inode value from line of /proc/net/tcp or /proc/net/tcp6: {line}')
            return
        elif info.port != 0 and inode_val != 0 and fields[STATE_IND] == TCP_LISTEN_STATE:
            result[int(inode_val)] = info
    
    for count, line in enumerate(ipv4_lines):
        process_line(line, count, convert_IPv4)

    for count, line in enumerate(ipv6_lines):
        process_line(line, count, convert_IPv6)

    return result

def convert_IPv4(hex_addr: str) -> TcpInfo:
    hex_addr = hex_addr.strip()
    if len(hex_addr) < 13:
        print(f'Invalid address string: {hex_addr} (expected length 13, got length {len(hex_addr)}')
        return

    split = hex_addr.split(':')
    if len(split) != 2:
        print(f"Invalid address string: {hex_addr} (expected exactly one ':' character")
        return
    
    address = f'{int(split[0][6:8], 16)}.{int(split[0][4:6], 16)}.{int(split[0][2:4], 16)}.{int(split[0][0:2], 16)}'

    return TcpInfo(address, split[1])

def convert_IPv6(hex_addr: str) -> TcpInfo:
    hex_addr = hex_addr.strip()
    if len(hex_addr) < 37:
        print(f'Invalid address string: {hex_addr} (expected length 37, got length {len(hex_addr)})')
        return

    split = hex_addr.split(':')
    if len(split) != 2:
      print(f"Invalid address string: {hex_addr} (expected exactly one ':' character)")
      return

    # IPV6 addresses are stored in words of 8 bytes, with the words from left to right, but the contents
    # of the words are right to left.
    values: List[str] = []
    for i in range (8, 32, 8):
      values.append(split[0][i - 2:i] + split[0][i - 4:i - 2])
      values.append(split[0][i - 6:i - 4] + split[0][i - 8:i - 6])

    addr = ''
    comp_started: bool = False
    comp_done: bool = False
    j: int = 0
    while j < len(values):
        if values[j] == '0000':
            if comp_done:
                addr += '0'
            comp_started = True
            j += 1
            continue

        elif comp_started and not comp_done:
            comp_done = True
            addr += '::'

        elif len(addr) > 0:
            addr += ':'

        addr += re.sub('^0+', '', values[j])
        j += 1

    if comp_started and not comp_done:
        addr += '::'

    return TcpInfo(addr, split[1])
