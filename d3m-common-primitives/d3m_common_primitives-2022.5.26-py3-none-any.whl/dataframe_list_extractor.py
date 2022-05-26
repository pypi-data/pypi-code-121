import os

from d3m import container, utils as d3m_utils
from d3m.metadata import base as metadata_base, hyperparams
from d3m.primitive_interfaces import base, transformer

import common_primitives

Inputs = container.List
Outputs = container.DataFrame


class Hyperparams(hyperparams.Hyperparams):
    dataframe_to_extract = hyperparams.Bounded[int](
        lower=0,
        upper=None,
        default=0,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='Index of the dataframe to extract from the list'
    )


class DataframeListExtractorPrimitive(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which extracts a Dataframe from a list of Dataframes byu index.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '9fe84601-a3d7-4881-86b2-44fecd42b296',
            'version': common_primitives.__version__,
            'name': 'Select dataframe from list of dataframes',
            'python_path': 'd3m.primitives.data_transformation.dataframe_list_extractor.Common',
            'source': {
                'name': common_primitives.__author__,
                'contact': 'mailto:dmartinez05@tamu.edu',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/dataframe_list_extractor.py',
                    'https://gitlab.com/datadrivendiscovery/common-primitives.git',
                ],
            },
            'installation': [{
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'd3m-common-primitives',
                'version': '2022.5.26',
            }],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.ARRAY_SLICING,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_TRANSFORMATION,
        },
    )

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        # check index_to_extract
        if self.hyperparams['dataframe_to_extract'] >= len(inputs):
            raise ValueError('dataframe_to_extract {} index is larger that indexes on input list {}'.format(self.hyperparams['dataframe_to_extract'], len(inputs)-1))

        # check metadata
        new_dataframe = inputs[self.hyperparams['dataframe_to_extract']].copy()
        return base.CallResult(new_dataframe)
