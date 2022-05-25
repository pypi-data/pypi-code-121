# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod
from ...core.space import Variable
import numpy as np
from functools import reduce


class DecisionVariable(Variable):
    """
    Represents the space of one decision variable

    Args:
        decisionvariable (Dict): Dict representing one decision variable. It may contain the following keys:
            name (str): name of the decision variable
            type (str): type of decision variable, among 'float','int' and 'categorical'
            bounds (list, optional): bounds between which the variable is defined (list with lower and upper value).
            size (int, optional): used when the decision variable is a list of parameters. Shape is the length of this list. If size = 1, the variable will be a list of one element.
            init (optional): initial value of the decision variable, may be an integer, float or a list of integers/floats
            values (list, optional): used when the decision variable type is 'categorical', list of possible values for the variable.
    """

    def __init__(self, decisionvariable):
        # Check that variable has a correct format
        if 'init' in decisionvariable:
            if 'size' in decisionvariable:
                if len(decisionvariable['init']) != decisionvariable['size']:
                    raise ValueError(
                        "In variable {}, the number of elements in 'init' should be equal to the size".format(
                            decisionvariable["name"]
                        )
                    )

        # Assign variable attributes
        if 'init' in decisionvariable:
            self.init = decisionvariable['init']
        else:
            self.init = None

        # Initialize from the parent Experiment class
        super().__init__(variable=decisionvariable)


class TransformedVariable(ABC):
    """
    Allows to transform values of one decision variable according to some transformation

    Args:
        decisionvariable (DecisionVariable): one decision variable.

    Attributes:
        name : name of the decision variable
        type : type of decision variable, among 'float','int' and 'categorical'
        bounds : bounds between which the variable is defined (list with lower and upper value).
        size : used when the decision variable is a list of parameters. size is the length of this list
        init : initial value of the decision variable, may be an integer, float or a list of integers/floats
        values : used when the decision variable type is 'categorical', list of values that will be tested during the parameter sweep
        transformed_dimension : dimension of the variable in the transformed space
    """

    def __init__(self, decisionvariable):
        self.name = decisionvariable.name
        self.type = decisionvariable.type
        self.size = decisionvariable.size
        self.init = decisionvariable.init
        self.bounds = decisionvariable.bounds
        self.values = decisionvariable.values
        self.dimension = decisionvariable.dimension
        self.transformed_dimension = self.dimension

    @abstractmethod
    def transform(self, reals):
        """
        Maps a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension) in the transformed space
        to a list of ParameterSets of length number_of_samples,
        with each ParameterSet containing as key the name of the decision variable,
        and as value the value (eventually a list) of the decision variable in the original space
        """
        pass

    @abstractmethod
    def inverse_transform(self, list_of_parametersets, deterministic=False):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with one parameter corresponding to the decision variable,
        to a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension)
        in the transformed space. May be non-deterministic.
        """
        pass

    def initial_value(self, deterministic=False):
        """
        Returns the initial value of the decision variable in the transformed space
        """
        if self.init is not None:
            transformed_input = self.inverse_transform(
                [{self.name: self.init}], deterministic=deterministic
            )
            return np.reshape(transformed_input, -1)
        else:
            return np.random.rand(self.transformed_dimension)

    def array_to_ParameterSet(self, array):
        """
        Maps a 2d array of shape
        (number_of_samples, dimension)
        to a list of ParameterSets of length number_of_samples,
        with each ParameterSet having as key the name of the decision variable,
        and as value a list of length size of the decision variable, or one element (if size is None)
        """
        array = array.tolist()
        if self.size is None:
            return [dict(zip([self.name], element)) for element in array]
        else:
            return [dict(zip([self.name], [element])) for element in array]

    def list_of_dict_to_array(self, list_of_dict):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with each ParameterSet having as key the name of the decision variable,
        and as value a list of length size of the decision variable, or one element (if dimension == 1)
        to a 2d array of shape (number_of_samples, transformed_dimension)
        """
        array = np.array([i[self.name] for i in list_of_dict])
        if len(array.shape) > 1:
            return array
        else:
            length = array.shape[0]
            return array.reshape(length, 1)


class IntegerTransformedVariable(TransformedVariable):
    """
    Allows to transform an integer variable to a real variable in [0,1]

    Args:
        decisionvariable (DecisionVariable): one decision variable.

    Attributes:
        name : name of the decision variable
        type : type of decision variable, among 'float','int' and 'categorical'
        bounds : bounds between which the variable is defined (list with lower and upper value).
        size : used when the decision variable is a list of parameters. size is the length of this list
        init : initial value of the decision variable, may be an integer, float or a list of integers/floats
        values : used when the decision variable type is 'categorical', list of values that will be tested during the parameter sweep
        transformed_dimension : dimension of the variable in the transformed space
    """

    def __init__(self, decisionvariable):
        super().__init__(decisionvariable)

    def _map_integer_array_to_real_array(self, integers):
        reals = (np.array(integers) - self.bounds[0] + 0.5) / (
            self.bounds[1] - self.bounds[0] + 1
        )
        return reals

    def _noisy_map_integer_array_to_real_array(self, integers):
        # Adds noise to the real array, while keeping the fact that the reals are mapped to the same integers
        reals = (
            np.array(integers)
            + np.random.random_sample(np.array(integers).shape)
            - 0.5
            - self.bounds[0]
            + 0.5
        ) / (self.bounds[1] - self.bounds[0] + 1)
        return reals

    def _map_real_array_to_integer_array(self, reals):
        # To map a uniform distribution on integers to a uniform distribution on reals by rounding
        # we have to enlarge the bounds to ensure an integer on the bounds corresponds to a segment [lower_bounds-0.5, lower_bounds+0.5]
        integers = np.round(
            (
                np.array(reals) * (self.bounds[1] - self.bounds[0] + 1)
                + self.bounds[0]
                - 0.5
            )
        )
        return integers.astype(int)

    def transform(self, reals):
        """
        Maps a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension) in the transformed space
        to a list of ParameterSets of length number_of_samples,
        with each ParameterSet containing as key the name of the decision variable,
        and as value the value (eventually a list) of the decision variable in the original space
        """
        integers = self._map_real_array_to_integer_array(reals)
        return self.array_to_ParameterSet(integers)

    def inverse_transform(self, list_of_parametersets, deterministic=False):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with one parameter corresponding to the decision variable,
        to a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension)
        in the transformed space. May be non-deterministic.
        """
        if deterministic:
            return self._map_integer_array_to_real_array(
                self.list_of_dict_to_array(list_of_parametersets)
            )
        else:
            return self._noisy_map_integer_array_to_real_array(
                self.list_of_dict_to_array(list_of_parametersets)
            )


class RealTransformedVariable(TransformedVariable):
    """
    Allows to transform a real variable to a real variable in [0,1]

    Args:
        decisionvariable (DecisionVariable): one decision variable.

    Attributes:
        name : name of the decision variable
        type : type of decision variable, among 'float','int' and 'categorical'
        bounds : bounds between which the variable is defined (list with lower and upper value).
        size : used when the decision variable is a list of parameters. size is the length of this list
        init : initial value of the decision variable, may be an integer, float or a list of integers/floats
        values : used when the decision variable type is 'categorical', list of values that will be tested during the parameter sweep
        transformed_dimension : dimension of the variable in the transformed space
    """

    def __init__(self, decisionvariable):
        super().__init__(decisionvariable)

    def _map_real_array_to_real_standard_array(self, reals):
        return (np.array(reals) - self.bounds[0]) / (self.bounds[1] - self.bounds[0])

    def _map_real_standard_array_to_real_array(self, reals):
        return np.array(reals) * (self.bounds[1] - self.bounds[0]) + self.bounds[0]

    def transform(self, reals):
        """
        Maps a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension) in the transformed space
        to a list of ParameterSets of length number_of_samples,
        with each ParameterSet containing as key the name of the decision variable,
        and as value the value (eventually a list) of the decision variable in the original space
        """
        reals = self._map_real_standard_array_to_real_array(reals)
        return self.array_to_ParameterSet(reals)

    def inverse_transform(self, list_of_parametersets, deterministic=False):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with one parameter corresponding to the decision variable,
        to a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension)
        in the transformed space. May be non-deterministic.
        """
        return self._map_real_array_to_real_standard_array(
            self.list_of_dict_to_array(list_of_parametersets)
        )


class CategoricalTransformedVariable(TransformedVariable):
    """
    Allows to transform a categorical variable in a real standard variable

    Args:
        decisionvariable (DecisionVariable): one decision variable.

    Attributes:
        name : name of the decision variable
        type : type of decision variable, among 'float','int' and 'categorical'
        bounds : bounds between which the variable is defined (list with lower and upper value).
        size : used when the decision variable is a list of parameters. size is the length of this list
        init : initial value of the decision variable, may be an integer, float or a list of integers/floats
        values : used when the decision variable type is 'categorical', list of values that will be tested during the parameter sweep
        dimension : dimension of the variable in the transformed space
    """

    def __init__(self, decisionvariable):
        super().__init__(decisionvariable)
        self.categoricaldimension = len(self.values)
        self.transformed_dimension = self.categoricaldimension * self.dimension
        self.map_category_to_int = {j: i for i, j in enumerate(self.values)}

    def _map_real_standard_array_to_categorical_array(self, reals):
        A = reals.reshape((reals.shape[0], self.dimension, self.categoricaldimension))
        A = np.argmax(A, axis=2).astype(int)
        return np.array(self.values, dtype=object)[A]

    def _map_categorical_array_to_real_standard_array(self, array):
        """Uses one-hot encoding"""
        vectorized_category_to_int = np.vectorize(self.map_category_to_int.__getitem__)
        return np.eye(self.categoricaldimension, dtype=float)[
            np.asarray(vectorized_category_to_int(array))
        ].reshape(array.shape[0], self.transformed_dimension)

    def _noisy_map_categorical_array_to_real_standard_array(self, array):
        """
        Maps each category to a random real vector such that the element corresponding
        to the category integer in map_category_to_int is maximal
        """
        new_array = np.zeros(
            (array.shape[0], array.shape[1] * self.categoricaldimension)
        )
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                u = np.random.rand(self.categoricaldimension)
                new_array[
                    i,
                    j * self.categoricaldimension : (j + 1) * self.categoricaldimension,
                ] = np.roll(u, self.map_category_to_int[array[i, j]] - np.argmax(u))
        return new_array

    def transform(self, reals):
        """
        Maps a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension) in the transformed space
        to a list of ParameterSets of length number_of_samples,
        with each ParameterSet containing as key the name of the decision variable,
        and as value the value (eventually a list) of the decision variable in the original space
        """
        categories = self._map_real_standard_array_to_categorical_array(reals)
        return self.array_to_ParameterSet(categories)

    def inverse_transform(self, list_of_parametersets, deterministic=False):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with one parameter corresponding to the decision variable,
        to a numpy array of floating point numbers of shape
        (number_of_samples, transformed_dimension)
        in the transformed space. May be non-deterministic.
        """
        if deterministic:
            return self._map_categorical_array_to_real_standard_array(
                self.list_of_dict_to_array(list_of_parametersets)
            )
        else:
            return self._noisy_map_categorical_array_to_real_standard_array(
                self.list_of_dict_to_array(list_of_parametersets)
            )

    def list_of_dict_to_array(self, list_of_dict):
        """
        Maps a list of ParameterSets of length number_of_samples,
        with each ParameterSet having as key the name of the decision variable,
        and as value a list of length size of the decision variable, or one element (if dimension == 1)
        to a 2d array of shape (number_of_samples, transformed_dimension), with type object
        """
        array = np.array([i[self.name] for i in list_of_dict], dtype=object)
        if len(array.shape) > 1:
            return array
        else:
            length = array.shape[0]
            return array.reshape(length, 1)


class StandardizedSpace:
    """
    Maps a Space to a standardized space of floating point numbers in the unit hypercube (bounded) or R^N (unbounded).

    Args:
        space (Space): Original Space
        bounded (bool): Whether the standardized space is bounded (unit hypercube) or not (R^N). Defaults to True. Be careful with unbounded spaces, infinities are not handled.

    Attributes:
        dimension (int): dimension of the standardized space
        list_of_variables (list of DecisionVariable): list of Variable in the standardized space (in practice contains only one variable)
        list_of_transformed_variables (list of TransformedVariable):
            list of TransformedVariable in charge of the transformation to the standardized space for each original DecisionVariable
    """

    def __init__(self, space, bounded=True):
        self.space = space
        self.dimension = 0  # Dimension of the standardized space
        self.list_of_transformed_variables = []
        self.bounded = bounded

        # Transform each variable
        for variable in self.space.list_of_variables:
            if variable.type == 'float':
                transformed_variable = RealTransformedVariable(variable)
            elif variable.type == 'int':
                transformed_variable = IntegerTransformedVariable(variable)
            elif variable.type == 'categorical':
                transformed_variable = CategoricalTransformedVariable(variable)
            else:  # pragma: no cover
                raise ValueError("Unknown variable type {}".format(variable.type))
            self.list_of_transformed_variables.append(transformed_variable)
        self.map_name_to_transformed_variable = {
            i.name: i for i in self.list_of_transformed_variables
        }

        # Compute the dimension of the standardized space
        self.list_of_dimensions = []
        for variable in self.list_of_transformed_variables:
            self.list_of_dimensions.append(variable.transformed_dimension)
        self.dimension = sum(self.list_of_dimensions)

        # Compute the slices in an array corresponding to each variable
        self.list_of_slices = []
        first_dimension = 0
        for dimension in self.list_of_dimensions:
            self.list_of_slices.append((first_dimension, first_dimension + dimension))
            first_dimension += dimension

        # Create decision variable in the original format
        standard_variable = DecisionVariable(
            {
                'name': 'StandardRealVariable',
                'type': 'float',
                'size': self.dimension,
                'bounds': [0, 1],
                'init': self.initial_value(),
            }
        )
        self.list_of_variables = [standard_variable]

    def map_to_standardized_space(self, list_of_parametersets, deterministic=False):
        """Maps a list of ParameterSets in the original space to a numpy array in the standardized space

        Args:
            list_of_parametersets (ParameterSet or list of ParameterSet): samples of parameters in the original space
            deterministic (bool, optional): Whether the mapping is deterministic or not. Defaults to False.

        Returns:
            numpy array: Array of floating point numbers of shape (number of samples x dimension)
                (or simply dimension if there is only one sample) in the standardized space
        """
        islist = True
        if not isinstance(list_of_parametersets, list):
            islist = False
            list_of_parametersets = [list_of_parametersets]
        arrays = []
        for name in list_of_parametersets[0].keys():
            arrays.append(
                self.map_name_to_transformed_variable[name].inverse_transform(
                    list_of_parametersets, deterministic=deterministic
                )
            )
        resulting_array = np.concatenate(arrays, axis=1)
        if not islist:
            resulting_array = np.reshape(resulting_array, -1)

        if not self.bounded:
            resulting_array = np.tan((resulting_array * np.pi) - np.pi / 2)
        return resulting_array

    def map_to_original_space(self, array):
        """Maps a numpy array in the standardized space to a list of ParameterSets in the original space

        Args:
            array (numpy array): : Array of floating point numbers of shape (number of samples x dimension)
                (or simply dimension if there is only one sample) in the standardized space

        Returns:
            list of ParameterSet or ParameterSet: corresponding samples in the original space
        """

        if not self.bounded:
            array = np.arctan(array) / np.pi + 1 / 2

        is2d = True
        if len(array.shape) == 1:
            is2d = False
            array = array.reshape(1, array.shape[0])
        transformed_lists = []
        for transformed_variable, slice in zip(
            self.list_of_transformed_variables, self.list_of_slices
        ):
            transformed_lists.append(
                transformed_variable.transform(array[:, slice[0] : slice[1]])
            )
        parameterset = [
            reduce(lambda a, b: {**a, **b}, k) for k in zip(*transformed_lists)
        ]
        if not is2d:
            parameterset = parameterset[0]
        return parameterset

    def initial_value(self, deterministic=False):
        """
        Return the initial numpy array in the standardized space.
        If an initial value is provided in the original space, this value will be mapped to the standardized space,
        otherwise the value is chosen randomly.

        Args:
            deterministic (bool, optional): Whether the mapping is deterministic or not. Defaults to False.
        Returns:
            numpy array: Array of floating point numbers of shape (dimension)
        """
        arrays = []
        for name, transformed_variable in self.map_name_to_transformed_variable.items():
            arrays.append(transformed_variable.initial_value(deterministic))

        resulting_array = np.concatenate(arrays)
        if not self.bounded:
            resulting_array = np.tan((resulting_array * np.pi) - np.pi / 2)
        return resulting_array
