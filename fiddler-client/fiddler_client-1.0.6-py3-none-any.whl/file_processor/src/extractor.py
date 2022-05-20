import os
import tempfile
from abc import ABC, abstractmethod

from fiddler.file_processor.src.constants import (
    FILE_EXTENSIONS_TO_CODE,
    SUPPORTABLE_FILE_EXTENSIONS,
    ExtractorDataType,
)


class FileExtractor(ABC):
    @staticmethod
    def get_extractor(datasource):
        if datasource == 'LOCAL_DISK':
            return LocalFileExtractor()
        if datasource == 'S3':
            return S3FileExtractor()
        if datasource == 'GCP':
            return GCPFileExtractor()

    @staticmethod
    def get_supportable_file_extension(object_path, fast_fail=True):
        """
        Given an `object_path`, will return the file's extension (e.g. ".parquet", ".csv")

        If `fast_fail`, will throw an exception should not able to find a supportable file extension
        """
        file_extension = os.path.splitext(object_path)[1]
        for supported_file_extension in SUPPORTABLE_FILE_EXTENSIONS:
            if file_extension in supported_file_extension:
                return FILE_EXTENSIONS_TO_CODE[file_extension]

        if fast_fail:
            err_val = f'Error: File extension not currently supported. \
                        Supported formats are : {SUPPORTABLE_FILE_EXTENSIONS} \
                        Provided format is :{file_extension}'
            raise ValueError(err_val)
        else:
            return ExtractorDataType.UNKNOWN

    @abstractmethod
    def extract(files):
        pass

    def unzip(self):
        pass


class LocalFileExtractor(FileExtractor):
    def extract(self, files):
        """
        Downloads files sent from Fiddler client's local disk to the current pod's disk,
        allowing for further processing.
        """
        temp_dir = tempfile.TemporaryDirectory()
        file_list = []
        for name, file in files.items():
            file_extension = self.get_supportable_file_extension(file.filename)
            file_path = os.path.join(temp_dir.name, file.filename)
            file.save(file_path)
            file_list.append((temp_dir, file_path, file_extension))
        return file_list


class S3FileExtractor(FileExtractor):
    pass


class GCPFileExtractor(FileExtractor):
    pass
