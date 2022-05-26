import os.path
import typing

from d3m import container, exceptions, utils as d3m_utils
from d3m.metadata import base as metadata_base, hyperparams as hyperparams_module, params
from d3m.primitive_interfaces import base, unsupervised_learning

import common_primitives


Inputs = container.DataFrame
Outputs = container.DataFrame


class Params(params.Params):
    _fitted: bool
    _indexes: typing.List[int]
    _metadata: typing.Optional[typing.Any]


class Hyperparams(hyperparams_module.Hyperparams):
    columns = hyperparams_module.Set(
        elements=hyperparams_module.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='A set of column indices of columns to compute unique values.',
    )


class ComputeUniqueValuesPrimitive(unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
    A primitive that adds the field all_distinct_values to the metadata of
    the input dataframe for any given indexes or for the target columns.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': 'dd580c45-9fbe-493d-ac79-6e9f706a3619',
            'version': common_primitives.__version__,
            'name': "Add all_distinct_values to the metadata of the input Dataframe",
            'python_path': 'd3m.primitives.operator.compute_unique_values.Common',
            'source': {
                'name': common_primitives.__author__,
                'contact': 'mailto:dmartinez05@tamu.edu',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/compute_unique_values.py',
                    'https://gitlab.com/datadrivendiscovery/common-primitives.git',
                ],
            },
            'installation': [{
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'd3m-common-primitives',
                'version': '2022.5.26',
            }],
            'algorithm_types': [metadata_base.PrimitiveAlgorithmType.DATA_NORMALIZATION],
            'primitive_family': metadata_base.PrimitiveFamily.OPERATOR,
        },
    )

    _training_inputs: typing.Optional[Inputs]
    _fitted: bool
    _indexes: typing.List
    _metadata: typing.Any

    def __init__(self, *, hyperparams: Hyperparams) -> None:
        super().__init__(hyperparams=hyperparams)

        self._training_inputs = None
        self._fitted = False
        self._metadata = None
        self._indexes = list(self.hyperparams['columns'])

    def set_training_data(self, *, inputs: Inputs) -> None:  # type: ignore
        self._training_inputs = inputs
        self._fitted = False

    def fit(self, *, timeout: float = None, iterations: int = None) -> base.CallResult[None]:
        if self._training_inputs is None:
            raise exceptions.InvalidStateError("Missing training data.")

        # if no columns are provided, then we compute unique values in targets.
        if not self._indexes:
            for i in range(len(self._training_inputs.columns)):
                if 'https://metadata.datadrivendiscovery.org/types/TrueTarget' in \
                        self._training_inputs.metadata.query((metadata_base.ALL_ELEMENTS, i))['semantic_types']:
                    self._indexes.append(i)

        new_metadata = self._training_inputs.metadata

        # Check for columns with index in _indexes; get the unique values and store them on the metadata
        for i in self._indexes:
            unique_targets = list(sorted(set(self._training_inputs.iloc[:, i].unique().tolist())))
            new_metadata = new_metadata.update((metadata_base.ALL_ELEMENTS, i,), {'all_distinct_values': unique_targets, })

        # Store the metadata and delete the training inputs
        self._metadata = new_metadata
        self._training_inputs = None
        self._fitted = True

        return base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        if not self._fitted:
            raise exceptions.PrimitiveNotFittedError("Primitive not fitted.")

        outputs = inputs.copy()
        for i in self._indexes:
            outputs.metadata = outputs.metadata.update((metadata_base.ALL_ELEMENTS, i,), self._metadata.query((metadata_base.ALL_ELEMENTS, i)))

        return base.CallResult(outputs)

    def get_params(self) -> Params:
        return Params(_fitted=self._fitted, _indexes=self._indexes, _metadata=self._metadata)

    def set_params(self, *, params: Params) -> None:
        self._fitted = params['_fitted']
        self._indexes = params['_indexes']
        self._metadata = params['_metadata']
