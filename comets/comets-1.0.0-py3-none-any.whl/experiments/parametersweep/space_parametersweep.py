# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.space import Variable


class Variable(Variable):
    """
    Represents the space of one variable of the parameter sweep

    Args:
        decisionvariable (Dict): Dict representing one decision variable. It may contain the following keys:
            name (str): name of the decision variable
            type (str): type of decision variable, among 'float','int' and 'categorical'
            bounds (list, optional): bounds between which the variable is defined (list with lower and upper value).
            number_of_points (int, optional): number of points used on this variable, to perform a parameter sweep of the space
            values (list, optional): used when the decision variable type is 'categorical', list of values that will be tested during the parameter sweep
            size (int, optional): used when the variable is a list of parameters. Size is the length of this list. If size = 1, the variable will be a list of one element.
    """

    def __init__(self, variable):
        # Check that variable has a correct format
        if 'number_of_points' in variable:
            if not isinstance(variable['number_of_points'], int):
                raise ValueError(
                    "In variable {}, the number of points should be an integer".format(
                        variable["name"]
                    )
                )
            if variable['number_of_points'] < 1:
                raise ValueError(
                    'In variable {}, the number of points should be positive'.format(
                        variable["name"]
                    )
                )
        if 'bounds' in variable:
            if 'number_of_points' not in variable:
                raise ValueError(
                    'In variable {}, the number of points should be given'.format(
                        variable["name"]
                    )
                )

        # Assign variable attributes
        if 'number_of_points' in variable:
            self.number_of_points = variable['number_of_points']

        # Initialize from the parent Experiment class
        super().__init__(variable=variable)
