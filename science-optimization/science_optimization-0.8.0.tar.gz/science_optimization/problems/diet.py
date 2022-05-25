"""
class that creates a diet problem
"""
import numpy as np
from science_optimization.builder import BuilderOptimizationProblem
from science_optimization.builder import Objective
from science_optimization.builder import Constraint
from science_optimization.builder import Variable
from science_optimization.function import FunctionsComposite
from science_optimization.function import LinearFunction


class Diet(BuilderOptimizationProblem):
    """Concrete builder implementation.

    This class builds a diet problem.

    """

    # class attributes
    _food = None
    _food_limits = None
    _cost = None
    _nutrients = None
    _demand = None

    def __init__(self, food, food_limits, cost, nutrient, demand):
        """ Constructor of Diet optimization problem.

        Args:
            food: food names
            food_limits: servings limit
            cost: cost per serving
            nutrient: nutrients on each food
            demand: nutrients demand
        """
        self.food = food
        self.food_limits = food_limits
        self.cost = cost
        self.nutrients = nutrient
        self.demand = demand

    # attributes interface
    @property
    def food(self):
        return self._food

    @property
    def food_limits(self):
        return self._food_limits

    @property
    def cost(self):
        return self._cost

    @property
    def nutrients(self):
        return self._nutrients

    @property
    def demand(self):
        return self._demand

    # setters
    @food.setter
    def food(self, food):
        self._food = food

    @food_limits.setter
    def food_limits(self, food_limits):
        self._food_limits = food_limits

    @cost.setter
    def cost(self, cost):
        self._cost = cost

    @nutrients.setter
    def nutrients(self, nutrients):
        self._nutrients = nutrients

    @demand.setter
    def demand(self, demand):
        self._demand = demand

    # methods
    def build_variables(self):

        # add variables
        variables = Variable(x_min=self.food_limits[:, 0].reshape(-1, 1),
                             x_max=self.food_limits[:, 1].reshape(-1, 1))

        return variables

    def build_objectives(self):

        # add objective
        obj_fun = FunctionsComposite()
        obj_fun.add(f=LinearFunction(c=1.*np.array(self.cost).reshape(-1, 1)))
        objective = Objective(objective=obj_fun)

        return objective

    def build_constraints(self):

        # parameters
        c = np.vstack((np.array(self.nutrients), -1.0 * np.array(self.nutrients)))
        d = np.vstack((-1.0 * np.array(self.demand)[:, 1].reshape((-1, 1)), np.array(self.demand)[:, 0].reshape((-1, 1))))

        # add constraint
        ineq_cons = FunctionsComposite()
        for aux in range(c.shape[0]):
            ineq_cons.add(f=LinearFunction(c=c[aux, :].reshape((-1, 1)), d=d[aux]))

        constraints = Constraint(ineq_cons=ineq_cons)

        return constraints
