import unittest
from io import BytesIO

import importlib_resources
from werkzeug.datastructures import FileStorage

from fiddler.file_processor.src.constants import ExtractorFileType
from fiddler.file_processor.src.extractor import FileExtractor


class LocalFileExtractorTest(unittest.TestCase):
    def test_local_disk_extractor_with_single_file_should_succeed(self):
        # GIVEN
        files = {}
        filepath_context_manager = importlib_resources.path(
            'fiddler.file_processor.tests.resources.csvs', 'credit_risk_dataset.csv'
        )
        file_name = 'credit_risk_dataset.csv'
        with filepath_context_manager as fh:
            buf = BytesIO(fh.read_bytes())

            files = {file_name: FileStorage(buf, file_name)}

        # WHEN
        extractor = FileExtractor.get_extractor('LOCAL_DISK')
        file_list = extractor.extract(files)

        # THEN
        for temp_dir, file_path, file_extension in file_list:
            assert file_extension == ExtractorFileType.CSV
            assert file_path.split('/')[-1] == file_name

        assert len(file_list) == 1

    def test_local_disk_extractor_with_multiple_files_should_succeed(self):
        # GIVEN
        files = {}
        filepath_context_manager = importlib_resources.path(
            'fiddler.file_processor.tests.resources.csvs', 'credit_risk_dataset.csv'
        )
        second_filepath_context_manager = importlib_resources.path(
            'fiddler.file_processor.tests.resources.csvs', 'credit_risk_dataset_1.csv'
        )
        first_file_name = 'credit_risk_dataset.csv'
        second_file_name = 'credit_risk_dataset_1.csv'
        with filepath_context_manager as fh:
            first_file_buffer = BytesIO(fh.read_bytes())

        with second_filepath_context_manager as fh:
            second_file_buffer = BytesIO(fh.read_bytes())

            files = {
                first_file_name: FileStorage(first_file_buffer, first_file_name),
                second_file_name: FileStorage(second_file_buffer, second_file_name),
            }

        # WHEN
        extractor = FileExtractor.get_extractor('LOCAL_DISK')
        file_list = extractor.extract(files)

        # THEN
        for temp_dir, file_path, file_extension in file_list:
            assert file_extension == ExtractorFileType.CSV
            assert file_path.split('/')[-1] in [first_file_name, second_file_name]

        assert len(file_list) == 2


if __name__ == '__main__':
    unittest.main()
