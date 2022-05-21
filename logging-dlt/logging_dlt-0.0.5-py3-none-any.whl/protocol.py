""" module:: dlt.protocol
    :synopsis: A pythonic representation of "diagnostic log and trace" protocol.
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: CC-BY-NC
"""
import struct
from collections import OrderedDict
from datetime import datetime
from enum import IntEnum, IntFlag

# Note: The difference in handling is, DLT has a storage header of 12 Bytes,
#       DLS does not, and thus no ECUID and no Timestamp
from typing import Tuple, Optional, Union

import logging

LOGGER = logging.getLogger(__name__)

DLT_MAGIC_FILE = b"DLT\x01"
DLT_MAGIC_SERIAL = b"DLS\x01"

DEFAULT_DLT_PORT = 3490


class DltHeaderBit(IntFlag):
    USE_EXTENDED_HEADER = 1
    MSB_FIRST = 2
    WITH_ECU_ID = 4
    WITH_SESSION_ID = 8
    WITH_TIMESTAMP = 16


class DltRecordType(IntEnum):
    LOG = 0
    APP_TRACE = 1
    NW_TRACE = 2
    CONTROL = 3


class DltControlType(IntEnum):
    REQUEST = 1
    RESPONSE = 2
    TIME = 3


class DltTraceType(IntEnum):
    VARIABLE = 1
    FUNCTION_INPUT = 2
    FUNCTION_OUTPUT = 3
    STATE = 4
    VIRTUAL_FUNCTION_BUS = 5


class DltLogLevel(IntEnum):
    FATAL = 1
    ERROR = 2
    WARN = 3
    INFO = 4
    DEBUG = 5
    VERBOSE = 6


class DltService(IntEnum):
    SET_LOG_LEVEL = 1
    SET_TRACE_STATUS = 2
    GET_LOG_INFO = 3
    GET_DEFAULT_LOG_LEVEL = 4
    STORE_CONFIG = 5
    RESET_TO_FACTORY_DEFAULT = 6
    SET_COM_INTERFACE_STATUS = 7
    SET_COM_INTERFACE_MAX_BANDWIDTH = 8
    SET_VERBOSE_MODE = 9
    SET_record_FILTERING = 10
    SET_TIMING_PACKETS = 11
    GET_LOCAL_TIME = 12
    USE_ECU_ID = 13
    USE_SESSION_ID = 14,
    USE_TIMESTAMP = 15
    USE_EXTENDED_HEADER = 16
    SET_DEFAULT_LOG_LEVEL = 17
    SET_DEFAULT_TRACE_STATUS = 18
    GET_SOFTWARE_VERSION = 19
    record_BUFFER_OVERFLOW = 20


class DltPayloadType(IntEnum):
    """
    Note: This enum represents the first 4 bytes of the payload, shifted 4 bits right.
          The original enum in
          `Genivi C-Code <https://github.com/COVESA/dlt-daemon/blob/master/include/dlt/dlt_protocol.h#L149>`_
          is unclean. It mixes flags and ENUM in these defines, so incompatible matches can happen there.

    Note2: The encoding is not used by this module because python does this automatically. It also shows how
           wicked this bitfield is used for arbitrary things.
           `#define DLT_TYPE_INFO_SCOD 0x00038000 /**< coding of the type string: 0 = ASCII, 1 = UTF-8 */`
    """
    BOOL = 1
    SIGNED_INT = 2
    UNSIGNED_INT = 4
    FLOAT = 8
    ARRAY = 0x10
    STRING = 0x20
    RAW = 0x40


def generate_storage_header(ecuid: str,
                            timestamp: datetime = datetime.now()):
    """
    Generate a dlt storage header
    A Storage header is a 12bytes entry in front of regular header.
    It contains absolute timestamp of reception and the ecu short name.
    Note: It is only used for test data generation in this project.

    :param ecuid: The Ecu Id, a short name with 4 characters max.
    :param timestamp: The timestamp of reception.
    :return: The storage header as bytes.
    """
    ts = timestamp.timestamp()
    second = int(ts)
    microsecond = round((ts - second) * 10 ** 6)
    return struct.pack("II4s", second, microsecond, ecuid.encode().ljust(4))


def parse_storage_header(data: bytes) -> dict:
    """
    Parse a dlt storage header.

    :param data: The data bytes.
    :return: A dictionary with timestamp and ecuid.
    """
    if len(data) < 12:
        raise DltRecordIncomplete("Expected at least 12 bytes - found {0}".format(len(data)))

    second, microsecond, ecuid = struct.unpack("II4s", data[:12])
    timestamp = datetime.fromtimestamp(second + (microsecond / 10 ** 6))
    return {"timestamp": timestamp,
            "ecuid": ecuid.decode("ascii", "ignore").strip(),
            }


def generate_standard_header(flags: DltHeaderBit,
                             record_count: int,
                             record_length: int,
                             version: int = 1):
    """
    Generate dlt standard header.

    :param flags: The header flags that indicate presence of other contents in record.
    :param record_count: The number of records that follow the header, typically just one.
    :param record_length: The length of the record which is everything in between the DLS\x01 markers.
    :param version: The protocol version which is always one.
    :return: The standard header as bytes.
    """
    return struct.pack(">BBH",
                       ((version << 5) | int(flags)),
                       record_count,
                       record_length)


def parse_standard_header(data: bytes) -> dict:
    """
    Parse a dlt standard header.

    :param data: The data bytes.
    :return: A dictionary with flags, version, record_count and record_length.
    """
    if len(data) < 4:
        raise DltRecordIncomplete("Expected at least 4 bytes - found {0}".format(len(data)))
    version_with_flags, record_count, record_length = struct.unpack(">BBH", data[:4])

    version = ((version_with_flags & 0xE0) >> 5)
    flags = DltHeaderBit(version_with_flags & 0x1F)
    if version != 1:
        raise NotImplementedError("Version {0} not handled".format(version))

    ret = {"flags": flags,
           "version": version,
           "record_count": record_count,
           "record_length": record_length,
           }

    return ret


def get_standard_header_extra_size(flags) -> int:
    """
    Get the expected size for the header extra content by inspecting the flags.

    :param flags: The header flags.
    :return: The expected size.
    """
    extra_header_content_flags = [DltHeaderBit.WITH_ECU_ID,
                                  DltHeaderBit.WITH_SESSION_ID,
                                  DltHeaderBit.WITH_TIMESTAMP]
    return sum([4 for b in extra_header_content_flags if (b & flags)])


def generate_standard_header_extra(ecuid: Optional[str] = None,
                                   sessionid: Optional[str] = None,
                                   timestamp: Optional[float] = None) -> Tuple[DltHeaderBit, bytes]:
    """
    Generate standard header extra content.

    :param ecuid: The ecuid.
    :param sessionid: The sessionid.
    :param timestamp: The timestamp.
    :return: A tuple of flags and data bytes
    """
    flags = DltHeaderBit(0)
    data = bytearray()

    if ecuid is not None:
        flags |= DltHeaderBit.WITH_ECU_ID
        data.extend(ecuid.encode().ljust(4))
    if sessionid is not None:
        flags |= DltHeaderBit.WITH_SESSION_ID
        data.extend(sessionid.encode().ljust(4))
    if timestamp is not None:
        flags |= DltHeaderBit.WITH_TIMESTAMP
        data.extend(int(timestamp * 10000).to_bytes(4, "big"))

    return flags, bytes(data)


def parse_standard_header_extra(flags: DltHeaderBit,
                                data: bytes) -> dict:
    """
    Parse the standard header extra content.

    :param flags: The header flags.
    :param data: The data bytes.
    :return: A dictionary with the contents.
    """
    expected_size = get_standard_header_extra_size(flags=flags)

    if len(data) < expected_size:
        raise DltRecordIncomplete("Expected at least {0} bytes - found {1}".format(expected_size, len(data)))

    key_dict = OrderedDict({DltHeaderBit.WITH_ECU_ID: {"key": "ecuid",
                                                       "conversion": lambda x: x.decode("ascii", "ignore").strip(),
                                                       "fmt": "4s",
                                                       },
                            DltHeaderBit.WITH_SESSION_ID: {"key": "sessionid",
                                                           "conversion": lambda x: x.decode("ascii", "ignore").strip(),
                                                           "fmt": "4s",
                                                           },
                            DltHeaderBit.WITH_TIMESTAMP: {"key": "timestamp",
                                                          "conversion": lambda x: x / 10000,
                                                          "fmt": "I",
                                                          },
                            })

    fmt = ">{0}".format("".join(val.get("fmt") for key, val in key_dict.items() if key in flags))
    funcs = [val.get("conversion") for key, val in key_dict.items() if key in flags]
    values = [func(value) for value, func in zip(struct.unpack(fmt, data[:expected_size]), funcs)]
    keys = [val.get("key") for key, val in key_dict.items() if key in flags]
    return dict(zip(keys, values))


def generate_extended_header(record_type: DltRecordType,
                             number_of_arguments: int,
                             applicationid: str,
                             contextid: str,
                             log_level: Optional[DltLogLevel] = None,
                             command: Optional[Union[DltTraceType, DltControlType]] = None,
                             verbose: bool = False,
                             ) -> bytes:
    """
    Generate the extended header.

    :param record_type: The record type.
    :param number_of_arguments: The number of arguments.
    :param applicationid: The applicationid.
    :param contextid: The contextid.
    :param log_level: The log_level. Only with DltrecordType.Log
    :param command: The command. Only with DltrecordType.Trace and Control
    :param verbose: The verbose flag.
    :return:
    """
    record_info = (record_type << 1)
    if verbose is True:
        record_info |= (1 << 0)
    if command is not None and record_type in [DltRecordType.CONTROL, DltRecordType.APP_TRACE]:
        record_info |= (command << 4)
    elif log_level is not None and record_type == DltRecordType.LOG:
        record_info |= (log_level << 4)

    return struct.pack("BB4s4s", record_info, number_of_arguments, applicationid.encode().ljust(4),
                       contextid.encode().ljust(4))


def parse_extended_header(data: bytes) -> dict:
    """
    Parse the extended header content.

    :param data: The data bytes.
    :return: A dictionary with the contents.
    """
    if len(data) < 10:
        raise DltRecordIncomplete("Expected at least 10 bytes - found {0}".format(len(data)))

    record_info, number_of_arguments, applicationid, contextid = struct.unpack("BB4s4s", data[:10])
    verbose = ((record_info & 0x1) == 1)
    record_type_raw = (record_info & 0xE) >> 1
    try:
        record_type = DltRecordType(record_type_raw)
    except ValueError:
        raise DltRecordInvalid("No matching record type for {0}".format(record_type_raw))
    record_sub_type_raw = (record_info & 0xF0) >> 4

    command = None
    log_level = None
    try:
        if record_type == DltRecordType.APP_TRACE:
            command = DltTraceType(record_sub_type_raw)
        elif record_type == DltRecordType.CONTROL:
            command = DltControlType(record_sub_type_raw)
        elif record_type == DltRecordType.LOG:
            log_level = DltLogLevel(record_sub_type_raw)
    except ValueError:
        raise DltRecordInvalid("No matching subtype for {0} ({1})".format(record_sub_type_raw, record_type.name))

    return {"record_type": record_type,
            "command": command,
            "log_level": log_level,
            "verbose": verbose,
            "number_of_arguments": number_of_arguments,
            "applicationid": applicationid.decode("ascii", "ignore").strip(),
            "contextid": contextid.decode("ascii", "ignore").strip()
            }


def generate_payload(payload_type: DltPayloadType,
                     payload_text: str,
                     endianess: str = "little",
                     ) -> Tuple[DltRecordType, bool, bytes]:
    if endianess == "little":
        msb_first = False
    elif endianess == "big":
        msb_first = True
    else:
        raise ValueError("{0} is not an endianess".format(endianess))

    data = bytearray()
    if isinstance(payload_type, DltPayloadType) and payload_type == DltPayloadType.STRING:
        record_type = DltRecordType.LOG
        data.extend((payload_type << 4).to_bytes(4, endianess))
        payload_data = payload_text.encode("ASCII")
        data.extend(len(payload_data).to_bytes(2, endianess))
        data.extend(payload_data)
    else:
        raise NotImplementedError("Concatenating {0} is not implemented yet".format(payload_type.name))

    return record_type, msb_first, data


def parse_payload(record_type: DltRecordType,
                  msb_first: bool,
                  data: bytes,
                  ) -> dict:
    """
    Parse the payload of the record.

    Note: Meet the first inconsistency of this protocol. Extended header has to provide the record_type
          or this whole function is incapable to handle different payload types. But Extended Header could
          be omitted by protocol (see extra header), so this house of cards collapses instantly.

    :param record_type: The record type.
    :param msb_first: The endianess flag.
    :param data: The data.
    :return: A dictionary with payload_type and payload_text for now.
    """
    if msb_first:
        endianess = "big"
    else:
        endianess = "little"
    expected_size = int.from_bytes(data[4:6], endianess)+6

    if len(data) < expected_size:
        raise DltRecordIncomplete("Expected at least {0} bytes - found {1}".format(expected_size, len(data)))
    if record_type is None:
        # A record without a Extended Header
        raise NotImplementedError("No record_type given for payload {0}".format(data[:expected_size]))

    if record_type == DltRecordType.LOG:
        # Note: the >> 4 is done to align the payload types, see class definition for details
        payload_type_raw = (int.from_bytes(data[:4], endianess) & 0x7FFF) >> 4
        try:
            payload_type = DltPayloadType(payload_type_raw)
        except ValueError:
            raise DltRecordInvalid("No matching DltPayloadType for {0}".format(payload_type_raw))
        if payload_type == DltPayloadType.STRING:
            # Note: Most implementations violate ASCII and UTF encodings and use CP1252 instead,
            #       Python recognizes this while original Genivi Implementation fails to do so.
            #       It is also necessary to strip() all annoying tabs, newlines and null bytes.
            payload_text = data[6:expected_size].decode("ascii", "ignore").strip()
        else:
            raise NotImplementedError("Extracting {0} is not implemented yet".format(payload_type.name))
    else:
        raise NotImplementedError("Extracting {0} is not implemented yet".format(record_type.name))

    return {"payload_type": payload_type,
            "payload_text": payload_text}


def parse_dlt_record(data: bytes) -> dict:
    """
    Parse a complete dlt record.
    Value Errors are raised by underlying parser functions if not complete.

    :param data: The data bytes.
    :return: A combined dictionary with all contents.
    """
    stdhdr_size = 4
    stdhdr = parse_standard_header(data=data[:stdhdr_size])
    expected_size = stdhdr.get("record_length")
    if len(data) < expected_size:
        raise DltRecordIncomplete("Expected at least {0} bytes - found {1}".format(expected_size, len(data)))
    ret = {}
    ret.update(stdhdr)
    flags = stdhdr.get("flags")
    msb_first = (DltHeaderBit.MSB_FIRST in flags)
    sdthdrxtra_size = get_standard_header_extra_size(flags=flags)
    stdhdrxtra = parse_standard_header_extra(flags=flags, data=data[stdhdr_size:stdhdr_size + sdthdrxtra_size])
    ret.update(stdhdrxtra)
    exthdr_size = 0
    record_type = None
    if flags & DltHeaderBit.USE_EXTENDED_HEADER:
        exthdr_size = 10
        exthdr = parse_extended_header(
            data=data[stdhdr_size + sdthdrxtra_size:stdhdr_size + sdthdrxtra_size + exthdr_size])
        ret.update(exthdr)
        record_type = exthdr.get("record_type")

    payload = parse_payload(record_type=record_type,
                            msb_first=msb_first,
                            data=data[stdhdr_size + sdthdrxtra_size + exthdr_size:])
    ret.update(payload)
    return ret


def generate_dlt_log_record(
        payload_text: str,
        ecuid: str,
        sessionid: str,
        timestamp: float,
        applicationid: str,
        contextid: str,
        log_level: DltLogLevel = DltLogLevel.INFO,
        verbose: bool = False,
        endianess: str = "little") -> bytes:
    """
    This function generates a LOG type dlt record.
    It is for testing purposes only.

    :param payload_text: The log text.
    :param ecuid: The ecuid.
    :param sessionid: The sessionid.
    :param timestamp: The timestamp.
    :param applicationid: The applicationid.
    :param contextid: The contextid.
    :param log_level: The log_level.
    :param verbose: The verbose flag.
    :param endianess: The endianess.
    :return: The dlt record bytes.
    """

    data = bytearray()
    payload_type = DltPayloadType.STRING
    record_type, msb_first, payload = generate_payload(payload_type=payload_type,
                                                       payload_text=payload_text,
                                                       endianess=endianess)
    flags = DltHeaderBit(0)
    if msb_first:
        flags |= DltHeaderBit.MSB_FIRST

    number_of_arguments = 1
    extended_header = generate_extended_header(record_type=record_type,
                                               applicationid=applicationid,
                                               contextid=contextid,
                                               log_level=log_level,
                                               verbose=verbose,
                                               number_of_arguments=number_of_arguments,
                                               )
    flags |= DltHeaderBit.USE_EXTENDED_HEADER

    extra_flags, standard_header_extra = generate_standard_header_extra(ecuid=ecuid,
                                                                        sessionid=sessionid,
                                                                        timestamp=timestamp)

    flags |= extra_flags
    standard_header = generate_standard_header(flags=flags,
                                               record_count=1,
                                               record_length=len(payload) + len(extended_header) + len(
                                                   standard_header_extra) + 4
                                               )
    data.extend(standard_header)
    data.extend(standard_header_extra)
    data.extend(extended_header)
    data.extend(payload)
    return bytes(data)


class DltParserException(Exception):
    pass


class DltRecordIncomplete(DltParserException):
    pass


class DltRecordInvalid(DltParserException):
    pass
