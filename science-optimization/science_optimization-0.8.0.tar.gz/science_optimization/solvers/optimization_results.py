"""
Class that deals with optimization results
"""

class OptimizationResults:
    """Container class for optimization results.

    """

    # class attributes
    _x = None  # the solution of the optimization
    _fx = None  # value of objectives function
    _parameter = None  # parameter of interest
    _message = None  # description of the cause of termination
    _n_iterations = None  # number of iterations
    _n_function_evaluations = None  # number of function evaluations

    # constructor
    def __init__(self, x=None, fun=None, parameter=None, message=None, n_iterations=0, n_function_evaluations=0):
        """OptimizationResults constructor.

        Args:
            x: (nd-array) The solution of the optimization
            fun: (nd-array) Values of objective function
            parameter: (nd-array) Any relevant parameter of the optimization algorithm
            message: (string) Termination message
            n_iterations: (int) Number of iterations performed by the solvers
            n_function_evaluations: (int) Number of evaluations of the objective functions
        """

        self.x = x
        self.fx = fun
        self.parameter = parameter
        self.message = message
        self.n_iterations = n_iterations
        self.n_function_evaluations = n_function_evaluations

    # attributes interface
    @property
    def x(self):
        return self._x

    @property
    def fx(self):
        return self._fx

    @property
    def parameter(self):
        return self._parameter

    @property
    def message(self):
        return self._message

    @property
    def n_iterations(self):
        return self._n_iterations

    @property
    def n_function_evaluations(self):
        return self._n_function_evaluations

    # setters
    @x.setter
    def x(self, x):
        self._x = x

    @fx.setter
    def fx(self, fun):
        self._fx = fun

    @parameter.setter
    def parameter(self, parameter):
        self._parameter = parameter

    @message.setter
    def message(self, message):
        self._message = message

    @n_iterations.setter
    def n_iterations(self, n_iterations):
        self._n_iterations = n_iterations

    @n_function_evaluations.setter
    def n_function_evaluations(self, n_function_evaluations):
        self._n_function_evaluations = n_function_evaluations

    # methods
    def info(self):
        """Print optimization results info.

        """
        print("\nTermination message: {}\n".format(self.message))
        print("x = \n{}\n".format(self.x))
        print("f(x) = \n{}\n".format(self.fx))
        print("Parameter value:\n {}\n".format(self.parameter))
        print("Number of iterations: {}\n".format(self.n_iterations))
        print("Number of function evaluations: {}".format(self.n_function_evaluations))
