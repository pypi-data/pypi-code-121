"""Parsers for Vector Product Format (VPF) artifacts conforming to MIL-STD-2407."""
from itertools import takewhile
from typing import Any, Dict, Generator, Tuple, Union, no_type_check

EMPTY_FIELD_PLACEHOLDER = '-'
VAR_LENGTH_INDICATOR = '*'
VAR_LENGTH = 9876543210


class ByteOrder:
    """Type to mix in VPF specific byte order detection."""

    byte_orders = ('big', 'little')
    big_endian = 'M'
    bo_indicators = {
        'L': 'little',
        big_endian: 'big',
    }
    bo_keys = tuple(bo_indicators.keys())
    bo_indicator_index = 4
    head_off_expl = bo_indicator_index + 1  # Index of first header byte with byte order info present

    @classmethod
    @no_type_check
    def detect(cls, seq) -> Tuple[str, bool, int]:
        """Detect the endianness of the artifact and return byte order, declaration method, and next offset."""
        byte_order_explicit = True if chr(seq[cls.bo_indicator_index]) in cls.bo_keys else False
        order_indicator = chr(seq[cls.bo_indicator_index]) if byte_order_explicit else cls.bo_keys[0]
        byte_order = cls.byte_orders[0] if order_indicator == cls.big_endian else cls.byte_orders[1]
        header_byte_offset = cls.head_off_expl if byte_order_explicit else cls.head_off_expl - 1
        return byte_order, byte_order_explicit, header_byte_offset


class HeaderLength:
    """Type to mix in VPF specific extraction of header length in bytes."""

    header_length_range = slice(0, 4)

    @classmethod
    @no_type_check
    def extract(cls, byte_order: str, seq) -> int:
        """Extract the length of the header for the artifact as encoded in the length field matching endianness."""
        return int.from_bytes(seq[cls.header_length_range], byteorder=byte_order)  # noqa


@no_type_check
class Table:
    """Type to parse a VPF table like artifact - eg. a Database Header Table (dht)."""

    semi_chr = ';'
    key_types = {
        'P': 'Primary key',
        'U': 'Unique key',
        'N': 'Non-unique key',
    }
    table: Dict[str, Union[int, object, str]] = {}
    ERROR = -1

    @no_type_check
    def __init__(self, label: str, byte_stream: Generator[bytes, Any, None]) -> None:
        """Parse the table data from the stream of bytes."""
        self.label = label
        self._seq = list(byte_stream)  # Eager consumption of the stream (for now)

        self.bootstrap_table()

        next_segment_start = self.parse_table_description(self.table['header_byte_offset'] + 1)
        if next_segment_start == self.ERROR:
            return

        next_segment_start = self.parse_narrative_table_name(next_segment_start)
        if next_segment_start == self.ERROR:
            return

        self.table['columns'] = {}
        _ = self.parse_columns(next_segment_start)  # hand over ... an start of next segment or self.ERROR
        return

    @no_type_check
    def bootstrap_table(self) -> None:
        """Detect byte order (endianness) from and determine header length of artifact."""
        byte_order, byte_order_explicit, header_byte_offset = ByteOrder.detect(self._seq)
        self.table = {
            'error': False,
            'error_detail': '',
            'byte_order': byte_order,
            'byte_order_explicit': byte_order_explicit,
            'header_length': HeaderLength.extract(byte_order, self._seq),
            'header_byte_offset': header_byte_offset,
        }

    @no_type_check
    def parse_table_description(self, next_segment_start: int) -> int:
        """Parse the name of the table description and return next segment start offset."""
        rem_seq = self._seq[next_segment_start:]
        try:
            table_description = ''.join(chr(c) for c in takewhile(lambda x: chr(x) != self.semi_chr, rem_seq))
            self.table['table_description'] = table_description
            if not table_description:
                raise ValueError('empty field or failed delimiter detection')
        except ValueError as err:
            self.table['error'] = True
            self.table['error_detail'] = f'failing to parse table description with {err}'
            return self.ERROR

        return self.table['header_byte_offset'] + 1 + len(table_description) + 1

    @no_type_check
    def parse_narrative_table_name(self, next_segment_start: int) -> int:
        """Parse the name of the narrative table and return next segment start offset."""
        rem_seq = self._seq[next_segment_start:]
        try:
            narrative_table_name = ''.join(chr(c) for c in takewhile(lambda x: chr(x) != self.semi_chr, rem_seq))
            self.table['narrative_table_name'] = narrative_table_name
        except ValueError as err:
            self.table['error'] = True
            self.table['error_detail'] = f'failing to parse narrative table name with {err}'
            return self.ERROR

        return next_segment_start + len(narrative_table_name) + 1

    @no_type_check
    def parse_columns(self, next_segment_start: int) -> int:
        """Parse all available column specs and return next segment start offset."""
        eq_chr = '='
        comma_chr = ','
        colon_chr = ':'
        col_rank = 0
        rem_seq = self._seq[next_segment_start:]
        while rem_seq and chr(rem_seq[0]) != self.semi_chr:  # noqa
            col_rank += 1
            column_spec = ''.join(chr(c) for c in takewhile(lambda x: chr(x) != colon_chr, rem_seq))
            try:
                col_name, spec = column_spec.split(eq_chr, 1)
            except ValueError as err:
                self.table['error'] = True
                self.table['error_detail'] = f'failing to parse column with {err}'
                return self.ERROR

            try:
                (
                    field_type,
                    field_length,
                    key_type,
                    column_textual_description,
                    optional_value_description_table_name,
                    optional_thematic_index_name,
                    optional_column_narrative_table_name,
                ) = spec.rstrip(comma_chr).split(comma_chr)
                self.table['columns'][col_name] = {
                    'column_rank': col_rank,
                    'column_name': col_name,
                    'field_type': field_type,
                    'field_length': int(field_length) if field_length != VAR_LENGTH_INDICATOR else VAR_LENGTH,
                    'key_type': key_type,
                    'column_textual_description': column_textual_description,
                    'optional_value_description_table_name': optional_value_description_table_name,
                    'optional_thematic_index_name': optional_thematic_index_name,
                    'optional_column_narrative_table_name': optional_column_narrative_table_name,
                }
            except ValueError as err:
                self.table['error'] = True
                self.table['error_detail'] = f'failing to parse {col_name} column spec with {err}'
                return self.ERROR
            that_key_type = self.table['columns'][col_name]['key_type']
            if that_key_type not in self.key_types:
                self.table['error'] = True
                self.table[
                    'error_detail'
                ] = f'key type error in {col_name} column spec with unknown code {that_key_type}'
                return self.ERROR

            next_segment_start += len(column_spec) + 1
            rem_seq = self._seq[next_segment_start:]

        return next_segment_start
