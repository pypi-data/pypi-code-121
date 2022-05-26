import dataclasses
from typing import Optional, Dict, List

import scipy.sparse
from scipy.sparse import csr_matrix
from pathlib import Path
import numpy as np

from sumo_output_parsers.models.parser import CsvBasedParser, MatrixObject
from sumo_output_parsers.models.statics import PATH_CACHING_DIR

@dataclasses.dataclass
class CollisionMatrixObject(MatrixObject):
    matrix: csr_matrix
    lane2id: Dict[str, int]
    interval_begins: List[str]
    value_type: str
    value2id: Dict[str, int] = None


class CollisionFileParser(CsvBasedParser):
    def __init__(self,
                 path_xml_file: Path,
                 name_xsd: str = 'collision_file.xsd',
                 path_working_dir: Optional[Path] = PATH_CACHING_DIR,
                 matrix_index: str = 'collision_lane',
                 matrix_column: str = 'collision_time',
                 is_caching: bool = True
                 ):
        super(CollisionFileParser, self).__init__(path_xml_file=path_xml_file,
                                                  name_xsd=name_xsd,
                                                  path_working_dir=path_working_dir,
                                                  index_header_name=matrix_index,
                                                  column_header_name=matrix_column,
                                                  is_caching=is_caching)

    def xml2matrix(self, target_element: str, agg_func = None) -> CollisionMatrixObject:
        matrix_df = self._xml2matrix(target_element, agg_func=agg_func)
        if matrix_df.values.dtype == object:
            feature_map = self._generate_feature_map(matrix_df)
            matrix_ndarray = np.vectorize(feature_map.get)(matrix_df)
        else:
            feature_map = None
            matrix_ndarray = matrix_df.values
        # end if
        csr = scipy.sparse.csr_matrix(matrix_ndarray)

        # end if
        return CollisionMatrixObject(
            matrix=csr,
            lane2id=self.index2id(matrix_df),
            interval_begins=self.column2id(matrix_df),
            value_type=target_element,
            value2id=feature_map
        )

