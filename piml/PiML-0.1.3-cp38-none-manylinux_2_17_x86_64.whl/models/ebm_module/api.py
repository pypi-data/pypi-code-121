# Copyright (c) 2019 Microsoft Corporation
# Distributed under the MIT software license

from abc import ABC, abstractmethod


# TODO v.3 PK Possibly rename explainer types to (blackbox, glassbox, greybox)
class ExplainerMixin(ABC):
    """ An object that computes explanations.
        This is a contract required for InterpretML.
    Attributes:
        available_explanations: A list of strings subsetting the following
            - "perf", "data", "local", "global".
        explainer_type: A string that is one of the following
            - "blackbox", "model", "specific", "data", "perf".
    """

    @property
    @abstractmethod
    def available_explanations(self):
        pass  # pragma: no cover

    @property
    @abstractmethod
    def explainer_type(self):
        pass  # pragma: no cover


class ExplanationMixin(ABC):
    """ The result of calling explain_* from an Explainer. Responsible for providing data and/or visualization.
        This is a contract required for InterpretML.
    Attributes:
        explanation_type: A string that is one of the
            explainer's available explanations.
            Should be one of "perf", "data", "local", "global".
        name: A string that denotes the name of the explanation
            for display purposes.
        selector: An optional dataframe that describes the data.
            Each row of the dataframe corresponds with a respective data item.
    """

    @property
    @abstractmethod
    def explanation_type(self):
        pass  # pragma: no cover

    @abstractmethod
    def data(self, key=None):
        """ Provides specific explanation data.
        Args:
            key: A number/string that references a specific data item.
        Returns:
            A serializable dictionary.
        """
        pass  # pragma: no cover

    name = "An Explanation"
    selector = None


class FeatureValueExplanation(ExplanationMixin):
    """ Handles explanations that can be visualized as horizontal bar graphs.
        Usually these are feature-value pairs being represented.
    """

    explanation_type = None

    def __init__(
        self,
        explanation_type,
        internal_obj,
        feature_names=None,
        feature_types=None,
        name=None,
        selector=None,
    ):
        """ Initializes class.
        Args:
            explanation_type:  Type of explanation.
            internal_obj: A jsonable object that backs the explanation.
            feature_names: List of feature names.
            feature_types: List of feature types.
            name: User-defined name of explanation.
            selector: A dataframe whose indices correspond to explanation entries.
        """
        self.explanation_type = explanation_type
        self._internal_obj = internal_obj
        self.feature_names = feature_names
        self.feature_types = feature_types
        self.name = name
        self.selector = selector

    def data(self, key=None):
        """ Provides specific explanation data.
        Args:
            key: A number/string that references a specific data item.
        Returns:
            A serializable dictionary.
        """
        # NOTE: When a non-default provider is used, it's represented as ("provider", key).
        if isinstance(key, tuple) and len(key) == 2:
            _, key = key

        # NOTE: Currently returns full internal object, open to change.
        if key == -1:
            return self._internal_obj

        if key is None:
            return self._internal_obj["overall"]

        if self._internal_obj["specific"] is None:  # pragma: no cover
            return None
        return self._internal_obj["specific"][key]
