import dataclasses
import itertools
from pathlib import Path
from typing import Optional, List
import pickle
from tqdm import tqdm

from scipy.sparse import csr_matrix
import numpy

from sumo_output_parsers.logger_unit import logger
from sumo_output_parsers.models.parser import ParserClass
from sumo_output_parsers.models.matrix import MatrixObject


@dataclasses.dataclass
class LoopDetectorMatrixObject(MatrixObject):
    matrix: csr_matrix
    detectors: numpy.ndarray
    interval_begins: numpy.ndarray
    interval_end: numpy.ndarray
    value_type: str

    @classmethod
    def from_pickle(self, path_pickle: Path) -> "LoopDetectorMatrixObject":
        with path_pickle.open('rb') as f:
            data = pickle.load(f)
        return LoopDetectorMatrixObject(**data)


class LoopDetectorParser(ParserClass):
    """A handler class that parse output-files of Sumo's output.
    Args:
        path_file: pathlib.Path object that leads into output file's path.
    """
    def __init__(self, path_file: Path, is_caching: bool = True):
        super(LoopDetectorParser, self).__init__(path_file, is_caching=is_caching)
        self.name_interval_node = 'interval'
        self.pre_defined_attribute = ['begin', 'end', 'id']

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'ResultFile class for {self.path_file}'

    def get_attributes(self, is_traverse_all: bool = False) -> List[str]:
        max_search = 10
        metrics = []
        for search_i, elem in enumerate(self.getelements(str(self.path_file), self.name_interval_node)):
            if is_traverse_all is False and search_i == max_search:
                return list(set(metrics))
            # end if
            item_list = [e for e in elem.attrib.keys() if e not in self.pre_defined_attribute]
            metrics += item_list
        # end for
        return list(set(metrics))

    def xml2matrix(self, target_element: str) -> LoopDetectorMatrixObject:
        """generates matrix object with the specified key name.
        Args:
            target_element: a name of key which corresponds to values of the matrix.
        Returns:
             MatrixObject
        """
        # region caching check
        p_cache = self.generate_cache_path(method_name='xml2matrix', suffix=self.encode_parameters(
            path_file=str(self.path_file),
            target_element=target_element))
        if self.is_caching and self.check_cache_file(p_cache):
            logger.info(f'using caching {p_cache}')
            return LoopDetectorMatrixObject.from_pickle(p_cache)
        # endregion

        stacks = []
        detector_ids = []
        time_interval_begin = []
        time_interval_end = []
        time_interval = 0
        current_time_label = ''
        logger.info('Parsing loop xml...')
        for i, elem in enumerate(self.getelements(str(self.path_file), tag=self.name_interval_node)):
            if i == 0:
                current_time_label = elem.get('begin')
            # end if
            detector_id: str = elem.get('id')
            time_begin: str = elem.get('begin')
            time_end: str = elem.get('end')
            obj_value = float(elem.get(target_element))
            try:
                if obj_value == '':
                    target_value = 0.0
                elif obj_value is None:
                    target_value = 0.0
                else:
                    target_value = float(elem.get(target_element))
            except ValueError:
                raise SystemError(f'unexpected error during parsing values because of {obj_value}')
            except KeyError:
                keys = elem.attrs.keys()
                raise KeyError(f'Invalid key name. Available keys are {keys}')
            # end try
            time_interval_begin.append(time_begin)
            time_interval_end.append(time_end)
            detector_ids.append(detector_id)
            stacks.append((time_begin, detector_id, target_value))
            if current_time_label != time_begin:
                time_interval += 1
                current_time_label = time_begin
            # end if
        # end for

        time2id = self.generate_time2id(time_interval_begin) \
            if self.detect_data_type_time(time_interval_begin) else None
        det_ids = list(sorted(list(set(detector_ids))))
        logger.info(f'Parsing done. n-time-interval = {time_interval + 1} detector-ids={len(det_ids)}')
        detector2id = {car_id: i for i, car_id in enumerate(det_ids)}
        metric_matrix = self.generate_csr_matrix(
            data_stack=stacks,
            row_index2id=detector2id,
            data_index2id=None,
            time_interval=time_interval,
            col_index2id=time2id
        )
        detectors = numpy.array(det_ids)
        begin_time_vector = numpy.array(time_interval_begin)
        end_time_vector = numpy.array(time_interval_end)
        assert len(metric_matrix.shape) == 2, f'The method expects 2nd array. But it detects {metric_matrix.shape} object. ' \
                                              f'Check your xml file at {self.path_file}'
        m_obj = LoopDetectorMatrixObject(
            matrix=metric_matrix,
            detectors=detectors,
            interval_begins=begin_time_vector,
            interval_end=end_time_vector,
            value_type=target_element)
        if self.is_caching:
            m_obj.to_pickle(p_cache)
        return m_obj

    def to_array_objects(self, aggregation_on: str) -> MatrixObject:
        matrix_obj = self.xml2matrix(target_element=aggregation_on)
        return matrix_obj
