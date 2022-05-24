from unittest import TestCase
from unittest.mock import patch
from nubium_utils.dict_manipulator import DictManipulator
from copy import deepcopy


class TestDictManipulator(TestCase):
    def tearDown(self):
        self.env_patch.stop()

    def setUp(self):
        self.env = {}
        self.env_patch = patch.dict('os.environ', self.env)
        self.env_patch.start()

        self.junk_func = lambda x: x + '_' if x else ''

        self.fields = {
            "truths": {
                "email_address": '',
                "first_name": 'yay',
                "last_name": 'nay',
                "address": {
                    "address_street": '',
                    "address_city": 'derp??',
                    "address_state": '',
                    "address_postal_code": ''
                },
                "country_name": '',
                "country_code": '',
                "company": '',
                "department": '',
                "industry": '',
                "job_title": 'neat'
            },
            "not_truths": {
                "blah": 'woo-hoo.com',
                "blah2": 'he-he.com'
            }
        }

        self.fields_junk_edit = {
            "truths": {
                "email_address": '',
                "first_name": 'yay_',
                "last_name": 'nay',
                "address": {
                    "address_street": '',
                    "address_city": 'derp??_',
                    "address_state": '',
                    "address_postal_code": ''
                },
                "country_name": '',
                "country_code": '',
                "company": '',
                "department": '',
                "industry": '',
                "job_title": 'neat_'
            },
            "not_truths": {
                "blah": 'woo-hoo.com_',
                "blah2": 'he-he.com'
            }
        }

        self.fields_subset_mask = {
            "truths": {
                "email_address": None,
                "first_name": None,
                "job_title": None,
                "address": {
                    "address_city": None,
                    "address_state": None
                }
            },
            "not_truths": {
                'blah': None
            }
        }

        self.fields_subset_populated = {
            "truths": {
                "email_address": '',
                "first_name": 'yay',
                "job_title": 'neat',
                "address": {
                    "address_city": 'derp??',
                    "address_state": ''
                }
            },
            "not_truths": {
                'blah': 'woo-hoo.com'
            }
        }

        self.dict_manipulator = DictManipulator(self.fields)

    def test__apply_funcs(self):
        self.assertEqual(self.dict_manipulator._apply_funcs([lambda x: x + 'pp', lambda y: y + 'le'], 'a'), 'apple')
        self.assertEqual(self.dict_manipulator._apply_funcs(self.junk_func, 'a'), 'a_')

    def test_apply_func_dict_to_field(self):
        def dumb_func_1(word, junk1=''):
            return word + junk1
        def dumb_func_2(word, junk2=''):
            return word + junk2
        self.dict_manipulator.apply_func_dict_to_field('truths.first_name',
                                                       {dumb_func_1: {'junk1': '_'}, dumb_func_2: {'junk2': 'z'}})
        self.assertEqual(self.dict_manipulator['truths']['first_name'], 'yay_z')

    def test__apply_funcs_to_mask_selection(self):
        self.dict_manipulator._apply_funcs_to_mask_selection(self.fields, self.fields_subset_mask, self.junk_func)
        self.assertDictEqual(self.fields, self.fields_junk_edit)

    def test_apply_funcs_to_mask_selection(self):
        self.dict_manipulator.apply_funcs_to_mask_selection(self.fields_subset_mask, self.junk_func)
        self.assertDictEqual(self.dict_manipulator, self.fields_junk_edit)

    def test__check_if_blanked(self):
        self.assertEqual(self.dict_manipulator._check_if_nulled('woo', ''), 'woo')
        self.assertEqual(self.dict_manipulator._check_if_nulled('', 'wee'), 'wee')
        self.assertEqual(self.dict_manipulator._check_if_nulled('', ''), '')
        self.assertEqual(self.dict_manipulator._check_if_nulled('woo', 'wee'), 'wee')

    def test__compare_and_overwrite_blanked_values(self):
        self.full_fields_edited = deepcopy(self.fields)
        self.full_fields_edited['not_truths']['blah'] = ''

        self.dict_manipulator._compare_and_overwrite_nulled_values(self.full_fields_edited, self.fields)
        self.assertDictEqual(self.full_fields_edited, self.fields)

    def test_compare_and_overwrite_blanked_values(self):
        self.dict_manipulator['not_truths']['blah'] = ''
        self.dict_manipulator.compare_and_overwrite_nulled_values(self.fields)
        self.assertDictEqual(self.dict_manipulator, self.fields)

    def test__get_populated_mask(self):
        self.assertDictEqual(
            self.dict_manipulator._view_populated_mask(self.fields, self.fields_subset_mask),
            self.fields_subset_populated)

    def test_get_populated_mask(self):
        self.assertDictEqual(self.dict_manipulator.view_populated_mask(self.fields_subset_mask), self.fields_subset_populated)

    def test_get_dict_with_dropped_keys(self):
        output = {
            "truths": {
                "first_name": 'yay',
                "last_name": 'nay',
                "address": {
                    "address_street": '',
                    "address_city": 'derp??',
                    "address_state": '',
                    "address_postal_code": ''
                },
                "country_name": '',
                "country_code": '',
                "company": '',
                "department": '',
                "industry": '',
                "job_title": 'neat'
            },
            "not_truths": {
                "blah2": 'he-he.com'
            }
        }
        self.assertDictEqual(self.dict_manipulator.view_while_ignoring_fields([('truths', 'email_address'),
                                                                               ('not_truths', 'blah')]),
                         output)
