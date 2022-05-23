import unittest

from lumipy.atlas.atlas import Atlas
from test.unit.utilities.test_utils import make_test_atlas, assert_locked_lockable
from inspect import signature


class TestAtlas(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.atlas = make_test_atlas()

    def test_atlas_construction(self):

        # Given an atlas constructed from field table catalog and entitlement resources
        # When you try to add a new attribute then it should throw
        assert_locked_lockable(self, self.atlas)

        # The number of provider descriptions on the atlas should be the expected
        providers = self.atlas.list_providers()
        self.assertEqual(len(providers), 261)
        self.assertEqual(len([p for p in providers if p.get_provider_type() == 'DataProvider']), 240)
        self.assertEqual(len([p for p in providers if p.get_provider_type() == 'DirectProvider']), 21)

        # Given the saved AppRequest provider info
        app_req = self.atlas.lusid_logs_apprequest
        # Should have the right number of columns
        cols = app_req.list_columns()
        self.assertEqual(len(cols), 30)
        # Should have the right number of params
        params = app_req.list_parameters()
        self.assertEqual(len(params), 6)
        # Should have the right number of fields overall (cols + params)
        self.assertEqual(len(app_req.list_fields()), 36)

        for factory in self.atlas.list_providers():
            # Check all providers have attached column descriptions
            # Check attributes
            for field_description in factory.list_fields():
                self.assertEqual(field_description.table_name, factory._table_name)
                self.assertNotEqual(field_description.field_name, '')
                self.assertNotEqual(field_description.field_name, None)
                self.assertTrue(hasattr(factory, field_description.get_name()), msg=f'Field {field_description.get_name()} is missing')

            # parameters on factory.__call__ must match the provider's parameter count (+ self)
            call_params = signature(factory.__call__).parameters
            self.assertEqual(
                len(factory.list_parameters()),
                len(call_params) if factory.get_provider_type() == 'DataProvider' else len(call_params) - 2,
                msg=f'''Params on {type(factory).__name__}.__call__ do not match the number of expected parameters
                    expected -> {', '.join(param.get_name() for param in factory.list_parameters())}
                    __call__ -> {', '.join(param for param in call_params)}
                '''
            )

            if factory.get_provider_type() == 'DataProvider':
                # Column content must not be zero for data providers
                self.assertTrue(
                    len(factory.list_columns()) > 0,
                    msg=f"Provider description {factory.get_name()} has no columns"
                )

                # Factory column metadata must match the columns on the generated table object
                table = factory()
                self.assertEqual(
                    len(table.get_columns()),
                    len(factory.list_columns()),
                    msg=f'Column mismatch between {type(factory).__name__} and  the table it produced'
                )

    def test_atlas_search(self):

        result = self.atlas.search_providers('aws')

        self.assertEqual(type(result), Atlas)
        self.assertEqual(len(result.list_providers()), 21)
        for p_description in result.list_providers():
            self.assertTrue(
                'aws' in p_description.get_name()
                or 'aws' in p_description.get_table_name().lower()
                or 'aws' in p_description.get_description().lower()
                or any('aws' in f.get_name() for f in p_description.list_fields())
            )
