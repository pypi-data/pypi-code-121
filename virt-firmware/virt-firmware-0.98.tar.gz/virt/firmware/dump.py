#!/usr/bin/python
""" dump content of ovmf firmware volumes """
import sys
import lzma
import struct
import optparse
import collections

from virt.firmware.efi import guids
from virt.firmware.efi import ucs16
from virt.firmware.efi import efivar


########################################################################
# objects for parsed tree

class Edk2CommonBase(collections.UserList):
    """ base class for various edk2 firmware elements """

    def __init__(self):
        super().__init__()
        self.tlen = 0
        self.hlen = 0
        self.used = 0
        self.secname = None

    def align(self, align):
        self.used = (self.used + align - 1) & ~(align - 1)

    def parse_sections(self, data):
        self.used = 0
        while self.used + 8 < len(data):
            try:
                section = Edk2FileSection(data = data [ self.used : ] )
            except ValueError as err:
                self.append(f'{err}')
                return
            self.used += section.size()
            self.align(4)
            self.append(section)
            if section.typeid == 0x15:
                self.secname = section

    def size(self):
        return self.tlen


class OvmfMemoryRange:
    """ memory range """

    def __init__(self, sev = None, tdx = None, blob = None, name = None):
        self.filebase = None
        self.filesize = None
        self.membase  = None
        self.memsize  = None
        self.typeid   = None
        self.typename = None
        self.flags    = None
        if sev:
            self.parse_sev(sev)
        if tdx:
            self.parse_tdx(tdx)
        if blob and name:
            self.parse_direct(blob, name)

    def parse_sev(self, data):
        (self.membase, self.memsize, self.typeid) = \
            struct.unpack_from( "=LLL", data)
        self.typename = self.sev_type(self.typeid)

    def parse_tdx(self, data):
        (self.filebase, self.filesize, self.membase, self.memsize,
         self.typeid, self.flags) = \
             struct.unpack_from("=LLQQLL", data)
        self.typename = self.tdx_type(self.typeid)

    def parse_direct(self, blob, name):
        self.typename = name
        self.membase = int.from_bytes(blob [ 0:4 ] , byteorder='little', signed=False)
        self.memsize = int.from_bytes(blob [ 4:8 ] , byteorder='little', signed=False)

    @staticmethod
    def sev_type(typeid):
        id2name = {
            1 : "MEM",
            2 : "Secrets",
            3 : "CPUID",
        }
        return id2name.get(typeid, f'{typeid}')

    @staticmethod
    def tdx_type(typeid):
        id2name = {
            0 : "BFV (code)",
            1 : "CFV (vars)",
            2 : "TD Hob",
            3 : "MEM",
        }
        return id2name.get(typeid, f'{typeid}')

    def __str__(self):
        ret = f'mbase=0x{self.membase:x} msize=0x{self.memsize:x}'
        ret += f' type={self.typename}'
        if self.filesize:
            ret += f' fbase=0x{self.filebase:x} fsize=0x{self.filesize:x}'
        if self.flags:
            ret += f' flags=0x{self.flags:x}'
        return ret


class OvmfGuidListEntry(Edk2CommonBase):
    """ ovmf (reset vector) guid list entry """

    def __init__(self, data, offset):
        super().__init__()
        self.guid = None
        self.blob = None
        self.parse(data, offset)

    def parse(self, data, offset):
        (self.tlen, guid) = struct.unpack_from("<H16s", data, offset - 0x12)
        self.guid = guids.parse_bin(guid, 0)
        self.blob = data [ offset - self.tlen :
                           offset - 0x12 ]
        if str(self.guid) == guids.OvmfSevMetadataOffset:
            self.parse_sev(data)
        if str(self.guid) == guids.TdxMetadataOffset:
            self.parse_tdx(data)
        if str(self.guid) == guids.SevHashTableBlock:
            memrange = OvmfMemoryRange(blob = self.blob, name = 'HashTableBlock')
            self.append(memrange)
        if str(self.guid) == guids.SevSecretBlock:
            memrange = OvmfMemoryRange(blob = self.blob, name = 'SecretBlock')
            self.append(memrange)

    def parse_sev(self, data):
        pos = len(data) - int.from_bytes(self.blob, byteorder='little', signed=False)
        (magic, size, version, entries) = struct.unpack_from("=LLLL", data, pos)
        self.append(f'header size=0x{size:x} version={version} entries={entries}')
        for i in range(entries):
            memrange = OvmfMemoryRange(sev = data [ pos + 16 + i * 12 : ])
            self.append(memrange)

    def parse_tdx(self, data):
        pos = len(data) - int.from_bytes(self.blob, byteorder='little', signed=False)
        (magic, size, version, entries) = struct.unpack_from("=LLLL", data, pos)
        self.append(f'header size=0x{size:x} version={version} entries={entries}')
        for i in range(entries):
            memrange = OvmfMemoryRange(tdx = data [ pos + 16 + i * 32 : ])
            self.append(memrange)

    def __str__(self):
        data = self.blob.hex()
        return f'{guids.name(self.guid)} size=0x{self.tlen:x} data={data}'


class OvmfResetVector(Edk2CommonBase):
    """ edk2 ovmf reset vector """

    def __init__(self, data = None):
        super().__init__()
        self.tlen = len(data)
        if data:
            self.parse(data)

    def parse(self, data):
        pos = len(data) - 0x32
        (size, guid) = struct.unpack_from("<H16s", data, pos)
        if str(guids.parse_bin(guid, 0)) != guids.OvmfGuidList:
            return
        end = pos - size
        while pos - 0x12 > end:
            entry = OvmfGuidListEntry(data, pos)
            self.append(entry)
            pos -= entry.size()

    def __str__(self):
        return f'resetvector size=0x{self.tlen:x}'


class Edk2FileSection(Edk2CommonBase):
    """ edk2 ffs file section """

    type2name = {
        0x10 : "pe32",
        0x11 : "pic",
        0x12 : "te",
        0x13 : "dxe-depex",
        0x14 : "version",
        0x15 : "ui",
        0x16 : "compat16",
        0x17 : "fw-volume",
        0x18 : "freeform-guid",
        0x19 : "raw",
        0x1b : "pei-depex",
        0x1c : "smm-depex",
    }

    def __init__(self, data = None):
        super().__init__()
        self.guid = None
        self.blob = None
        self.typeid = 0
        if data:
            self.parse(data)

    def parse(self, data):
        (s1, s2, s3, self.typeid, xsize) = struct.unpack_from("=BBBBL", data)
        self.tlen = s1 | (s2 << 8) | (s3 << 16)
        self.hlen = 4
        if self.tlen == 0xffffffff:  # large section
            self.tlen = xsize
            self.hlen = 8

        if self.tlen == 0:
            raise ValueError('ERROR: section size is zero')
        if self.tlen > len(data):
            raise ValueError(f'ERROR: section size is too big (0x{self.tlen:x} > 0x{len(data):x})')

        if self.typeid == 0x02:
            self.guid = guids.parse_bin(data, self.hlen)
            (doff, attr) = struct.unpack_from("=HH", data, self.hlen + 16)
            if str(self.guid) == guids.LzmaCompress:
                unxz = lzma.decompress(data [ doff : self.tlen ] )
                self.parse_sections(unxz)

        elif self.typeid == 0x17:
            vol = Edk2Volume(data = data [ self.hlen : ])
            self.append(vol)

        else:
            self.blob = data [ self.hlen : ]

    def fmt_type(self):
        if self.typeid == 0x02:
            return guids.name(self.guid)
        name = self.type2name.get(self.typeid)
        if name:
            return name
        return f'0x{self.typeid:x}'

    def fmt_desc(self):
        if self.typeid == 0x14: # version
            build = struct.unpack_from("=H", self.blob)
            name = ucs16.from_ucs16(self.blob, 2)
            return f'build={build[0]} version={name}'
        if self.typeid == 0x15: # user interface
            name = ucs16.from_ucs16(self.blob, 0)
            return f'name={name}'
        return None

    def __str__(self):
        ret = f'section size=0x{self.tlen:x} type={self.fmt_type()}'
        desc = self.fmt_desc()
        if desc:
            ret += f' [ {desc} ]'
        return ret


class Edk2FfsFile(Edk2CommonBase):
    """ edk2 ffs file """

    type2name = {
        0x01 : 'raw',
        0x02 : 'freeform',
        0x03 : 'sec-core',
        0x04 : 'pei-core',
        0x05 : 'dxe-core',
        0x06 : 'peim',
        0x07 : 'driver',
        0x09 : 'application',
        0x0a : 'smm',
        0x0b : 'fw-volume',
        0x0d : 'smm-core',
        0xf0 : 'padding',
    }
    sectiontypes = (
        0x03, 0x04, 0x05,
        0x06, 0x07, 0x08, 0x09,
        0x0a, 0x0b, 0x0d,
    )

    def __init__(self, data = None):
        super().__init__()
        self.guid = None
        self.typeid = 0
        self.attr = 0
        if data:
            self.parse(data)

    def parse(self, data):
        (guid, self.typeid, self.attr, s1, s2, s3, state, xsize) = \
            struct.unpack_from('<16sxxBBBBBBL', data)
        self.guid = guids.parse_bin(guid, 0)
        if self.attr & 0x01: # large file
            self.tlen = xsize
            self.hlen = 12
        else:
            self.tlen = s1 | (s2 << 8) | (s3 << 16)
            self.hlen = 8

        if self.typeid == 0xff:
            raise ValueError('end of ffs file list')
        if self.tlen > len(data):
            raise ValueError(f'ERROR: file size is too big (0x{self.tlen:x} > 0x{len(data):x})')

        if self.has_sections():
            self.parse_sections(data [ 16 + self.hlen : self.tlen ])
        if str(self.guid) == guids.ResetVector:
            rv = OvmfResetVector(data [ 16 + self.hlen : self.tlen ])
            self.append(rv)

    def has_sections(self):
        return self.typeid in self.sectiontypes

    def fmt_type(self):
        name = self.type2name.get(self.typeid)
        if name:
            return name
        return f'0x{self.typeid:x}'

    def __str__(self):
        return f'ffsfile={guids.name(self.guid)} size=0x{self.tlen:x} type={self.fmt_type()}'


class Edk2Variable(Edk2CommonBase):
    """ edk2 (non-volatile) variable """

    def __init__(self, data = None):
        super().__init__()
        self.guid = None
        self.name = None
        self.blob = b''
        self.state = 0
        self.attr = 0
        if data:
            self.parse(data)

    def parse(self, data):
        (magic, self.state, self.attr, count, time, pk, nsize, dsize, guid) = \
            struct.unpack_from("<HBxLQ16sLLL16s", data)
        if magic != 0x55aa:
            raise ValueError('end of variable list')
        self.guid = guids.parse_bin(guid, 0)
        self.name = ucs16.from_ucs16(data, 60)
        self.blob = data [ 60 + nsize :
                           60 + nsize + dsize ]
        self.tlen = 60 + nsize + dsize

        if self.state == 0x3f:
            var = efivar.EfiVar(self.name,
                                guid = self.guid,
                                attr = self.attr,
                                data = self.blob)
            desc = var.fmt_data()
            if desc:
                self.append(desc)
            else:
                self.append(f'blob: {len(self.blob)} bytes')

    def fmt_state(self):
        if self.state == 0x3f:
            return None
        if self.state == 0x3c:
            return '(deleted)'
        return f'state=0x{self.state:x}'

    def __str__(self):
        ret = f'variable={guids.name(self.guid)} size=0x{self.tlen:x}'
        ret += f' attr=0x{self.attr:x} name={self.name}'
        state = self.fmt_state()
        if state:
            ret += f' {state}'
        return ret


class Edk2NvData(Edk2CommonBase):
    """ edk2 non-volatile data """

    def __init__(self, data = None):
        super().__init__()
        self.guid = None
        self.storefmt = 0
        self.state = 0
        if data:
            self.parse(data)

    def parse(self, data):
        (guid, self.tlen, self.storefmt, self.state) = struct.unpack_from("<16sLBB", data)
        self.guid = guids.parse_bin(guid, 0)
        self.parse_varlist(data [ 28 : ])

    def parse_varlist(self, data):
        self.used = 0
        while self.used + 60 < len(data):
            try:
                var = Edk2Variable(data [ self.used : ])
            except (ValueError, struct.error) as err:
                self.append(f'{err}')
                return
            self.used += var.size()
            self.align(4)
            self.append(var)

    def __str__(self):
        return (f'nvdata={guids.name(self.guid)} size=0x{self.tlen:x}'
                f' format=0x{self.storefmt:x} state=0x{self.state:x}')


# pylint: disable=too-many-instance-attributes
class Edk2Volume(Edk2CommonBase):
    """ edk2 firmware volume """

    def __init__(self, data = None, offset = 0):
        super().__init__()
        self.guid   = None
        self.attr   = 0
        self.xoff   = 0
        self.rev    = 0
        self.blocks = 0
        self.bsize  = 0
        self.offset = offset
        if data:
            self.parse(data)

    def parse(self, data):
        (guid, self.tlen, sig, self.attr, self.hlen,
         csum, self.xoff, self.rev, self.blocks, self.bsize) = \
            struct.unpack_from('<16x16sQLLHHHxBLL', data)
        self.guid = guids.parse_bin(guid, 0)

        if self.is_ffs():
            self.parse_ffs(data [ self.hlen : self.tlen ])
        if self.is_nvdata():
            nvdata = Edk2NvData(data [ self.hlen : self.tlen ])
            self.used += nvdata.size()
            self.append(nvdata)

    def parse_ffs(self, data):
        self.used = 0
        while self.used + 28 < len(data):
            try:
                item = Edk2FfsFile(data = data [ self.used : ] )
            except (ValueError, struct.error) as err:
                self.append(f'{err}')
                return
            self.used += item.size()
            self.align(8)
            self.append(item)

    def is_ffs(self):
        return str(self.guid) == guids.Ffs

    def is_nvdata(self):
        return str(self.guid) == guids.NvData

    def __str__(self):
        return (f'volume={guids.name(self.guid)} '
                f'offset=0x{self.offset:x} size=0x{self.tlen:x} '
                f'hlen=0x{self.hlen:x} xoff=0x{self.xoff:x} '
                f'rev={self.rev} blocks={self.blocks}*{self.bsize} '
                f'used={self.used * 100 / self.tlen:.1f}%')


class Edk2Capsule(Edk2CommonBase):
    """ efi signed capsule """

    def __init__(self, data = None):
        super().__init__()
        self.guid  = None
        self.hlen  = 0
        self.flags = 0
        self.clen  = 0
        if data:
            self.parse(data)

    def hex(self, data, start, end):
        while start < end:
            line = f'{start:04x}: '
            line += data [ start : start + 16 ].hex(' ')
            self.append(line)
            start += 16

    def parse(self, data):
        (guid, self.hlen, self.flags, self.clen) = \
            struct.unpack_from('<16sLLL', data)
        self.guid = guids.parse_bin(guid, 0)
        self.tlen = self.hlen # header only while we can't parse the content
        #self.hex(data, 28, 28 + 32)
        #self.hex(data, self.hlen, self.hlen + 64)

    def __str__(self):
        return(f'capsule={guids.name(self.guid)} hlen=0x{self.hlen:x} '
               f'flags=0x{self.flags:x} clen=0x{self.clen:x}')


class Edk2Image(collections.UserList):
    """ edk2 firmware image """

    def __init__(self, name = None, data = None):
        super().__init__()
        self.name = name
        if data:
            self.parse(data)

    def parse(self, data):
        pos = 0
        step = 1024
        while pos + 32 < len(data):
            (tlen, sig) = struct.unpack_from('<QL', data, pos + 32)
            if sig == 0x4856465f:
                vol = Edk2Volume(data = data [ pos : ],
                                 offset = pos)
                pos += vol.size()
                self.append(vol)
                continue

            guid = guids.parse_bin(data, pos)
            if str(guid) == guids.SignedCapsule:
                upd = Edk2Capsule(data [ pos : ] )
                pos += upd.size()
                self.append(upd)
                continue

            pos = (pos + step) & ~(step-1)
            continue

    def __str__(self):
        return f'image={self.name}'


########################################################################
# print stuff

def print_all(item, indent):
    if indent == 0:
        # workaround for old python
        print(f'{item}')
    else:
        print(f'{"":{indent}s}{item}')
    return 2

def print_volumes(item, indent):
    if isinstance(item, (Edk2Image, Edk2Volume)):
        return print_all(item, indent)
    return 0

def print_modules(item, indent):
    if isinstance(item, (Edk2Image, Edk2Volume)):
        return print_all(item, indent)
    if isinstance(item, Edk2FfsFile) and item.secname is not None:
        name = ucs16.from_ucs16(item.secname.blob, 0)
        print(f'{"":{indent}s}ffsfile size=0x{item.tlen:x} type={item.fmt_type()} name={name}')
        return 2
    return 0

def print_ovmf_meta(item, indent):
    if isinstance(item, (Edk2Image, OvmfResetVector, OvmfGuidListEntry, OvmfMemoryRange)):
        return print_all(item, indent)
    return 0

def print_tree(item, pfunc, indent = 0):
    inc = pfunc(item, indent)
    if isinstance(item, collections.UserList):
        for i in list(item):
            print_tree(i, pfunc, indent + inc)


########################################################################
# main

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', dest = 'input', type = 'string',
                      help = 'dump firmware volume FILE', metavar = 'FILE')
    parser.add_option('--all', dest = 'fmt',
                      action = 'store_const', const = 'all',
                      help = 'print everything (default)')
    parser.add_option('--volumes', dest = 'fmt',
                      action = 'store_const', const = 'volumes',
                      help = 'print firmware volumes')
    parser.add_option('--modules', dest = 'fmt',
                      action = 'store_const', const = 'modules',
                      help = 'print included modules')
    parser.add_option('--ovmf-meta', dest = 'fmt',
                      action = 'store_const', const = 'ovmf-meta',
                      help = 'print included modules')
    (options, args) = parser.parse_args()

    if not options.input:
        print('ERROR: no input file specified (try -h for help)')
        sys.exit(1)

    with open(options.input, 'rb') as f:
        data = f.read()
    image = Edk2Image(options.input, data)

    if options.fmt == 'all' or options.fmt is None:
        print_tree(image, print_all)
    elif options.fmt == 'volumes':
        print_tree(image, print_volumes)
    elif options.fmt == 'modules':
        print_tree(image, print_modules)
    elif options.fmt == 'ovmf-meta':
        print_tree(image, print_ovmf_meta)

if __name__ == '__main__':
    sys.exit(main())
