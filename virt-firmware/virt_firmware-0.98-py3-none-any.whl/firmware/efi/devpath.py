#!/usr/bin/python
"""
efi device path decoder

EFI_DEVICE_PATH_PROTOCOL (Protocol/DevicePath.h)
"""

import struct
import collections

from virt.firmware.efi import guids
from virt.firmware.efi import ucs16

class DevicePathElem:
    """ class reprsenting an efi device path element """

    def __init__(self, data = None):
        self.devtype = 0x7f
        self.subtype = 0xff
        self.data    = b''
        if data:
            (self.devtype, self.subtype, size) = struct.unpack_from('=BBH', data)
            self.data = data[ 4 : size ]

    def set_ipv4(self):
        self.devtype = 0x03
        self.subtype = 0x0c
        self.data    = bytes(23) # use dhcp

    def set_uri(self, uri):
        self.devtype = 0x03
        self.subtype = 0x18
        self.data    = str(uri).encode()

    def fmt_hw(self):
        if self.subtype == 0x01:
            (func, dev) = struct.unpack_from('=BB', self.data)
            return f'PCI(dev={dev:02x}:{func:x})'
        if self.subtype == 0x04:
            guid = guids.parse_bin(self.data, 0)
            return f'VendorHW({guid})'
        return f'HW(subtype=0x{self.subtype:x})'

    def fmt_acpi(self):
        try:
            if self.subtype == 0x01:
                (hid, uid) = struct.unpack_from('=LL', self.data)
                if hid == 0xa0341d0:
                    return 'PciRoot()'
                return f'ACPI(hid=0x{hid:x},uid=0x{uid:x})'
            if self.subtype == 0x03:
                adr = struct.unpack_from('=L', self.data)
                return f'GOP(adr=0x{adr[0]:x})'
            return f'ACPI(subtype=0x{self.subtype:x})'
        except struct.error as err:
            return f'ACPI(ERROR:{err})'

    # pylint: disable=too-many-return-statements
    def fmt_msg(self):
        if self.subtype == 0x02:
            (pun, lun) = struct.unpack_from('=HH', self.data)
            return f'SCSI(pun={pun},lun={lun})'
        if self.subtype == 0x05:
            (port, intf) = struct.unpack_from('=BB', self.data)
            return f'USB(port={port})'
        if self.subtype == 0x0b:
            return 'MAC()'
        if self.subtype == 0x0c:
            return 'IPv4()'
        if self.subtype == 0x0d:
            return 'IPv6()'
        if self.subtype == 0x12:
            (port, mul, lun) = struct.unpack_from('=HHH', self.data)
            return f'SATA(port={port})'
        if self.subtype == 0x18:
            return f'URI({self.data.decode()})'
        if self.subtype == 0x1f:
            return 'DNS()'
        return f'Msg(subtype=0x{self.subtype:x})'

    def fmt_media(self):
        if self.subtype == 0x01:
            (pnr, pstart, pend) = struct.unpack_from('=LQQ', self.data)
            return f'Partition(nr={pnr})'
        if self.subtype == 0x04:
            path = ucs16.from_ucs16(self.data, 0)
            return f'FilePath({path})'
        if self.subtype == 0x06:
            guid = guids.parse_bin(self.data, 0)
            return f'FvFileName({guid})'
        if self.subtype == 0x07:
            guid = guids.parse_bin(self.data, 0)
            return f'FvName({guid})'
        return f'Media(subtype=0x{self.subtype:x})'

    def size(self):
        return len(self.data) + 4

    def __bytes__(self):
        hdr = struct.pack('=BBH', self.devtype, self.subtype, self.size())
        return hdr + self.data

    def __str__(self):
        if self.devtype == 0x01:
            return self.fmt_hw()
        if self.devtype == 0x02:
            return self.fmt_acpi()
        if self.devtype == 0x03:
            return self.fmt_msg()
        if self.devtype == 0x04:
            return self.fmt_media()
        return f'Unknown(type=0x{self.devtype:x},subtype=0x{self.subtype:x})'

class DevicePath(collections.UserList):
    """ class reprsenting an efi device path """

    def __init__(self, data = None):
        super().__init__()
        if data:
            pos = 0
            while pos < len(data):
                elem = DevicePathElem(data[pos:])
                if elem.devtype == 0x7f:
                    break
                self.append(elem)
                pos += elem.size()

    @staticmethod
    def uri(uri):
        path = DevicePath()
        elem = DevicePathElem()
        elem.set_uri(uri)
        path.append(elem)
        return path

    def __bytes__(self):
        blob = b''
        for elem in list(self):
            blob += bytes(elem)
        blob += bytes(DevicePathElem())
        return blob

    def __str__(self):
        return "/".join(map(str, list(self)))
