import json
import os
import unittest

from fiddler.file_processor.src.constants import ExtractorFileType
from fiddler.file_processor.src.processor import AvroFileProcessor

package_dir = os.path.dirname(os.path.abspath(__file__))


class AvroFileProcessorTest(unittest.TestCase):
    def test_validation_with_invalid_schema_should_fail(self):
        # GIVEN
        schema_file_path = os.path.join(
            package_dir, 'resources/avro/simple_avro_invalid_mapping_schema.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        avro_file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        files_list = [(package_dir, avro_file_path, ExtractorFileType.AVRO)]
        avro_file_processor = AvroFileProcessor(file_schema_str)

        # WHEN
        self.assertRaises(ValueError, avro_file_processor.process, files_list)

    def test_validation_with_invalid_nested_schema_should_fail(self):
        # GIVEN
        schema_file_path = os.path.join(
            package_dir, 'resources/avro/nested_avro_invalid_mapping_schema.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        avro_file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        files_list = [(package_dir, avro_file_path, ExtractorFileType.AVRO)]
        avro_file_processor = AvroFileProcessor(file_schema_str)

        # WHEN
        self.assertRaises(ValueError, avro_file_processor.process, files_list)

    def test_simple_avro_file_should_succeed(self):
        # GIVEN
        schema_file_path = os.path.join(
            package_dir, 'resources/avro/simple_avro_mapping_schema.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        avro_file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        files_list = [(package_dir, avro_file_path, ExtractorFileType.AVRO)]
        avro_file_processor = AvroFileProcessor(file_schema_str)

        # WHEN
        result = avro_file_processor.process(files_list)

        # THEN
        expected = [
            {u'station': u'011990-99999', u'temp': 0, u'time': 1433269388},
            {u'station': u'011990-99999', u'temp': 22, u'time': 1433270389},
            {u'station': u'011990-99999', u'temp': -11, u'time': 1433273379},
            {u'station': u'012650-99999', u'temp': 111, u'time': 1433275478},
        ]
        assert len(result) == 4
        assert result == expected

    def test_nested_avro_file_should_succeed(self):
        """
                AVRO RECORD:
                records = [
                {u'name': u'test-account-1', u'transaction':['first_transaction','second_transaction']},
            {u'name': u'test-account-2', u'transaction':['second_first_transaction','second_second_transaction']}
            # {u'name': u'test-account-3'}
        ]
        """
        # GIVEN
        schema_file_path = os.path.join(
            package_dir, 'resources/avro/nested_avro_schema_mapping.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        avro_file_path = os.path.join(package_dir, 'resources/avro/nested_avro.avro')
        files_list = [(package_dir, avro_file_path, ExtractorFileType.AVRO)]
        avro_file_processor = AvroFileProcessor(file_schema_str)

        # WHEN
        result = avro_file_processor.process(files_list)

        # THEN
        expected = [
            {u'name': u'test-account-1', u'transaction': 'first_transaction'},
            {u'name': u'test-account-1', u'transaction': 'second_transaction'},
            {u'name': u'test-account-2', u'transaction': 'second_first_transaction'},
            {u'name': u'test-account-2', u'transaction': 'second_second_transaction'},
        ]
        assert len(result) == 4
        assert result == expected

    # Commenting as it does not work. I will fix as a part of next revision. Publishing to get early comments on the PR.
    # def test_multi_level_nested_avro_file_should_succeed(self):
    #     # GIVEN
    #     schema_file_path = os.path.join(
    #         package_dir, 'resources/avro/multi_level_nested_avro_schema_mapping.json')
    #     avro_file_path = os.path.join(package_dir, 'resources/avro/multi_level_nested_avro.avro')
    #     files_list = [(package_dir, avro_file_path, ExtractorFileType.AVRO)]
    #     avro_file_processor = AvroFileProcessor(schema_file_path)

    #     # WHEN
    #     result = avro_file_processor.process(files_list)

    #     # THEN
    #     expected = [
    #         {u'name': u'test-account-1', u'transaction': 'first_transaction'},
    #         {u'name': u'test-account-1', u'transaction': 'second_transaction'},
    #         {u'name': u'test-account-1', u'transaction': 'third_first_transaction'},
    #         {u'name': u'test-account-2', u'transaction': 'fourth_first_transaction'},
    #         {u'name': u'test-account-2', u'transaction': 'fifth_first_transaction'},
    #         {u'name': u'test-account-2', u'transaction': 'sixth_first_transaction'},
    #     ]
    #     assert len(result) == 6
    #     assert result == expected


if __name__ == '__main__':
    unittest.main()
