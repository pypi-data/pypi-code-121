import dataclasses
from typing import Optional, Dict, List

import numpy as np
import pandas
from pathlib import Path

from sumo_output_parsers.models.parser import CsvBasedParser
from sumo_output_parsers.models.statics import PATH_CACHING_DIR


class StatisticFileParser(CsvBasedParser):
    """A parser class to parse statistic.xml."""
    def __init__(self,
                 path_xml_file: Path,
                 name_xsd: str = 'statistic_file.xsd',
                 path_working_dir: Optional[Path] = PATH_CACHING_DIR,
                 matrix_index: str = '',
                 matrix_column: str = '',
                 is_caching: bool = True):
        super(StatisticFileParser, self).__init__(path_xml_file=path_xml_file,
                                                  name_xsd=name_xsd,
                                                  path_working_dir=path_working_dir,
                                                  index_header_name=matrix_index,
                                                  column_header_name=matrix_column,
                                                  is_caching=is_caching)

    @staticmethod
    def clean_up_dataframe(df_statistics: pandas.DataFrame) -> pandas.DataFrame:
        return_records = []
        for c_name in df_statistics.columns:
            non_nan_cell = df_statistics[c_name].dropna()
            if len(non_nan_cell) == 0:
                return_records.append({'metric': c_name, 'value': np.NaN})
            else:
                return_records.append({'metric': c_name, 'value': non_nan_cell.item()})
        # end if
        _df = pandas.DataFrame(return_records)
        return _df

    def xml2matrix(self, target_element: str, agg_func = None):
        raise NotImplementedError('`xml2matrix() is not available for summary output.`')

