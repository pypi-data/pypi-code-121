#!/usr/bin/python
""" aws varstore parser """
import sys
import zlib
import base64
import struct
import logging

from pkg_resources import resource_filename

from virt.firmware.efi import guids
from virt.firmware.efi import ucs16
from virt.firmware.efi import efivar

# pylint: disable=ungrouped-imports
try:
    from crc32c import crc32c
except ModuleNotFoundError:
    from virt.firmware.misc import crc32c

zdict_v0_file = resource_filename('virt.firmware', 'aws/dict.v0')
zdict_v0_blob = None

# pylint: disable=global-statement
def zdict_v0():
    global zdict_v0_blob
    if zdict_v0_blob is None:
        with open(zdict_v0_file, "rb") as f:
            zdict_v0_blob = f.read()
    return zdict_v0_blob


class AwsVarStore:
    """  class for aws efi varstore """

    MAGIC = 0x494645554e5a4d41

    def __init__(self, filename = None):
        self.filename = filename
        self.filedata = b''
        self.vardata  = b''
        self.varpos   = 0

        if self.filename:
            self.readfile()
            self.parse()

    @staticmethod
    def probe(filename):
        with open(filename, "rb") as f:
            try:
                data = base64.b64decode(f.read())
            except base64.binascii.Error:
                return False
        (magic, crc32, version) = struct.unpack_from("=QLL", data, 0)
        if magic != AwsVarStore.MAGIC:
            return False
        return True

    def readfile(self):
        logging.info('reading aws varstore from %s', self.filename)
        with open(self.filename, "rb") as f:
            self.filedata = base64.b64decode(f.read())

    def parse(self):
        (magic, crc32, version) = struct.unpack_from("=QLL", self.filedata, 0)
        logging.debug('magic=0x%x crc32=0x%x version=%d',
                      magic, crc32, version)
        if magic != self.MAGIC:
            logging.error('%s: aws magic mismatch', self.filename)
            sys.exit(1)
        if crc32c(self.filedata[ 12 : ]) != crc32:
            logging.error('%s: crc32c mismatch', self.filename)
            sys.exit(1)
        if version != 0:
            logging.error('%s: unknnown version', self.filename)
            sys.exit(1)

        decompressor = zlib.decompressobj(0, zdict = zdict_v0())
        self.vardata = decompressor.decompress(self.filedata[ 16 : ])

    def get_int(self, bits):
        s = int(bits / 8)
        d = self.vardata [ self.varpos : self.varpos + s ]
        i = int.from_bytes(d, byteorder='little', signed=False)
        self.varpos += s
        return i

    def get_blob(self):
        size = self.get_int(64)
        blob = self.vardata [ self.varpos : self.varpos + size ]
        self.varpos += size
        return blob

    def get_guid(self):
        guid = guids.parse_bin(self.vardata, self.varpos)
        self.varpos += 16
        return guid

    def get_time(self):
        blob = self.vardata [ self.varpos : self.varpos + 16 ]
        self.varpos += 16
        return blob

    # pylint: disable=W0511
    def get_varlist(self):
        self.varpos = 0
        count = self.get_int(64)
        varlist = efivar.EfiVarList()
        for index in range(count):
            name = self.get_blob()
            data = self.get_blob()
            guid = self.get_guid()
            attr = self.get_int(32)
            var = efivar.EfiVar(ucs16.from_string(name.decode('utf-8')),
                                guid = guid, attr = attr, data = data)
            if attr & efivar.EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS:
                timestamp = self.get_time()
                var.parse_time(timestamp, 0)
                digest    = self.get_blob() # FIXME
            varlist[str(var.name)] = var
        return varlist

    # pylint: disable=W0511
    @staticmethod
    def bytes_var(var):
        name = str(var.name).encode('utf-8')
        blob = struct.pack("=Q", len(name))
        blob += name
        blob += struct.pack("=Q", len(var.data))
        blob += var.data
        blob += var.guid.bytes_le
        blob += struct.pack("=L", var.attr)
        if var.attr & efivar.EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS:
            blob += var.bytes_time()
            blob += struct.pack("=Q", 0)  # FIXME: empty digest
        return blob

    @staticmethod
    def bytes_varlist(varlist):
        blob = struct.pack("=Q", len(varlist))
        for (key, item) in varlist.items():
            blob += AwsVarStore.bytes_var(item)
        return blob

    @staticmethod
    def base64_varstore(varlist):
        encoder = zlib.compressobj(9, zdict = zdict_v0())
        zblob = struct.pack("=L", 0)  # version
        zblob += encoder.compress(AwsVarStore.bytes_varlist(varlist))
        zblob += encoder.flush()
        hdr = struct.pack("=QL", AwsVarStore.MAGIC, crc32c(zblob))
        return base64.b64encode(hdr + zblob)

    @staticmethod
    def write_varstore(filename, varlist):
        logging.info('writing aws varstore to %s', filename)

        with open(filename, "wb") as f:
            f.write(AwsVarStore.base64_varstore(varlist))

if __name__ == "__main__":
    logging.basicConfig(format = '%(levelname)s: %(message)s',
                        level = logging.DEBUG)

    testfile = "tests/data/secboot.aws"
    if AwsVarStore.probe(testfile):
        awsstore = AwsVarStore(testfile)
        vl = awsstore.get_varlist()
        vl.print_normal()
