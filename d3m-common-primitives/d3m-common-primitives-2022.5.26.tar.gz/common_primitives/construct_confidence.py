import os
import typing

import numpy as np
import pandas as pd

import d3m.metadata.base as metadata_module
from d3m import container, utils as d3m_utils
from d3m.metadata import hyperparams
import d3m.metadata.base as metadata_base
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult, ProbabilisticCompositionalityMixin
from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase

import common_primitives
from common_primitives.random_forest import RandomForestClassifierPrimitive

Inputs = container.DataFrame
Outputs = container.DataFrame


class Hyperparams(hyperparams.Hyperparams):
    primitive_learner = hyperparams.Hyperparameter[base.PrimitiveBase](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        default=RandomForestClassifierPrimitive,
        description='The primitive instance already trained that is going to be computing the log_likelihoods. \
        This primitive must implement log_likelihoods.'
    )


class ConstructConfidencePrimitive(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which takes as input a DataFrame, another Dataframe as a reference and a primitive that implements
    ProbabilisticCompositionalityMixin as hyperparameter to produce confidences for labels in Lincoln Labs predictions
    """

    __author__ = "JPL DARPA D3M Team, Diego Martinez <dmartinez05@tamu.edu>"
    metadata = metadata_module.PrimitiveMetadata({
        'id': '500c4f0c-a040-48a5-aa76-d6463ea7ea37',
        "version": common_primitives.__version__,
        "name": "Construct confidence",
        "source": {
            'name': common_primitives.__author__,
            'contact': 'mailto:dmartinez05@tamu.edu',
            'uris': [
                'https://gitlab.com/datadrivendiscovery/common-primitives/blob/master/common_primitives/construct_confidence.py',
                'https://gitlab.com/datadrivendiscovery/common-primitives.git',
            ],
        },
        "installation": [{
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package': 'd3m-common-primitives',
            'version': '2022.5.26',
        }],
        "python_path": "d3m.primitives.data_transformation.construct_confidence.Common",
        "algorithm_types": [metadata_base.PrimitiveAlgorithmType.DATA_CONVERSION],
        "primitive_family": metadata_base.PrimitiveFamily.DATA_TRANSFORMATION,
    })

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed)

        if not isinstance(self.hyperparams['primitive_learner'], ProbabilisticCompositionalityMixin):
            raise ValueError("Primitivie {primitive_name} does not implement ProbabilisticCompositionalityMixin".format(
                primitive_name=self.hyperparams['primitive_learner'].metadata.query().get('name')))

    def produce(self, *, inputs: Inputs, reference: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:  # type: ignore
        labels = []
        target_index_columns = []

        for i in range(inputs.metadata.query((metadata_base.ALL_ELEMENTS,))['dimension']['length']):
            column_metada = inputs.metadata.query((metadata_base.ALL_ELEMENTS, i,))
            if 'semantic_types' in column_metada and 'https://metadata.datadrivendiscovery.org/types/TrueTarget' in column_metada['semantic_types']:
                target_index_columns.append(i)
                if 'all_distinct_values' not in column_metada:
                    raise ValueError('Target Column {} does not contains "all_distinct_values"'.format(column_metada['name']))

                labels += list(column_metada['all_distinct_values'])

        if len(labels) == 0:
            raise ValueError("No labels were found")

        labels = list(sorted(set(labels)))
        n_samples = len(inputs)

        index_column_ = reference.metadata.get_index_columns()

        if index_column_:
            index_column = reference.iloc[:, index_column_]
        else:
            index_column = container.DataFrame(np.arange(n_samples))

        index_column = index_column.loc[index_column.index.repeat(len(labels))].reset_index(drop=True)

        # Repeat input rows as many times as labels and update the metadata.
        primitive_inputs = inputs.loc[inputs.index.repeat(len(labels))].reset_index(drop=True)
        primitive_inputs.metadata = inputs.metadata.update((), {'dimension': {'length': len(labels)}})

        # we need to remove the target columns from the inputs just in case.
        primitive_inputs.drop(primitive_inputs.columns[target_index_columns], axis=1, inplace=True)

        # Create a dataframe for the labels for the log_likelihood to be computed. For this we repeat the labels
        # according to the number of samples and update the metadata.
        input_labels = container.DataFrame(labels)
        input_labels = input_labels.append([input_labels] * (n_samples - 1)).reset_index(drop=True)
        input_labels.metadata = input_labels.metadata.generate(input_labels)
        input_labels.metadata = input_labels.metadata.add_semantic_type((metadata_base.ALL_ELEMENTS, 0), 'https://metadata.datadrivendiscovery.org/types/TrueTarget')

        # Compute the log_likelihood according to the primitive learner.
        log_likelihoods = self.hyperparams['primitive_learner'].log_likelihoods(inputs=primitive_inputs, outputs=input_labels).value
        log_likelihoods = log_likelihoods.apply(np.vectorize(np.exp))

        # Concatenate the indexes, the labels and the log_likelihoods, add the proper column names and update the metadata
        result = pd.concat((index_column, input_labels, log_likelihoods), axis=1)
        result = container.DataFrame(result.to_numpy(), generate_metadata=True)
        label_name = inputs.metadata.query((metadata_base.ALL_ELEMENTS, target_index_columns[0],))['name']
        result.columns = ['d3mIndex', label_name, 'confidence']

        # Update metadata
        result.metadata = result.metadata.update(
            (metadata_base.ALL_ELEMENTS, 0),
            {
                'name': 'd3mIndex',
                'semantic_types': [
                    'http://schema.org/Integer',
                    'https://metadata.datadrivendiscovery.org/types/PrimaryKey'
                ]
            }
        )

        result.metadata = result.metadata.update(
            (metadata_base.ALL_ELEMENTS, 1),
            {
                'name': label_name,
                'semantic_types': [
                    'https://metadata.datadrivendiscovery.org/types/Target'
                ]
            }
        )

        result.metadata = result.metadata.update(
            (metadata_base.ALL_ELEMENTS, 2),
            {
                'name': 'confidence',
                'semantic_types': [
                    'http://schema.org/Float',
                    'https://metadata.datadrivendiscovery.org/types/LogLikelihood'
                ]
            }
        )

        return CallResult(result)

    def multi_produce(self, *, produce_methods: typing.Sequence[str], inputs: Inputs, reference: Inputs, timeout: float = None, iterations: int = None) -> base.MultiCallResult:  # type: ignore
        return self._multi_produce(produce_methods=produce_methods, timeout=timeout, iterations=iterations, inputs=inputs, reference=reference)

    def fit_multi_produce(self, *, produce_methods: typing.Sequence[str], inputs: Inputs, reference: Inputs, timeout: float = None, iterations: int = None) -> base.MultiCallResult:  # type: ignore
        return self._fit_multi_produce(produce_methods=produce_methods, timeout=timeout, iterations=iterations,
                                       inputs=inputs, reference=reference)
