import logging
import time
from collections import defaultdict

import pandas

from kolibri.core import modules
from kolibri.core.component import ComponentMetaclass
import numpy as np

LOGGER = logging.getLogger(__name__)


def validate_arguments(pipeline, context, allow_empty_pipeline=False):
    # type: (List[Component], Dict[Text, Any], bool) -> None
    """Validates a pipeline before it is run. Ensures, that all
    arguments are present to train the pipeline."""

    # Ensure the pipeline is not empty
    if not allow_empty_pipeline and len(pipeline) == 0:
        raise ValueError("Can not train an empty pipeline. "
                         "Make sure to specify a proper pipeline in "
                         "the configuration using the `pipeline` key." +
                         "The `backend` configuration key is "
                         "NOT supported anymore.")

    provided_properties = set(context.keys())

    for component in pipeline:
        for r in component.requires:
            if r not in provided_properties:
                raise Exception("Failed to validate at component "
                                "'{}'. Missing property: '{}'"
                                "".format(component.my_name, r))
        provided_properties.update(component.provides)

class Pipeline(object, metaclass=ComponentMetaclass):
    """Pipeline Class.

    The **Pipeline** class represents a Machine Learning Pipeline, which
    is an ordered collection of Machine Learning tools or Primitives,
    represented by **Component instances**, that will be executed
    sequentially in order to produce results.

    The Pipeline has two working modes or phases: **fitting** and
    **predicting**.

    During the **fitting** phase, each Component instance, or **component** will be
    fitted and immediately after used to produce results on the same
    fitting data.
    This results will be then passed to the next componenet of the sequence
    as its fitting data, and this process will be repeated until the last
    component is fitted.

    During the **predicting** phase, each component will be used to produce results
    on the output of the previous one, until the last one has produce its
    results, which will be returned as the prediction of the pipelines.
    """

    def _get_tunable_hyperparameters(self):
        """Get the tunable hyperperparameters from all the blocks in this pipelines."""
        tunable = {}
        for step_name, step in self.steps.items():
            tunable[step_name] = step.get_tunable_hyperparameters()

        return tunable

    def _validate_components(self):
        if self.steps is None:
            return

        names, components = self.steps.keys(), self.steps.values()

        self.transformers=[]
        self.estimator=None
        for component in components:
            if component.component_type=="estimator":
                self.estimator=component
            else:
                self.transformers.append(component)

        self.active = True

        for t in self.transformers:
            if t is None:
                continue
            else:
                if not (hasattr(t, "fit") or hasattr(t, "fit_transform")) or not hasattr(t, "transform"):
                    self.active = False
                    raise TypeError("All intermediate steps, including an evaluator, "
                                    "should implement fit and transform.")

    def __init__(self, steps=None, parameters={}):

        self.steps= {}
        if steps is not None:
            for step in steps:
                self.steps[step[0]]=step[1]


        self._validate_components()


        self.verbose =  parameters["verbose"] if "verbose" in parameters else False

        super(Pipeline, self).__init__()

    def add_steps(self, steps):
        if self.steps is None:
            self.steps={}
        for name, component in steps:
            if name not in self.steps:
                self.steps[name]=component
            else:
                raise ValueError("duplicate Compoenent name in the pipeline")

        self._validate_components()
    @staticmethod
    def from_configs(params):
        """Transform the passed names of the pipeline components into classes"""

        steps = []
        # Transform the passed names of the pipeline components into classes
        for component_name, param_val in params.items():
            component = modules.create_component_by_name(
                component_name, param_val)
            steps.append((component_name, component))

        return Pipeline(steps)
    @staticmethod
    def _flatten_dict(hyperparameters):
        return {
            (block, name): value
            for block, block_hyperparameters in hyperparameters.items()
            for name, value in block_hyperparameters.items()
        }

    def get_tunable_hyperparameters(self, flat=False):
        """Get the tunable hyperparamters of each block.

        Args:
            flat (bool): If True, return a flattened dictionary where each key
                is a two elements tuple containing the name of the block as the first
                element and the name of the hyperparameter as the second one.
                If False (default), return a dictionary where each key is the name of
                a block and each value is a dictionary containing the complete
                hyperparameter specification of that block.

        Returns:
            dict:
                A dictionary containing the block names as keys and
                the block tunable configs dictionary as values.
        """
        tunables = self._tunable_hyperparameters.copy()
        if flat:
            tunables = self._flatten_dict(tunables)

        return tunables

    @classmethod
    def _sanitize_value(cls, value):
        """Convert numpy values to their python primitive type equivalent.

        If a value is a dict, recursively sanitize its values.

        Args:
            value:
                value to sanitize.

        Returns:
            sanitized value.
        """
        if isinstance(value, dict):
            return {
                key: cls._sanitize_value(value)
                for key, value in value.items()
            }
        if isinstance(value, np.integer):
            return int(value)
        elif isinstance(value, np.floating):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif isinstance(value, np.bool_):
            return bool(value)
        elif value == 'None':
            return None

        return value

    @classmethod
    def _sanitize(cls, hyperparameters):
        """Convert tuple hyperparameter keys to nested dicts.

        Also convert numpy types to primary python types.

        The input configs dict can specify them in two formats:

        One is the native MLBlocks format, where each key is the name of a block and each value
        is a dict containing a complete hyperparameter specification for that block::

            {
                'block_name': {
                    'hyperparameter_name': 'hyperparameter_value',
                    ...
                },
                ...
            }

        The other one is an alternative format where each key is a two element tuple containing
        the name of the block as the first element and the name of the hyperparameter as the
        second one::

            {
                ('block_name', 'hyperparameter_name'): 'hyperparameter_value',
                ...
            }


        Args:
            hyperparaeters (dict):
                configs dict to sanitize.

        Returns:
            dict:
                Sanitized dict.
        """
        params_tree = defaultdict(dict)
        for key, value in hyperparameters.items():
            value = cls._sanitize_value(value)
            if isinstance(key, tuple):
                block, hyperparameter = key
                params_tree[block][hyperparameter] = value
            else:
                params_tree[key] = value

        return params_tree
    @property
    def parameters(self):
        """Get the current hyperparamters of each block.

        Args:
            flat (bool): If True, return a flattened dictionary where each key
                is a two elements tuple containing the name of the block as the first
                element and the name of the hyperparameter as the second one.
                If False (default), return a dictionary where each key is the name of
                a block and each value is a dictionary containing the complete
                hyperparameter specification of that block.

        Returns:
            dict:
                A dictionary containing the block names as keys and
                the current block configs dictionary as values.
        """
        hyperparameters = dict()
        for block_name, block in self.steps.items():
            hyperparameters[block_name] = block.get_hyperparameters()

        return hyperparameters

    def set_hyperparameters(self, hyperparameters):
        """Set new hyperparameter values for some blocks.

        Args:
            hyperparameters (dict):
                A dictionary containing the block names as keys and the new configs
                dictionary as values.
        """
        hyperparameters = self._sanitize(hyperparameters)
        for block_name, block_hyperparams in hyperparameters.items():
            self.steps[block_name].set_hyperparameters(block_hyperparams)

    def fit(self, X, y, X_val=None, y_val=None):

        """ fit
        Sequentially fit and transformer texts in all but last step, then fit
        the model_type in last step.
        Parameters
        ----------
        X: numpy.ndarray of shape (n_samples, n_features)
            The texts upon which the transforms/estimator will create their
            model_type.
        y: An array_like object of length_train n_samples
            Contains the true class y_values for all the samples in data.
        Returns
        -------
        Pipeline
            self
        """

        Xt, y, Xt_val, y_val=self.fit_transformers(X, y, X_val,y_val)

        self.fit_estimator(Xt, y, Xt_val, y_val)

        return self

    def fit_transformers(self, X, y, X_val=None, y_val=None):

        Xt = X
        Xt_val = X_val

        for transformer in self.transformers:
            start=time.time()
            if transformer is None:
                pass
            if hasattr(transformer, "fit_transform"):
                Xt = transformer.fit_transform(Xt, y)
                if Xt_val is not None:
                    Xt_val = transformer.fit_transform(Xt_val, y_val)
            else:
                Xt = transformer.fit(Xt, y).transform(Xt)
                if Xt_val is not None:
                    Xt_val = transformer.transform(Xt_val)
            print('fitted component ' + transformer.name + '. Elapsed time ' + str(time.time() - start))

        return Xt, y, Xt_val, y_val

    def fit_estimator(self, Xt, y, Xt_val=None, y_val=None):
        if self.estimator is not None:
            print('fitting estimator '+self.estimator.name)
            try:
                self.estimator.fit(Xt, y, Xt_val, y_val)
            except:
                self.estimator.fit(Xt, y)

    def predict(self, X):
        """ predict
        Sequentially applies all transforms and then predict with last step.
        Parameters
        ----------
        X: numpy.ndarray of shape (n_samples, n_features)
            All the samples we want to predict the label for.
        Returns
        -------
        list
            The predicted class label for all the samples in data.
        """

        if isinstance(X, np.ndarray):
            X=X.tolist()
        if isinstance(X, list) or isinstance(X, pandas.DataFrame):
            Xt = X
        else:
            Xt=[X]

        for transform in self.transformers:
            if transform is not None:
                Xt = transform.transform(Xt)
        if self.estimator is not None:
            return self.estimator.predict(Xt)
        else:
            return Xt

    def get_info(self):
        info = "Pipeline:\n["
        names, estimators = zip(*self.steps)
        learner = estimators[-1]
        transforms = estimators[:-1]
        i = 0
        for t in transforms:
            try:
                if t.get_info() is not None:
                    info += t.get_info()
                    info += "\n"
                else:
                    info += 'Transform: no info available'
            except NotImplementedError:
                info += 'Transform: no info available'
            i += 1

        if learner is not None:
            try:
                if hasattr(learner, 'get_info'):
                    info += learner.get_info()
                else:
                    info += 'Learner: no info available'
            except NotImplementedError:
                info += 'Learner: no info available'
        info += "]"
        return info
