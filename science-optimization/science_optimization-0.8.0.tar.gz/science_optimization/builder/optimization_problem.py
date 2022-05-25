"""
Optimization problem class
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D     # DO NOT REMOVE

from science_optimization.solvers import OptimizationResults

from .objective import Objective
from .constraint import Constraint
from .variable import Variable
from .builder_optimization_problem import BuilderOptimizationProblem
from science_optimization.function import QuadraticFunction
from science_optimization.function import LinearFunction


class OptimizationProblem:
    """Optimization problem class.

    Canonical form:
        minimize f(x)
        s.t.     g(x) <= 0
                 h(x) = 0

    An optimization problem is assembled by the Model class from parts
    made by Builder. Both these classes have influence on the resulting
    object.

    """

    # class attributes
    _objective = None
    _constraints = None
    _variables = None
    _results_ = None

    def __init__(self, builder: BuilderOptimizationProblem):
        """ Constructor of an optimization problem.

        Args:
             builder: (BuilderOptimizationProblem) class Builder instance
        """

        # check builder instance
        if not isinstance(builder, BuilderOptimizationProblem):
            raise Exception('Not a BuilderOptimizationProblem instance!')

        # builder problem
        self._build_problem(builder)

    def __call__(self, x):
        """ Callable of optimization problem.

        Args:
            x: (np.ndarray) (n x 1) evaluation point.

        Returns:
            f : (np.ndarray) (o  x 1) objectives evaluation, where o is the number of objectives.
            g : (np.ndarray) (ni x 1) inequalities constraints evaluation, where ni is the number of inequalities.
            h : (np.ndarray) (ne x 1) equalities constraints evaluation, where ne is the number of equalities.
            df: (np.ndarray) (n x o) objectives gradient evaluation.
            dg: (np.ndarray) (n x ni) inequalities gradient evaluation.
            dh: (np.ndarray) (n x ne) equalities gradient evaluation.
            hf: (np.ndarray) (n x n x o) objectives hessian evaluation.
            hg: (np.ndarray) (n x n x ni) inequalities hessian evaluation.
            hh: (np.ndarray) (n x n x ne) equalities hessian evaluation.

        """

        # functions evaluation
        f = self.objective.objectives.eval(x)
        g = self.constraints.inequality_constraints.eval(x)
        h = self.constraints.equality_constraints.eval(x)

        # functions gradient evaluation
        df = self.objective.objectives.gradient(x)
        dg = self.constraints.inequality_constraints.gradient(x)
        dh = self.constraints.equality_constraints.gradient(x)

        # functions hessian evaluation
        hf = self.objective.objectives.hessian(x)
        hg = self.constraints.inequality_constraints.hessian(x)
        hh = self.constraints.equality_constraints.hessian(x)

        return f, g, h, df, dg, dh, hf, hg, hh

    # attributes interface
    @property
    def objective(self):
        return self._objective

    @property
    def constraints(self):
        return self._constraints

    @property
    def results_(self):
        return self._results_

    @property
    def variables(self):
        return self._variables

    # setters
    @objective.setter
    def objective(self, objective):
        """Set objective of optimization problem.

        Args:
            objective: Objective class instance

        """

        if isinstance(objective, Objective):
            self._objective = objective
        else:
            raise Exception('Not an Objective instance!')

    @constraints.setter
    def constraints(self, constraints):
        """Set constraints of optimization problem.

        Args:
            constraints: Constraints class instance

        """

        if isinstance(constraints, Constraint):
            self._constraints = constraints
        else:
            raise Exception('Not a Constraints instance!')

    @results_.setter
    def results_(self, results):
        """Set results of optimization problem.

        Args:
            results: OptimizationResults class instance

        """

        if isinstance(results, OptimizationResults):
            self._results_ = results
        else:
            raise Exception('Not a Constraints instance!')

    @variables.setter
    def variables(self, variables):
        """Set variables of optimization problem.

        Args:
            variables: Variables class instance

        """

        if isinstance(variables, Variable):
            self._variables = variables
        else:
            raise Exception('Not a Variables instance!')

    def has_inequality_constraints(self):
        """

        Returns: (bool) True to indicate current problem has inequality constraints, false otherwise

        """
        return self.constraints.inequality_constraints.n_functions > 0

    def has_equality_constraints(self):
        """

        Returns: (bool) True to indicate current problem has equality constraints, false otherwise

        """
        return self.constraints.equality_constraints.n_functions > 0

    # methods
    def _build_problem(self, builder):
        """Build an optimization instance

        Args:
            builder: class Builder instance

        """

        # problem attributes
        variables = builder.build_variables()
        objective = builder.build_objectives()
        constraints = builder.build_constraints()

        # consistency check
        self._check_consistency(variables=variables, objectives=objective, constraints=constraints)

        # builder problem
        self.variables = variables
        self.objective = objective
        self.constraints = constraints

    def _check_consistency(self, variables, objectives, constraints):
        """Check optimization problem consistency.

        Args:
            variables  : problem variables
            objectives : objective functions
            constraints: constraints functions

        """

        # number of variables
        n = variables.x_min.shape[0]

        # linear inequality objective check
        C = objectives.C()
        d = objectives.d()
        self._linear_coefficients_check(C, d, n)

        # quadratic objective check
        self._quadratic_function_check(objectives.objectives, n)

        # linear equality constraints check
        Aeq = constraints.Aeq()
        beq = constraints.beq()
        self._linear_coefficients_check(Aeq, beq, n)

        # quadratic equality constraints check
        if constraints.equality_constraints is not None:
            self._quadratic_function_check(constraints.equality_constraints, n)

        # linear inequality constraints check
        A = constraints.A()
        b = constraints.b()
        self._linear_coefficients_check(A, b, n)

        # quadratic inequality constraints check
        if constraints.inequality_constraints is not None:
            self._quadratic_function_check(constraints.inequality_constraints, n)

    def op_arguments(self):
        """Method to return all optimization arguments.

        Returns:
            f     : eval of objectives
            df    : gradient eval of objectives
            C     : linear objective coefficients
            d     : linear objective constant
            g     : eval of nonlinear constraints
            dg    : gradient of nonlinear constraints
            A     : inequality linear constraints matrix
            b     : inequality linear constraints constants
            Aeq   : equality linear constraints matrix
            beq   : equality linear constraints constants
            x_min : lower bounds
            x_max : upper bounds
            x_type: variables' types
        """

        # define variables limits
        x_min = self.variables.x_min
        x_max = self.variables.x_max
        x_type = self.variables.x_type
        n = x_min.shape[0]

        # objective functions
        def f(x):
            return self.objective.objectives.eval(x)

        # objective function derivative
        def df(x):
            return self.objective.objectives.gradient(x)

        # linear objective parameters
        C = self.objective.C()
        d = self.objective.d()
        if C is None:
            C = np.zeros((n, 0))
        if d is None:
            d = np.zeros((0, 1))

        # define eval and gradient for nonlinear constraints
        idx_cons = self.nonlinear_functions_indices(self.constraints.inequality_constraints.functions)
        if idx_cons:
            def g(x):
                return self.constraints.inequality_constraints.eval(x, idx=idx_cons)

            def dg(x):
                return self.constraints.inequality_constraints.gradient(x, idx=idx_cons)
        else:
            def g(x):
                return np.zeros((0, 1))

            def dg(x):
                return np.zeros((n, 0))

        # inequality linear constraints parameters
        A = self.constraints.A()
        b = self.constraints.b()

        if A is None:
            A = np.zeros((0, n))
        if b is None:
            b = np.zeros((0, 1))

        # equality linear constraints parameters
        Aeq = self.constraints.Aeq()
        beq = self.constraints.beq()

        if Aeq is None:
            Aeq = np.zeros((0, n))
        if beq is None:
            beq = np.zeros((0, 1))

        return f, df, C, d, g, dg, A, b, Aeq, beq, x_min, x_max, x_type

    @staticmethod
    def nonlinear_functions_indices(functions_list):
        """ Index of nonlinear functions.

            Args:
                functions_list: a list of functions.

            Returns:
                idx: indices of nonlinear functions.
        """
        idx = [i for (i, f) in enumerate(functions_list) if not isinstance(f, LinearFunction)]
        return idx

    @staticmethod
    def _linear_coefficients_check(C, c, n):
        """Linear coefficients check.

        Args:
            C: dependent coefficients matrix
            c: independent coefficients vector
            n: number of variables

        """

        # check
        if C is not None and not (C.shape[1] == n):
            raise Exception("Dependent coefficients C must be a mx{}-matrix!".format(n))

        if c is not None and not (c.shape[0] == C.shape[0]) and not(c.shape[1] == 1):
            raise Exception("Independent coefficients d must be a {}x1-matrix!".format(C.shape[0]))

    @staticmethod
    def _quadratic_function_check(f_composite, n):
        """Quadratic function check

        Args:
            f_composite: function composite instance
            n          : number of variables

        """

        # check
        for fun in f_composite.functions:
            if isinstance(fun, QuadraticFunction) and not (fun.parameters['Q'].shape[0] == n and
                                                           fun.parameters['Q'].shape[1] == n):
                raise Exception("Q must be a {}x{} matrix!".format(n, n))

            if isinstance(fun, QuadraticFunction) and not (fun.parameters['c'].shape[0] == n):
                raise Exception("c must be {}x1 vector!".format(n))

    def info(self):
        """Print information about optimization problem."""

        # verbose
        print('\n')
        n = self.variables.x_min.shape[0]
        print('Numbers of objectives: {}'.format(self.objective.objectives.n_functions))
        print('Linear objective coefficients (c\'x):')
        print('c =')
        print(self.objective.C())
        print('Numbers of variables: {}'.format(n))
        for i in range(n):
            print('\t {} <= {} <= {}'.format(self.variables.x_min[i], 'x_' + str(i), self.variables.x_max[i]))
        if self.constraints.A() is not None:
            print('Inequality Linear Constraints (A*x <= b):')
            print('A =')
            print(self.constraints.A())
            print('b =')
            print(self.constraints.b())
        if self.constraints.Aeq() is not None:
            print('Equality Linear Constraints (Aeq*x = beq):')
            print('Aeq =')
            print(self.constraints.Aeq())
            print('beq =')
            print(self.constraints.beq())

    def plot(self, show_plot=True, levels=None):
        """
        Plot problem properly
        Args:
            show_plot: boolean, choose if plot will be directly shown

        Returns:

        """

        if self.objective.objectives.n_functions == 1:
            aux_plot = self.plot_mono_objective_problem()

        else:
            self.plot_pareto_variable_space(levels=levels)
            aux_plot = self.plot_pareto_objective_space()

        if show_plot:
            plt.show()

        return aux_plot

    def plot_mono_objective_problem(self):
        """
        Plot objective level curve, constraints borders and minimum point (not valid for multi objective problems)
        Args:

        Returns: QuadContourSet instance (from matplotlib)

        """

        f_obj = self.objective.objectives.functions[0]
        fig, ax = plt.subplots()

        x_lim = np.hstack((self.variables.x_min, self.variables.x_max))
        aux_plot = f_obj.plot(x_lim, ax_instance=ax, show_plot=False)

        for g in self.constraints.inequality_constraints.functions:
            g.plot(x_lim, ax_instance=ax, colors='g', levels=[0], l_width=2, show_plot=False)

        for h in self.constraints.equality_constraints.functions:
            h.plot(x_lim, ax_instance=ax, colors='r', levels=[0], l_width=2, show_plot=False)

        if self.results_ is not None:
            plt.scatter(self.results_.x[0, :], self.results_.x[1, :], s=40, c='k')

        plt.xlabel('$x_1$')
        plt.ylabel('$x_2$')
        plt.grid()

        return aux_plot

    def plot_pareto_variable_space(self, levels=None):
        """
        Plot objectives level curve and pareto border points in the variables space (doesn't plot constraints)
        Args:
            levels: level curves to be shown

        Returns: QuadContourSet instance (from matplotlib)

        """
        aux_plot = None
        color_vec = ['b', 'g', 'y', 'r', 'm', 'c']

        var = self.variables

        if var.dimension() > 2:
            return      # function plot not implemented for dimensions above 2

        x_lim = np.hstack((var.x_min, var.x_max))

        fig, ax = plt.subplots()
        for i, f in enumerate(self.objective.objectives.functions):

            aux_plot = f.plot(x_lim, ax_instance=ax, colors=color_vec[i], show_plot=False, levels=levels)

        if self.results_ is not None:
            plt.scatter(self.results_.x[0, :], self.results_.x[1, :], s=8, c='k')

        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.set_xlabel(r'$x_1$')
        ax.set_ylabel(r'$x_2$')

        return aux_plot

    def plot_pareto_objective_space(self):
        """
        Pareto border data considering objective evaluation
        Returns: PathCollection instance (from matplotlib)

        """

        n_func = self.objective.objectives.n_functions

        if n_func == 2:
            plt.figure()
            aux_plot = plt.scatter(self.results_.fx[0, :], self.results_.fx[1, :], s=20)
            plt.xlabel(r'$f_1$')
            plt.ylabel(r'$f_2$')
            plt.grid()

        elif n_func == 3:

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            aux_plot = ax.scatter(self.results_.fx[0, :], self.results_.fx[1, :], self.results_.fx[2, :])

            # axis labels
            ax.set_xlabel('$f_1$')
            ax.set_ylabel('$f_2$')
            ax.set_zlabel('$f_3$')

        else:   # pareto plot not implemented for more than three objectives
            return

        return aux_plot
