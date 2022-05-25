
import io
from construct import this, EnumIntegerString, Default, CString, Check, Select, Const, Container, Struct, Int16ul, PaddedString, Int32ul, Int8ul, Padding, Array, Bytes, Padded, Hex, BitStruct, Bit, Optional, Adapter, ValidationError, Checksum, RawCopy, Flag, Enum, FlagsEnum

from zlib import crc32

import json

class FixedString(Adapter):
    def _decode(self, obj, context, path):
        try:
            return str(obj, 'ascii').rstrip('\0')
        except UnicodeDecodeError:
            return None

    def _encode(self, obj: str, context, path):
        return obj.encode('ascii', errors='strict')

class MacAddressList(Adapter):
    nulladdr = b'\0\0\0\0\0\0'

    def __init__(self, length):
        self.length = length
        super().__init__(Array(length, Padded(8, Bytes(6))))

    @classmethod
    def decodeitem(cls, mac):
        if len(mac) != 6:
            raise ValueError('MAC Address is not correct length', mac)
        return ':'.join('{:02x}'.format(x) for x in mac)

    @classmethod
    def encodeitem(cls, mac):
        if mac is None:
            return bytes(6)
        else:
            b = mac.replace('-',':')
            b = b.split(':')
            if len(b) == 6:
                return bytes.fromhex(''.join(b))
            else:
                if len(b[0] == 12):
                    return b
                else:
                    raise ValueError('MAC Address is not correct length', mac)

    def _decode(self, obj, context, path):
        return [self.decodeitem(i) for i in obj if i != self.nulladdr]

    def _encode(self, obj, context, path):
        pad = self.length - len(obj)
        return [self.encodeitem(i) for i in obj] + [bytes(6)] * pad


class FlashLayoutAdapter(Adapter):
    def __init__(self):
      super().__init__(
        Array(10, Padded(36,
            Struct(
                "Type" / Enum(Int32ul,
                              NONE=0x00,
                              HWCONFIG=0x01,
                              FDL=0x02,
                              FW=0x03,
                              FW_CONT=0x04,
                              CONFIG=0x05,
                              REMANENT=0x06,
                              MANAGEMENT=0x07,
                              APP_CONT=0x08,
                              MFW=0x09,
                              FILESYSTEM=0x0A,
                              FWUPDATE=0x0B,
                              MFW_HWCONFIG=0x0C,
                              APP=0x0D),
                "Start" / Int32ul,
                "Size" / Int32ul,
                "Chip" / Enum(Int32ul,
                              INTFLASH0=0,
                              INTFLASH1=1,
                              EXTERNAL=2),
                "Name" / Padded(16, CString('ascii')),
                "Access" / Enum(Int8ul, O_RDONLY=0, O_RDWR=2),
                Padding(3),
              )
          ))
        )

    def _decode(self, obj, context, path):
        return [i for i in obj if i is not None]

    def _encode(self, obj, context, path):
        pad=10 - len(obj)
        return obj + [None] * pad


class ChipTableAdapter(Adapter):
    def __init__(self):
        super().__init__(
          Array(4,
            Padded(32,
              Optional(
                  Struct(
                      "Chip" / Enum(Int32ul,
                                  INTFLASH0=0,
                                  INTFLASH1=1,
                                  EXTERNAL=2),
                      "Driver" / Padded(16, CString('ascii')),
                      "Block" / Int32ul,
                      "Size" / Int32ul,
                      "Cycles" / Int32ul,
                      Check(this['Size'] > 0)
                  )
                )
              )
            )
          )

    def _decode(self, obj, context, path):
        return [i for i in obj if i is not None]

    def _encode(self, obj, context, path):
        pad = 4 - len(obj)
        return obj + [None] * pad

class ProductionDate(Adapter):
    def _decode(self, obj, context, path):
        year=(obj >> 8 & 0xff) + 2000
        week=(obj & 0xff)
        return '{}-W{}'.format(year, week)

    def _encode(self, obj, context, path):
        year, week=obj.split('-W', 2)
        year=int(year)
        week=int(week)
        code=((year - 2000) << 8) + (week & 0xff)
        return code

def _postprocess(obj):
    if isinstance(obj, Container):
        return {k.__str__(): _postprocess(v) for k, v in obj.items() if k[0] != '_'}
    elif isinstance(obj, list):
         return [_postprocess(i) for i in obj]
    elif isinstance(obj, EnumIntegerString):
        return str.__repr__(obj).strip('\'')
    else:
        return obj


class FlashDeviceLabel:
    struct=Struct(
        Const(b'ProductData>'),
        "Label Size" / Int16ul,
        "Content Size" / Int16ul,
        "Contents" / RawCopy(
            Struct(
                "Device" / Struct(
                    "Manufacturer" / Int16ul,
                    "Class" /
                        Enum(Int16ul, NETX90=0x3C, NETX90_SDRAM=0x45),
                    "Device Number" / Int32ul,
                    "Serial Number" / Int32ul,
                    "Hardware Compatibility" / Int8ul,
                    "Hardware Revision" / Int8ul,
                    "Production Date" / ProductionDate(Int16ul),
                    Padding(16)
                ),
                "MAC Addresses" / MacAddressList(8),
                "APP MAC Addresses" / MacAddressList(4),
                Padding(2),  # USB ID is not used on netX90
                Padding(2),
                Padding(16),
                Padding(16),
                Padding(76),
                "OEM Identification" / Struct(
                    "Options" / FlagsEnum(Int32ul, SerialNumber=1, OrderNumber=2, HWRevision=3, ProductionDate=4),
                    "Serial Number" / Padded(28, CString('ascii')),
                    "Order Number" / Padded(32, CString('ascii')),
                    "Hardware Revision" / Padded(16, CString('ascii')),
                    "Production Date" / Padded(32, CString('ascii')),
                    Padding(12),  # Reserved
                    "Custom Data" / Default(Bytes(112), bytes(112))
                ),
                "Flash Layout" / FlashLayoutAdapter(),
                "Chip Table" / ChipTableAdapter()
            )
        ),
        "CRC" / Checksum(Int32ul, crc32, this.Contents.data),
        Const(b'<ProductData')
    )

    def __init__(self, struct):
        self.label=struct

    @classmethod
    def frombin(cls, src):
        if isinstance(src, io.IOBase):
            return cls(_postprocess(cls.struct.parse_stream(src).Contents.value))
        else:
            return cls(_postprocess(cls.struct.parse(src).Contents.value))

    @classmethod
    def fromdict(cls, d):
        return cls(d)

    def tobin(self):
        return self.struct.build(
            {
                'Label Size': self.struct.sizeof(),
                'Content Size': self.struct.Contents.sizeof(),
                'Contents': {'value': self.label}
            }
        )

    def todict(self):
        return self.label

    def __repr__(self):
        return str(json.dumps(self.label))

    def __str__(self):
        return str(json.dumps(self.label, indent=4))
