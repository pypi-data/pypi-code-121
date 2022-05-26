import pathlib
import shutil
import typing
import urllib.parse
from pathlib import Path
from typing import Optional, List, Union, Dict, Tuple
from scipy.sparse import csr_matrix
from lxml import etree
from tempfile import mkdtemp
import more_itertools
import os
import sys
import subprocess
import time
import pandas
import base64
import json
import hashlib

import numpy as np
import requests

from sumo_output_parsers.models.matrix import MatrixObject
from sumo_output_parsers.logger_unit import logger
from sumo_output_parsers.models import statics


class ParserClass(object):
    def __init__(
            self,
            path_file: Path,
            path_cache: Path = statics.PATH_CACHING_DIR,
            is_caching: bool = True):
        """A handler class that parse output-files of Sumo's output.
        Args:
            path_file: pathlib.Path object that leads into output file path.
            path_cache: pathlib.Path
            is_caching: True if a parser holds processed files, False not.
        """
        assert path_file.exists(), f'No input file named {path_file}'
        self.path_file = path_file
        self.path_cache = path_cache
        self.is_caching = is_caching
        self.generate_caching_directory()
        self.cache_param_max_length = 100

    def generate_caching_directory(self):
        if self.is_caching and not pathlib.Path(self.path_cache).exists():
            pathlib.Path(self.path_cache).mkdir()

    def check_cache_file(self, path_cache: pathlib.Path) -> bool:
        """check an existing file in the cache directory and return the path.

        Returns: True or False.
        """
        if path_cache.exists():
            return True
        else:
            return False

    def generate_cache_path(self, method_name: str, suffix: str) -> pathlib.Path:
        return self.path_cache.joinpath(f'{self.__class__.__name__}-{method_name}-{suffix}')

    def encode_parameters(self, **kwargs) -> str:
        """generate base64 encoded string"""
        message_bytes = json.dumps(kwargs).encode('utf-8')
        base64_bytes = base64.b64encode(message_bytes)
        hash_key = hashlib.md5(base64_bytes).hexdigest()
        return hash_key

    @staticmethod
    def generate_time2id(time_intervals_begin: List[str]) -> Dict[str, int]:
        __ = {t: i for i, t in enumerate(more_itertools.unique_everseen(time_intervals_begin))}
        return __

    @staticmethod
    def detect_data_type_time(time_interval_begin: List[Union[str, int]],
                              is_traverse_all: bool = False) -> object:
        max_search = 10
        time_dtype = None
        for i, t in enumerate(time_interval_begin):
            try:
                t_int = int(t)
                time_dtype = float
            except ValueError:
                time_dtype = str

            if is_traverse_all is False and i == max_search:
                return time_dtype
            # end if
        # end for
        return time_dtype

    @staticmethod
    def detect_data_type(data_sequence: List[Union[str, int]],
                         is_traverse_all: bool = False) -> object:
        max_search = 10
        _dtype = str
        for i, t in enumerate(data_sequence):
            try:
                float(t)
                _dtype = float
            except:
                try:
                    int(t)
                    _dtype = int
                except:
                    _dtype = str
                # end try
            # end try
            if is_traverse_all is False and i == max_search:
                return _dtype
            # end if
        # end for
        return _dtype

    @staticmethod
    def generate_csr_matrix(data_stack: List[Tuple[str, str, Union[str, int, float]]],
                            row_index2id: Dict[str, int],
                            time_interval: int,
                            data_index2id: Dict[str, int] = None,
                            col_index2id: Dict[str, int] = None) -> csr_matrix:
        # data
        __row = []
        __col = []
        __data = []
        for data_t in data_stack:
            __col.append(data_t[0])
            assert isinstance(data_t[1], str), 'The 1st index must be `str` type.'
            __row.append(row_index2id[data_t[1]])
            if data_index2id is not None:
                __data.append(data_index2id[data_t[2]])
            else:
                __data.append(data_t[2])
        # end for
        if col_index2id is not None:
            col = np.array([col_index2id[c] for c in __col])
        else:
            col = np.array(__col, dtype=np.int)
        # end if
        row = np.array(__row)
        data = np.array(__data)
        del __row, __col, __data
        assert len(col) == len(data) == len(row)
        logger.info(f'row-size={len(set(row))} column-size={len(set(col))}')
        # matrix-size
        matrix_size = (row.max() + 1, time_interval + 1)
        target_matrix = csr_matrix((data, (row, col)), shape=matrix_size)
        return target_matrix

    @staticmethod
    def getelements(filename_or_file, tag):
        context = iter(etree.iterparse(filename_or_file, events=('start', 'end')))
        _, root = next(context)  # get root element
        for event, elem in context:
            if event == 'end' and elem.tag == tag:
                yield elem
                root.clear()  # preserve memory

    @staticmethod
    def get_attributes(self) -> List[str]:
        raise NotImplementedError()

    @staticmethod
    def matrix_with_autofill(matrix_stack: List[List[float]]) -> np.ndarray:
        """auto-fill a matrix object with nan value if lengths of lists are different.
        :param matrix_stack: 2nd list. [[value]]
        :return: 2nd ndarray.
        """
        max_length = max([len(l) for l in matrix_stack])
        min_length = min([len(l) for l in matrix_stack])
        if max_length == min_length:
            matrix_value = np.array(matrix_stack)
            return matrix_value
        else:
            matrix_value = np.zeros([len(matrix_stack), max_length])
            logger.warning('The output file different length of elements. I replaced insufficient values with Nan. '
                           'Be careful the existence of Nan values.')
            matrix_value[:] = np.NAN
            for i, j in enumerate(matrix_stack):
                matrix_value[i][0:len(j)] = j
            # end for
            return matrix_value

    def to_array_objects(self, aggregation_on: str) -> MatrixObject:
        raise NotImplementedError()

    def xml2matrix(self, target_element: str):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'ResultFile class for {self.path_file}'


class CsvBasedParser(ParserClass):
    """A base class that utilises SUMO-default csv script. SUMO is supposed to be installed in your environment."""
    def __init__(self,
                 path_xml_file: Path,
                 name_xsd: str,
                 index_header_name: str,
                 column_header_name: str,
                 path_working_dir: Optional[Path] = statics.PATH_CACHING_DIR,
                 path_default_sumo_home: Path = statics.PATH_DEFAULT_SUMO_HOME,
                 is_caching: bool = True):
        super(CsvBasedParser, self).__init__(path_file=path_xml_file,
                                             path_cache=path_working_dir,
                                             is_caching=is_caching)
        self.name_xsd = name_xsd
        if path_working_dir is None or path_working_dir == statics.PATH_CACHING_DIR:
            self.path_working_dir = Path(mkdtemp())
            self.path_basic_xsd = self.get_basic_xsd_file()
            self.path_xsd = self.get_xsd_schema_file(name_xsd)
        else:
            self.path_working_dir = path_working_dir
            self.path_basic_xsd = path_working_dir.joinpath(statics.NAME_BASE_TYPES)
            self.path_xsd = path_working_dir.joinpath(name_xsd)
            assert self.path_basic_xsd.exists()
            assert self.path_xsd.exists()
        # end if
        self.path_target_script = self.check_sumo_script(path_default_sumo_home)
        self.path_python_interpreter = Path(sys.executable)
        self.path_tmp_csv: Optional[Path] = None
        self.separator = ';'
        self.index_header_name = index_header_name
        self.column_header_name = column_header_name

    @staticmethod
    def check_sumo_script(default_sumo_home: Path) -> Path:
        path_sumo_home = Path(os.environ['SUMO_HOME']) if 'SUMO_HOME' in os.environ else None
        if path_sumo_home is None:
            logger.info(f'No definition of SUMO_HOME. Use default path {default_sumo_home}')
        # end if
        if 'SUMO_HOME' in os.environ:
            assert path_sumo_home.joinpath('tools/xml/xml2csv.py').exists()
            return path_sumo_home.joinpath('tools/xml/xml2csv.py')
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

    def get_basic_xsd_file(self) -> Path:
        r = requests.get(urllib.parse.urljoin(statics.BASE_URL_XSD, statics.NAME_BASE_TYPES),
                         allow_redirects=True)
        path_basic_xsd = self.path_working_dir.joinpath(statics.NAME_BASE_TYPES)
        assert r.status_code == 200
        with path_basic_xsd.open('wb') as f:
            f.write(r.content)
        # end with
        return path_basic_xsd

    def get_xsd_schema_file(self, name_xsd: str) -> Path:
        r = requests.get(urllib.parse.urljoin(statics.BASE_URL_XSD, name_xsd),
                         allow_redirects=True)
        path_xsd = self.path_working_dir.joinpath(name_xsd)
        assert r.status_code == 200
        with path_xsd.open('wb') as f:
            f.write(r.content)
        # end with
        return path_xsd

    def get_attributes(self) -> List[str]:
        assert self.path_tmp_csv is not None, 'run `xml2csv()` first.'
        df = pandas.read_csv(self.path_tmp_csv, sep=self.separator)
        __ = [e for e in df.columns.to_list() if e != self.index_header_name and e != self.column_header_name]
        return __

    def xml2csv(self) -> pandas.DataFrame:
        # region checking caching of an encoded csv file.
        encoded_params = self.encode_parameters(
            separator=self.separator,
            path_xml=self.path_file.__str__())
        p_cache = self.generate_cache_path(method_name='xml2csv', suffix=encoded_params)
        if self.is_caching and p_cache.exists():
            logger.info(f'using cache {p_cache}')
            self.path_tmp_csv = p_cache
            return pandas.read_csv(p_cache, sep=self.separator)
        # endif

        path_out = self.path_working_dir.joinpath(self.path_file.name + '.csv')
        commands = [self.path_python_interpreter.__str__(),
                    self.path_target_script.__str__(),
                    '-s', self.separator,
                    '-x', self.path_xsd.__str__(),
                    '-o', path_out.__str__(), self.path_file.__str__()]
        logger.info(f'running command: {commands}')
        process = subprocess.Popen(commands, stdout=subprocess.PIPE)
        out = process.communicate()[0]
        if self.is_caching:
            shutil.copy(path_out.__str__(), p_cache)
        # end if
        status_code = process.returncode
        assert status_code == 0, f'Failed to execute the command {" ".join(commands)}'
        time.sleep(1)
        assert path_out.exists()
        self.path_tmp_csv = path_out
        df = pandas.read_csv(path_out, sep=self.separator)
        return df

    def _xml2matrix(self, target_element: str, agg_func: Optional[str] = None) -> pandas.DataFrame:
        assert self.path_tmp_csv is not None, 'run `xml2csv()` first.'
        df = pandas.read_csv(self.path_tmp_csv, sep=self.separator)
        check_df = df[[self.index_header_name, self.column_header_name, target_element]]
        if agg_func is None:
            assert len(check_df[check_df.duplicated()]) == 0, \
                f'Detected duplicated {len(check_df[check_df.duplicated()])} rows. Use `agg_func` argument to aggregate values.'
            matrix_df = df.pivot_table(index=self.index_header_name, columns=self.column_header_name, values=[target_element],
                                       aggfunc='first')
        else:
            matrix_df = df.pivot_table(index=self.index_header_name, columns=self.column_header_name, values=[target_element],
                                       aggfunc=agg_func)
        # end

        return matrix_df

    @staticmethod
    def index2id(matrix_df: pandas.DataFrame) -> Dict[str, int]:
        return {f: i for i, f in enumerate(sorted(matrix_df.index.tolist()))}

    @staticmethod
    def column2id(matrix_df: pandas.DataFrame) -> List[str]:
        return [f[1] for i, f in enumerate(sorted(matrix_df.columns.tolist()))]

    @staticmethod
    def _generate_feature_map(matrix_df: pandas.DataFrame) -> Dict[str, int]:
        values_ndarray = matrix_df.values
        elements = [e for e in list(set(values_ndarray.flatten())) if isinstance(e, str)]
        features = {f: i for i, f in enumerate(sorted(elements))}
        features.update({np.nan: np.nan})
        return features

    def xml2matrix(self, target_element: str):
        raise NotImplementedError()







