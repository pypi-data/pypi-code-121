import json
import os
import unittest
from io import BytesIO

from werkzeug.datastructures import FileStorage

from fiddler.file_processor.src.facade import upload_dataset

package_dir = os.path.dirname(os.path.abspath(__file__))


class FacadeTest(unittest.TestCase):
    def test_upload_dataset_with_valid_dataset_succeed(self):
        files = {}
        file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        file_name = 'credit_risk_dataset.csv'
        with open(file_path, 'rb') as fh:
            buf = BytesIO(fh.read())
            files = {file_name: FileStorage(buf, file_name)}

        schema_file_path = os.path.join(
            package_dir, 'resources/avro/simple_avro_mapping_schema.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        upload_dataset(files, 'LOCAL_DISK', 'avro', file_schema_str)

    def test_upload_dataset_with_invalid_dataset_throw_exception(self):
        files = {}
        file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        file_name = 'credit_risk_dataset.csv'
        with open(file_path, 'rb') as fh:
            buf = BytesIO(fh.read())
            files = {file_name: FileStorage(buf, file_name)}

        schema_file_path = os.path.join(
            package_dir, 'resources/avro/simple_avro_mapping_schema.json'
        )
        with open(schema_file_path) as fs:
            file_schema_str = json.load(fs)
        self.assertRaises(
            ValueError, upload_dataset, files, 'LOCAL_DISK', 'avro1', file_schema_str
        )

    def test_upload_dataset_with_missing_avro_schema_dataset_throw_exception(self):
        files = {}
        file_path = os.path.join(package_dir, 'resources/avro/simple_avro.avro')
        file_name = 'credit_risk_dataset.csv'
        with open(file_path, 'rb') as fh:
            buf = BytesIO(fh.read())
            files = {file_name: FileStorage(buf, file_name)}

        self.assertRaises(ValueError, upload_dataset, files, 'LOCAL_DISK', 'avro')


if __name__ == '__main__':
    unittest.main()
