"""Service to parse backtraces in mongo log files."""
from json import JSONDecodeError, JSONDecoder
from typing import Any, Dict, List, NamedTuple, Optional

import inject

BACKTRACE_KEY = "backtrace"
PROCESS_INFO_KEY = "processInfo"

SOMAP_KEY = "somap"
MONGODB_VERSION_KEY = "mongodbVersion"

BINARY_LOAD_ADDRESS_KEY = "b"
ELF_TYPE_KEY = "elfType"
BUILD_ID_KEY = "buildId"
VMADDR_KEY = "vmaddr"


class SoInfo(NamedTuple):
    """Information about process that printed backtrace."""

    elf_type: Optional[int] = None
    vmaddr: Optional[str] = None
    build_id: Optional[str] = None
    mongodb_version: Optional[str] = None


class TraceDoc(NamedTuple):
    """
    Document with backtrace related information.

    * backtrace: Backtrace doc printed out by mongo process.
    * base_addr_map: Map from binary load address to description of library.
    """

    backtrace: List[Dict[str, Any]]
    base_addr_map: Dict[str, SoInfo]


class MongoLogParserService:
    """Service to parse backtraces in mongo log files."""

    @inject.autoparams()
    def __init__(self, json_decoder: JSONDecoder):
        """
        Initialize.

        :param json_decoder: JSONDecoder object.
        """
        self.json_decoder = json_decoder

    def parse_log_lines(
        self, log_lines: str, base_addr_map: Optional[Dict[str, SoInfo]] = None
    ) -> List[TraceDoc]:
        """
        Analyze log lines and return all backtraces found.

        :param log_lines: Log lines as string.
        :param base_addr_map: Map from binary load address to description of library.
        :return: List of trace docs.
        """
        global_base_addr_map = base_addr_map if base_addr_map is not None else {}
        backtraces_list = []

        for line in log_lines.splitlines():
            log_json = self.decode_log(line)
            if log_json is None:
                continue

            process_info = self.get_value_recursively(log_json, PROCESS_INFO_KEY)
            if process_info is not None:
                process_base_addr_map = self.make_base_addr_map(process_info)
                global_base_addr_map.update(process_base_addr_map)

            backtrace = self.get_value_recursively(log_json, BACKTRACE_KEY)
            if backtrace is not None:
                backtraces_list.append(backtrace)

        return [TraceDoc(backtrace, global_base_addr_map) for backtrace in backtraces_list]

    def decode_log(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Decode JSON doc from log string.

        :param line: Log string.
        :return: Decoded log line or None.
        """
        start_index = line.find("{")
        if start_index == -1:
            return None

        # Skip over everything before the first '{' since it is likely to be log line prefixes.
        sub_line = line[start_index:]
        try:
            # Using raw_decode() to ignore extra data after the closing '}' to allow maximal
            # sloppiness in copy-pasting input.
            return self.json_decoder.raw_decode(sub_line)[0]

        except JSONDecodeError:
            # It is expected that any kind of logs may be passed in along with a backtrace,
            # we are skipping the lines that do not contain a valid JSON document
            return None

    def get_value_recursively(self, doc: Any, key: str) -> Optional[Any]:
        """
        Search the dict recursively for a value that has the key.

        :param doc: Dict or any value to search in.
        :param key: Key to search for.
        :return: Value of the key or None.
        """
        try:
            if key in doc.keys():
                return doc[key]
            for sub_doc in doc.values():
                res = self.get_value_recursively(sub_doc, key)
                if res:
                    return res
        except AttributeError:
            pass
        return None

    @staticmethod
    def make_base_addr_map(process_info: Dict[str, Any]) -> Dict[str, SoInfo]:
        """
        Make map from binary load address to description of library from the processInfo.

        :param process_info: Backtrace processInfo.
        :return: Map from binary load address to description of library.
        """
        addr_map = {}
        mongodb_version = process_info.get(MONGODB_VERSION_KEY)
        so_map_list = process_info.get(SOMAP_KEY, [])

        for so_entry in so_map_list:
            if BINARY_LOAD_ADDRESS_KEY in so_entry:
                addr_map[so_entry[BINARY_LOAD_ADDRESS_KEY]] = SoInfo(
                    elf_type=so_entry.get(ELF_TYPE_KEY),
                    vmaddr=so_entry.get(VMADDR_KEY),
                    build_id=so_entry.get(BUILD_ID_KEY),
                    mongodb_version=mongodb_version,
                )

        return addr_map
