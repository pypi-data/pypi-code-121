import os
import pandas as pd

from d3m import container, utils as d3m_utils
from d3m.metadata import base as metadata_base, hyperparams
from d3m.primitive_interfaces import base, transformer

import common_primitives

__all__ = ('HorizontalConcatListPrimitive',)

Inputs = container.List
Outputs = container.DataFrame


class Hyperparams(hyperparams.Hyperparams):
    pass


class HorizontalConcatListPrimitive(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which concatenates multiple DataFrames horizontally.

    It is required that all DataFrames have the same number of samples.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '3e53391c-74aa-443f-bf2a-8890f3e7d7b6',
            'version': common_primitives.__version__,
            'name': "Concatenate multiple dataframes",
            'python_path': 'd3m.primitives.data_transformation.multi_horizontal_concat.Common',
            'source': {
                'name': common_primitives.__author__,
                'contact': 'mailto:dmartinez05@tamu.edu',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/horizontal_concat.py',
                    'https://gitlab.com/datadrivendiscovery/common-primitives.git',
                ],
            },
            'installation': [{
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'd3m-common-primitives',
                'version': '2022.5.26',
            }],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.ARRAY_CONCATENATION,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_TRANSFORMATION,
        },
    )

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        if len(inputs) < 2:
            raise ValueError("At least a list of two values are required.")

        # We get the first dataframe that contains and index, otherwise disregard.
        for i in range(0, len(inputs)):
            if inputs[i].metadata.get_index_columns():
                if i != 0:
                    index_dataframe = inputs.pop(i)
                    inputs.insert(0, index_dataframe)
                break

        # we assume the index metadata is on the first dataframe
        new_metadata = inputs[0].metadata
        for i in range(1, len(inputs)):
            i_metadata = inputs[i].metadata
            column_indexes = i_metadata.get_index_columns()
            if column_indexes:
                i_metadata = i_metadata.remove_columns(column_indexes)

                # we drop index columns on the dataframe.
                inputs[i].drop(inputs[i].columns[column_indexes], axis=1, inplace=True)
            new_metadata = new_metadata.append_columns(i_metadata, use_right_metadata=False)

        new_dataframe = pd.concat(inputs, axis=1)
        new_dataframe.metadata = new_metadata
        return base.CallResult(new_dataframe)
