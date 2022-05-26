import numpy as np
import dataclasses
import pickle
from typing import List, Dict, Optional, Union
from pathlib import Path
from tqdm import tqdm
from scipy.sparse import csr_matrix

from sumo_output_parsers.logger_unit import logger
from sumo_output_parsers.models.parser import ParserClass
from sumo_output_parsers.models.matrix import MatrixObject


@dataclasses.dataclass
class FcdMatrixObject(MatrixObject):
    """
    """
    matrix: csr_matrix
    value2id: Dict[str, int]
    car2id: Dict[str, int]
    interval_begins: np.ndarray
    value_type: str
    interval_end: Optional[np.ndarray] = None
    sub_sampling_interval: Optional[int] = None

    @classmethod
    def from_pickle(self, path_pickle: Path) -> "FcdMatrixObject":
        with path_pickle.open('rb') as f:
            data = pickle.load(f)
        return FcdMatrixObject(**data)


class FCDFileParser(ParserClass):
    def __init__(self, path_file: Path, is_caching: bool = True):
        """A handler class that parse output-files of Sumo's output.
        Args:
            path_file: pathlib.Path object that leads into output file's path.
            is_caching
        """
        super().__init__(path_file, is_caching=is_caching)
        self.name_vehicle_node = 'vehicle'
        self.name_time_node = 'timestep'
        self.pre_defined_attribute = ['id']

    def get_attributes(self, is_traverse_all: bool = False) -> List[str]:
        max_search = 10
        metrics = []
        for search_i, elem in enumerate(self.getelements(str(self.path_file), self.name_vehicle_node)):
            if is_traverse_all is False and search_i == max_search:
                return list(set(metrics))
            # end if
            item_list = [e for e in elem.attrib.keys() if e not in self.pre_defined_attribute]
            metrics += item_list
        # end for
        return list(set(metrics))

    def xml2matrix(self, target_element: str, skip_intervals: int = -1) -> FcdMatrixObject:
        """generates matrix object with the specified key name.
        Args:
            target_element: a name of key which corresponds to values of the matrix.
            skip_intervals: parameter of sub-sampling. -1 is disable.
        Return:
            FcdMatrixObject
        """
        # region caching check
        p_cache = self.generate_cache_path(method_name='xml2matrix', suffix=self.encode_parameters(
            path_file=str(self.path_file),
            target_element=target_element,
            skip_intervals=skip_intervals))
        if self.is_caching and self.check_cache_file(p_cache):
            logger.info(f'using caching {p_cache}')
            return FcdMatrixObject.from_pickle(p_cache)
        # endregion

        route_stack = []
        car_ids = []
        values = []
        seq_begin = []
        time_interval = 0
        __time_interval: Optional[float] = None
        logger.info('Parsing FCD xml...')
        __car_ids = []
        __values = []
        if skip_intervals != -1:
            logger.info(f'`skip_intervals` = {skip_intervals} is available. The method sub-samples.')
        # end if
        for elem in tqdm(self.getelements(str(self.path_file), tag=self.name_time_node)):
            if skip_intervals != -1:
                if time_interval % skip_intervals != 0:
                    time_interval += 1
                    continue
            # end if

            seq_begin.append(elem.attrib['time'])
            element_time_interval = []
            __car_ids = []
            __values = []
            for vehicle_tree in elem.findall('vehicle'):
                __values.append(vehicle_tree.attrib[target_element])
                __car_ids.append(vehicle_tree.attrib['id'])
                element_time_interval.append(
                    (time_interval, vehicle_tree.attrib['id'], vehicle_tree.attrib[target_element]))
            # end for
            car_ids += list(set(__car_ids))
            values += list(set(__values))
            route_stack += element_time_interval
            time_interval += 1
        # end for
        del __values
        del __car_ids

        assert len(car_ids) > 0 and len(values) > 0 and len(route_stack) > 0, 'Nothing extracted from the FCD output.'
        car_ids = list(sorted(list(set(car_ids))))
        values = list(sorted(list(set(values))))
        logger.info(f'Parsing done. n-time-interval={time_interval} car-types={len(car_ids)} value-types={len(values)}')
        # convert lane-id & car-id into integer
        car2id = {car_id: i for i, car_id in enumerate(car_ids)}
        value_type = self.detect_data_type(values)
        if value_type == str:
            values2id = {lane_id: i for i, lane_id in enumerate(values)}
        elif value_type == float or value_type == int:
            values2id = None
            route_stack = [(t[0], t[1], value_type(t[2])) for t in route_stack]
        else:
            raise NotImplementedError('undefined case.')
        # end if
        time2id = None
        lane_matrix = self.generate_csr_matrix(
            data_stack=route_stack,
            row_index2id=car2id,
            data_index2id=values2id,
            time_interval=time_interval,
            col_index2id=time2id
        )

        begin_time_vector = np.array(seq_begin)
        assert len(lane_matrix.shape) == 2, f'The method expects 2nd array. But it detects {lane_matrix.shape} object. ' \
                                            f'Check your xml file at {self.path_file}'
        m_obj = FcdMatrixObject(
            matrix=lane_matrix,
            value2id=values2id,
            car2id=car2id,
            interval_begins=begin_time_vector,
            value_type=target_element,
            sub_sampling_interval=skip_intervals
        )
        if self.is_caching:
            m_obj.to_pickle(p_cache)
        # endif
        return m_obj
