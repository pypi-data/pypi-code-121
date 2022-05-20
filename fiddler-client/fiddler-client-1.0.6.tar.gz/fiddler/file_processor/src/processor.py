import logging
import os
import shutil
import tempfile
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO
from itertools import tee

from fastavro import block_reader as AvroReader
from werkzeug.datastructures import FileStorage

from fiddler.file_processor.src.constants import (
    SENTINEL_ABSENT,
    SUPPORTABLE_FILE_EXTENSIONS,
    FiddlerPublishSchema,
)

from .extractor import FileExtractor
from .utils import open_file_w_auto_close

# from file_processor_utils import getProgressBar
LOG = logging.getLogger(__name__)

DICT_SEPARATOR = '/'
LIST_INDEXER_OPENER = '['
LIST_INDEXER_CLOSER = ']'


class FileProcessorBase(ABC):
    """
    FileProcessorBase is an abstract class. If we need to support any new file type. We need to override the validate
    and transform functions, which defines how we want to convert a given file into desired output type. For now, we are
    converting all the records into python dictionary and then to CSV.
    """

    @staticmethod
    def get_processor(file_type, schema):
        if file_type == 'csv':
            return CsvFileProcessor()
        elif file_type == 'avro':
            return AvroFileProcessor(schema)
        raise ValueError(
            f'Invalid file type. Supported file types are : {SUPPORTABLE_FILE_EXTENSIONS}'
        )

    def process(self, file_list) -> None:
        # file_list = self.unzip(file_list)
        file_list = self.validate(file_list)
        return self.transform(file_list)

    def unzip(self, file_list):
        unzipped_files_list = []
        old_temp_dir = ''

        # Extract files to new temporary directory.
        new_temp_dir = tempfile.TemporaryDirectory()
        for temp_dir, file_path, file_extension in file_list:
            old_temp_dir = temp_dir

            if zipfile.is_zipfile(file_path):
                zip_ref = zipfile.ZipFile(file_path)
                zip_ref.extractall(new_temp_dir.name)
                file_lists = os.listdir(new_temp_dir.name)

                # Generate list of files with new_temp_dir, file, and extension.
                for file_name in file_lists:
                    file_extension = FileExtractor.get_supportable_file_extension(
                        file_name
                    )
                    file_path = os.path.join(new_temp_dir.name, file_name)
                    if file_extension is not None:
                        with open(file_path, 'rb') as fh:
                            buf = BytesIO(fh.read())
                            file = {file_name: FileStorage(buf, file_name)}
                        unzipped_files_list.append((new_temp_dir, file, file_extension))
                zip_ref.close()

        # Clean old temporary directory
        try:
            shutil.rmtree(old_temp_dir.name)
        except (FileNotFoundError, Exception, shutil.Error):
            LOG.info(f'failed to delete directory : {old_temp_dir}')

        return unzipped_files_list

    def parse_key(self, d, k):
        """
        Will properly parse and handle nested values indicated as DICT_SEPARATOR

        # value/nested/final
        # list[-1]
        # list[-1][-1]
        # value/nested/list[-1]/final
        """
        DEFAULT_VALUE = SENTINEL_ABSENT
        ABSENT_IND_VALUE = len(k) + 1

        list_ind_opener = (
            k.find(LIST_INDEXER_OPENER)
            if k.find(LIST_INDEXER_OPENER) > -1
            else ABSENT_IND_VALUE
        )
        dict_sep_ind = (
            k.find(DICT_SEPARATOR) if k.find(DICT_SEPARATOR) > -1 else ABSENT_IND_VALUE
        )

        if k == '':
            # List ends value
            return d

        if dict_sep_ind == list_ind_opener == ABSENT_IND_VALUE:
            # No nested value, no lists. Easy
            return d.get(k, DEFAULT_VALUE)

        if dict_sep_ind < list_ind_opener:
            # Dict separator comes first (or list separator is absent)
            dict_sep_ind = k.find(DICT_SEPARATOR)
            sub_key = k[:dict_sep_ind]

            nested_d = d.get(sub_key, DEFAULT_VALUE)
            if nested_d == DEFAULT_VALUE or nested_d is None:
                return DEFAULT_VALUE

            return self.parse_key(nested_d, k[dict_sep_ind + 1 :])

        elif dict_sep_ind > list_ind_opener:
            # List separator comes first (or dict separator is absent)
            while True:
                opener = k.find(LIST_INDEXER_OPENER)
                closer = k.find(LIST_INDEXER_CLOSER)

                if opener != 0:
                    ind = int(k[opener + 1 : closer])
                    sub_key = k[:opener]
                    nested_d = d.get(sub_key, DEFAULT_VALUE)
                    if nested_d == DEFAULT_VALUE or nested_d is None:
                        return DEFAULT_VALUE

                    d = d[sub_key][ind]
                    k = k[closer + 1 :]
                else:
                    ind = int(k[opener + 1 : closer])
                    d = d[ind]
                    k = k[closer + 1 :]

                if len(k) > 0 and k[0] == '/':
                    # Edge case, next key is a sub
                    k = k[1:]

                if len(k) > 0 and k[0] != LIST_INDEXER_OPENER or len(k) == 0:
                    break

            return self.parse_key(d, k)

        else:
            return DEFAULT_VALUE

    def generate_events(
        self, publish_schema, parent_event_template, rows_iterator, results=[]
    ):
        """
        Transforms the passed event by fixing field names to be DB friendly,
        and then removing fields that are not part of `supported_fields` or a timestamp_column
        """
        event_template = parent_event_template.copy()

        # Get static info
        if FiddlerPublishSchema.STATIC in publish_schema:
            for f_mapping, static_value in publish_schema[
                FiddlerPublishSchema.STATIC
            ].items():
                if static_value is SENTINEL_ABSENT:
                    continue

        for row in rows_iterator:
            row_template = event_template.copy()

            # Get dynamic info
            if FiddlerPublishSchema.DYNAMIC in publish_schema:
                for f_mapping, d_mapping in publish_schema[
                    FiddlerPublishSchema.DYNAMIC
                ].items():
                    if d_mapping is SENTINEL_ABSENT:
                        continue

                    cleaned_val = self.parse_key(row, d_mapping)
                    if cleaned_val is SENTINEL_ABSENT:
                        continue

                    row_template[f_mapping] = cleaned_val

            # Check for iterator recursion point in AVRO files
            if FiddlerPublishSchema.ITERATOR in publish_schema:
                if isinstance(publish_schema[FiddlerPublishSchema.ITERATOR], list):
                    recursed_successfully = False

                    for iter_schema in publish_schema[FiddlerPublishSchema.ITERATOR]:
                        curr_iterator_key = iter_schema[
                            FiddlerPublishSchema.ITERATOR_KEY
                        ]
                        row_iterator = self.parse_key(row, curr_iterator_key)
                        if row_iterator is SENTINEL_ABSENT:
                            # Default behavior if no row iterator present for that key: Pass
                            #     This is done to prevent multiple publishing of exact same base
                            continue

                        recursed_successfully = True
                        self.generate_events(
                            iter_schema, row_template, row_iterator, results
                        )

                    if not recursed_successfully:
                        # Default behavior if no row iterator present for ANY key: publish at current level
                        # log(f'Iterators {iter_keys} specified, but no iterators found in row. Default publishing event at current level.')
                        # publish(event_template)
                        return

                elif isinstance(publish_schema[FiddlerPublishSchema.ITERATOR], dict):
                    iter_schema = publish_schema[FiddlerPublishSchema.ITERATOR]
                    curr_iterator_key = iter_schema[FiddlerPublishSchema.ITERATOR_KEY]
                    row_iterator = self.parse_key(row, curr_iterator_key)
                    if row_iterator is SENTINEL_ABSENT:
                        # Default behavior if no row iterator present for that key: publish at current level
                        # publish(event_template)
                        return
                    else:
                        # print(f' row iterator before result :{row_iterator}')
                        self.generate_events(
                            iter_schema, row_template, row_iterator, results
                        )
                else:
                    # Iterator present in config, but not in row. Default behavior: Publish as is.
                    # publish(event_template)
                    results.append(row_template)
            else:
                # No iterator, publish as is
                # publish(event_template)
                results.append(row_template)
        return results

    @abstractmethod
    def validate(self, file_list):
        pass

    @abstractmethod
    def transform(self, file_list):
        pass


class CsvFileProcessor(FileProcessorBase):
    def validate(self, file_list):
        pass

    def transform(self, file_list):
        pass


class AvroFileProcessor(FileProcessorBase):
    def __init__(self, schema):
        if schema is None:
            raise ValueError('Schema is required for AVRO files')
        self.schema = schema

    def validate(self, file_list):
        LOG.info(f'publish_schema :{self.schema}')
        publish_schema = self.schema
        invalid_keys = self.validate_schema(publish_schema, set())
        if len(invalid_keys) > 0:
            raise ValueError(
                f'Invalid Schema. Schema contains invalid keys : {invalid_keys}.\
                            Valid keys are : {FiddlerPublishSchema.VALID_SCHEMA_KEYWORDS}'
            )
        return file_list

    def validate_schema(self, schema_json, invalid_keys):
        for key in schema_json:
            if key in FiddlerPublishSchema.VALID_SCHEMA_KEYWORDS:
                if key is FiddlerPublishSchema.ITERATOR:
                    return self.validate_schema(schema_json[key], invalid_keys)
            else:
                invalid_keys.add(key)
        return invalid_keys

    def transform(self, file_list):
        results = []
        for temp_path, file_path, file_extension in file_list:
            file_path_str = file_path if isinstance(file_path, str) else file_path.name
            LOG.info(f'avro file path {file_path_str}')
            events_collection = AvroReader(open(file_path_str, 'rb'))
            results.extend(self.process_avro(events_collection))
        return results

    def process_avro(self, avro_reader):
        """
        Breaks the inputstream into a series of rows.

        """
        avro_reader, block_iter = tee(avro_reader)
        num_rows = 0
        for block in block_iter:
            num_rows += block.num_records

        results = []
        for batch, block in enumerate(avro_reader):
            results = self.generate_events(
                publish_schema=self.schema,
                parent_event_template={},
                rows_iterator=block,
                results=results,
            )
            results = [i for i in results if i]
        return results
