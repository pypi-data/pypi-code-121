import copy
import typing
import os

from d3m import container, utils as d3m_utils
from d3m.metadata import base as metadata_base, hyperparams
from d3m.primitive_interfaces import base, transformer

import common_primitives

__all__ = ('AddSemanticTypesPrimitive',)

Inputs = container.DataFrame
Outputs = container.DataFrame


class Hyperparams(hyperparams.Hyperparams):
    columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='A set of column indices of columns to add semantic types for.',
    )
    semantic_types = hyperparams.Set(
        elements=hyperparams.Hyperparameter[str](''),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='Semantic types to add for columns listed in "columns".',
    )


class AddSemanticTypesPrimitive(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which adds semantic types for columns in a DataFrame.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': 'd7e14b12-abeb-42d8-942f-bdb077b4fd37',
            'version': common_primitives.__version__,
            'name': "Add semantic types to columns",
            'python_path': 'd3m.primitives.data_transformation.add_semantic_types.Common',
            'source': {
                'name': common_primitives.__author__,
                'contact': 'mailto:mitar.commonprimitives@tnode.com',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/add_semantic_types.py',
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
        outputs = copy.copy(inputs)

        outputs.metadata = self._update_metadata(outputs.metadata)

        return base.CallResult(outputs)

    def _update_metadata(self, inputs_metadata: metadata_base.DataMetadata) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata

        for column_index in self.hyperparams['columns']:
            for semantic_type in self.hyperparams['semantic_types']:
                outputs_metadata = outputs_metadata.add_semantic_type((metadata_base.ALL_ELEMENTS, column_index), semantic_type)

        return outputs_metadata
