import os
import typing

from d3m import container, utils as d3m_utils
from d3m.metadata import base as metadata_base
from d3m.metadata import hyperparams
from d3m.primitive_interfaces import base, transformer

import common_primitives

__all__ = ('DataFrameToListPrimitive',)

Inputs = container.DataFrame
Outputs = container.List


class Hyperparams(hyperparams.Hyperparams):
    pass


class DataFrameToListPrimitive(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which converts a pandas dataframe into a list of rows.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '901ff55d-0a0a-4bfd-8195-3a947ba2a8f5',
            'version': common_primitives.__version__,
            'name': "DataFrame to list converter",
            'python_path': 'd3m.primitives.data_transformation.dataframe_to_list.Common',
            'source': {
                'name': common_primitives.__author__,
                'contact': 'mailto:mitar.commonprimitives@tnode.com',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/dataframe_to_list.py',
                    'https://gitlab.com/datadrivendiscovery/common-primitives.git',
                ],
            },
            'installation': [{
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'd3m-common-primitives',
                'version': '2022.5.26',
            }],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.DATA_CONVERSION,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_TRANSFORMATION,
        },
    )

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        return base.CallResult(container.List(inputs, generate_metadata=True))
