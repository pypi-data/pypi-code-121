import unittest

from lumipy.common.string_utils import handle_available_string
from lumipy.atlas.field_metadata import FieldMetadata
from lumipy.atlas.base.base_provider_factory import BaseProviderFactory
from lumipy.atlas.data_provider_metafactory import _DataProviderMetafactory
from test.unit.utilities.test_utils import get_atlas_test_data, standardise_sql_string


class TestProviderFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.data_df, self.direct_df = get_atlas_test_data()

    def test_data_provider_factory_construction(self):

        for _, p_df in self.data_df.groupby('TableName'):

            fields = [FieldMetadata.from_row(row) for _, row in p_df.iterrows()]

            p_row = p_df.iloc[0]
            provider_meta = _DataProviderMetafactory(
                table_name=p_row.TableName,
                description=p_row.Description,
                provider_type=p_row.Type,
                category=p_row.Category,
                last_ping_at=p_row.LastPingAt,
                documentation=p_row.DocumentationLink,
                fields=fields,
                client="dummy client value"
            )()

            self.assertTrue(issubclass(type(provider_meta), BaseProviderFactory))

            self.assertEqual(len(provider_meta.list_fields()), len(fields))
            self.assertEqual(len(provider_meta.list_columns()), len([f for f in fields if f.field_type == 'Column']))
            self.assertEqual(len(provider_meta.list_parameters()), len([f for f in fields if f.field_type == 'Parameter']))

            self.assertEqual(provider_meta.get_name(), p_row.TableName.replace('.', '_').lower())
            self.assertEqual(provider_meta._client, "dummy client value")
            self.assertEqual(provider_meta.get_table_name(), p_row.TableName)
            self.assertEqual(
                standardise_sql_string(provider_meta._description),
                standardise_sql_string(handle_available_string(p_row.Description))
            )
            self.assertEqual(provider_meta._provider_type, p_row.Type)
            self.assertEqual(provider_meta._category, p_row.Category)
            self.assertEqual(provider_meta._last_ping_at, p_row.LastPingAt)
            self.assertEqual(provider_meta._documentation, handle_available_string(p_row.DocumentationLink))

            provider_str = str(provider_meta)
            for field in fields:
                self.assertIn(field.get_name(), provider_str)
                self.assertTrue(hasattr(provider_meta, field.get_name()))
