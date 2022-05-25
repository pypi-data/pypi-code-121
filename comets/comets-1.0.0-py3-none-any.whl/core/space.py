# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from comets.utilities import utilities

VARIABLE_TYPES = [
    'float',
    'int',
    'categorical',
]


class Variable:
    """
    Represents the space of one variable

    Args:
        variable (Dict): Dict representing one variable. It may contain the following keys:
            name (str): name of the variable
            type (str): type of variable, among 'float','int' and 'categorical'
            bounds (list, optional): bounds between which the variable is defined (list with lower and upper value).
            size (int, optional): used when the decision variable is a list of parameters. Shape is the length of this list. If size = 1, the variable will be a list of one element.
            values (list, optional): used when the variable type is 'categorical', list of possible values for the variable.
    """

    def __init__(self, variable):
        # Check that variable has a correct format
        if 'name' not in variable:
            raise ValueError("A variable should have a name")
        if 'type' not in variable:
            raise ValueError("Variable {} should have a type".format(variable["name"]))
        if variable['type'] not in VARIABLE_TYPES:
            raise ValueError("Variable type should be in {}".format(VARIABLE_TYPES))
        if variable['type'] == 'categorical':
            if 'values' not in variable:
                raise ValueError(
                    "Categorial variable {} requires a list of values".format(
                        variable["name"]
                    )
                )
            else:
                if not isinstance(variable['values'], list):
                    raise ValueError(
                        "Values of categorial variable {} should be a list".format(
                            variable["name"]
                        )
                    )
        else:
            # All other variable types are numerical and should have bounds
            if 'bounds' not in variable:
                raise ValueError(
                    "Numerical variable {} should have bounds".format(variable["name"])
                )
        utilities.check_size(variable)

        # Assign variable attributes
        self.name = variable['name']
        self.type = variable['type']
        if 'bounds' in variable:
            self.bounds = variable['bounds']
        else:
            self.bounds = None
        if 'size' in variable:
            self.size = variable['size']
            self.dimension = self.size
        else:
            self.size = None
            self.dimension = 1
        if 'values' in variable:
            self.values = variable['values']
        else:
            self.values = None


class Space:
    """
    Space of decision variables

    Args:
        variables (list): list of Dict, each Dict representing one variable

    Attributes:
        list_of_variables (list): list of Variable
    """

    def __init__(self, variables, variable_type):
        self.list_of_variables = [variable_type(p) for p in variables]
        self.dimension = self.get_dimension()

    def get_dimension(self):
        dimension = 0
        for elements in self.list_of_variables:
            dimension += elements.dimension
        return dimension

    def is_1d(self):
        if self.dimension == 1:
            return True
        else:
            return False
