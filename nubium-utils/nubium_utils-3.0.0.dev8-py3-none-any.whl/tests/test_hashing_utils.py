from unittest import TestCase

from nubium_utils.hashing_utils import hash_record


class TestRecordHasher(TestCase):

    def setUp(self) -> None:
        self.test_record = {
            "desired_field_1": "value_1",
            "desired_field_2": "value_2",
            "undesired_field_3": "value_3"
        }
        self.desired_field_mask = {
            "desired_field_1": True,
            "desired_field_2": True,
            "undesired_field_3": False
        }
        self.expected_hex_digest = '50cb97c5e1a0078bad72104eb389b65b'

    def test_dictionary_hash(self):
        """Function should return a hash of a dictionary using the desired fields"""
        record_hash = hash_record(self.test_record, self.desired_field_mask)
        assert self.expected_hex_digest == record_hash.hexdigest()

    def test_ignores_unincluded_fields(self):
        """Shouldn't include fields that we don't want in the hash"""
        record_hash = hash_record(self.test_record, self.desired_field_mask)
        hex_digest_using_all_fields = '8c7855a8a95074460d09ea7a00ecff7f'
        assert hex_digest_using_all_fields != record_hash.hexdigest()

    def test_repeatable_hash(self):
        """Hash function should return the same output given the same input"""
        record_hash_1 = hash_record(self.test_record, self.desired_field_mask)
        record_hash_2 = hash_record(self.test_record, self.desired_field_mask)

        assert record_hash_1.hexdigest() == record_hash_2.hexdigest()

    def test_nested_fields(self):
        test_record = {
            "desired_field_1": "value_1",
            "desired_field_2": {
                "desired_field_3": "value_3",
                "undesired_field_4": "value_4",
                "desired_field_5": {
                    "desired_field_6": "value_6"
                }
            },
            "undesired_field_7": "value_7"
        }
        test_map = {
            "desired_field_1": True,
            "desired_field_2": {
                "desired_field_3": True,
                "undesired_field_4": False,
                "desired_field_5": {
                    "desired_field_6": True
                }
            },
            "undesired_field_7": False
        }
        output_record = hash_record(test_record, test_map)
        expected_output = '63f8a9b3e2836f6f469154d59a7270d2'
        assert output_record.hexdigest() == expected_output

    def test_list_field(self):
        test_record = {
            "field_1": ["value_1", "value_2", "value_3"]
        }
        test_map = {"field_1": True}
        output_hash = hash_record(test_record, test_map)
        expected_output = '81cc8e59f248a7ec3a94bd105c48619c'
        assert output_hash.hexdigest() == expected_output
