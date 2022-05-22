import pathlib

import attribuutit.vpf as vpf

VPF_ROOT = pathlib.Path('local', 'incoming')


def test_table_library_reference_edge_bounding_rectangle_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 222,
        'header_byte_offset': 5,
        'table_description': 'Edge Bounding Rectangle Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
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
    with open(VPF_ROOT / 'scenario' / '42' / 'libref' / 'ebr', 'rb') as source:
        ebr = vpf.Table(label, source.read(4606))  # noqa
        for key, value in base_expectation.items():
            assert ebr.table[key] == value
        assert sorted(ebr.table['columns']) == column_names_expected
        assert ebr.table['columns']['id'] == index_column_data_expected  # noqa


def test_table_library_reference_text_primitive_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 134,
        'header_byte_offset': 5,
        'table_description': 'Text Primitive Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'string',
            'shape_line',
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
    with open(VPF_ROOT / 'scenario' / '42' / 'libref' / 'txt', 'rb') as source:
        txt = vpf.Table(label, source.read(397))  # noqa
        for key, value in base_expectation.items():
            assert txt.table[key] == value
        assert sorted(txt.table['columns']) == column_names_expected
        assert txt.table['columns']['id'] == index_column_data_expected  # noqa


def test_table_library_reference_character_value_description_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 261,
        'header_byte_offset': 5,
        'table_description': 'Library Reference Character Value Description Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'table',
            'attribute',
            'value',
            'description',
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
    with open(VPF_ROOT / 'scenario' / '42' / 'libref' / 'char.vdt', 'rb') as source:
        char_vdt = vpf.Table(label, source.read(418))  # noqa
        for key, value in base_expectation.items():
            assert char_vdt.table[key] == value
        assert sorted(char_vdt.table['columns']) == column_names_expected
        assert char_vdt.table['columns']['id'] == index_column_data_expected  # noqa


def test_table_library_reference_feature_class_schema_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 301,
        'header_byte_offset': 5,
        'table_description': 'Library Reference Feature Class Schema Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'feature_class',
            'table1',
            'table1_key',
            'table2',
            'table2_key',
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
    with open(VPF_ROOT / 'scenario' / '42' / 'libref' / 'fcs', 'rb') as source:
        fcs = vpf.Table(label, source.read(537))  # noqa
        for key, value in base_expectation.items():
            assert fcs.table[key] == value
        assert sorted(fcs.table['columns']) == column_names_expected
        assert fcs.table['columns']['id'] == index_column_data_expected  # noqa


def test_table_library_reference_connected_primitive_parsing():
    label = 'scenario-42'
    base_expectation = {
        'error': False,
        'error_detail': '',
        'byte_order': 'little',
        'byte_order_explicit': True,
        'header_length': 171,
        'header_byte_offset': 5,
        'table_description': 'Connected Node Primitive Table',
        'narrative_table_name': vpf.EMPTY_FIELD_PLACEHOLDER,
    }
    column_names_expected = sorted(
        (
            'id',
            'first_edge',
            'coordinate',
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
    with open(VPF_ROOT / 'scenario' / '42' / 'libref' / 'cnd', 'rb') as source:
        cnd = vpf.Table(label, source.read(4415))  # noqa
        for key, value in base_expectation.items():
            assert cnd.table[key] == value
        assert sorted(cnd.table['columns']) == column_names_expected
        assert cnd.table['columns']['id'] == index_column_data_expected  # noqa
