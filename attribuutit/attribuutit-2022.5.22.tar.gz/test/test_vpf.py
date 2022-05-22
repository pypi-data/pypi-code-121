import pathlib

import attribuutit.vpf as vpf

VPF_ROOT = pathlib.Path('local', 'incoming')


def test_table_header_length_detection():
    label = 'header-5-bytes'
    expectation = {
        'error': True,
        'error_detail': 'failing to parse table description with empty field or failed delimiter detection',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 886,
        'header_byte_offset': 5,
        'table_description': '',
    }
    with open(VPF_ROOT / 'head' / '5-bytes' / 'dht', 'rb') as source:
        dht = vpf.Table(label, (b for b in source.read(5)))
        assert dht.table == expectation


def test_table_name_and_first_column_detection():
    label = 'header-61-bytes'
    expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 886,
        'header_byte_offset': 5,
        'table_description': 'Database Header Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
        'columns': {
            'id': {
                'column_rank': 1,
                'column_name': 'id',
                'field_type': 'I',
                'field_length': 1,
                'key_type': 'P',
                'column_textual_description': 'Row Identifier',
                'optional_value_description_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
                'optional_thematic_index_name': vpf.EMPTY_FIELD_PLACEHOLDER,
                'optional_column_narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
            }
        },
    }
    with open(VPF_ROOT / 'head' / '61-bytes' / 'dht', 'rb') as source:
        dht = vpf.Table(label, (b for b in source.read(61)))
        assert dht.table == expectation


def test_table_database_header_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 886,
        'header_byte_offset': 5,
        'table_description': 'Database Header Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'vpf_version',
            'database_name',
            'database_desc',
            'media_standard',
            'originator',
            'addressee',
            'media_volumes',
            'seq_numbers',
            'num_data_sets',
            'security_class',
            'downgrading',
            'downgrade_date',
            'releasability',
            'transmittal_id',
            'edition_number',
            'edition_date',
        )
    )
    index_column_data_expected = {
        'column_rank': 1,
        'column_name': 'id',
        'field_type': 'I',
        'field_length': 1,
        'key_type': 'P',
        'column_textual_description': 'Row Identifier',
        'optional_value_description_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
        'optional_thematic_index_name': vpf.EMPTY_FIELD_PLACEHOLDER,
        'optional_column_narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    with open(VPF_ROOT / 'scenario' / '42' / 'dht', 'rb') as source:
        dht = vpf.Table(label, source.read(890))
        for key, value in base_expectation.items():
            assert dht.table[key] == value
        assert sorted(dht.table['columns']) == column_names_expected
        assert dht.table['columns']['id'] == index_column_data_expected


def test_table_library_attribute_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 268,
        'header_byte_offset': 5,
        'table_description': 'Library Attribute (Extent) Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'library_name',
            'xmax',
            'xmin',
            'ymax',
            'ymin',
        )
    )
    index_column_data_expected = {
        'column_rank': 1,
        'column_name': 'id',
        'field_type': 'I',
        'field_length': 1,
        'key_type': 'P',
        'column_textual_description': 'Row Identifier',
        'optional_value_description_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
        'optional_thematic_index_name': vpf.EMPTY_FIELD_PLACEHOLDER,
        'optional_column_narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    with open(VPF_ROOT / 'scenario' / '42' / 'lat', 'rb') as source:
        lat = vpf.Table(label, source.read(328))
        for key, value in base_expectation.items():
            assert lat.table[key] == value
        assert sorted(lat.table['columns']) == column_names_expected
        assert lat.table['columns']['id'] == index_column_data_expected
