import numpy as np
from scipy.optimize import minimize

from flex_optimization import OptimizationType, NotSupported
from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import ActiveMethod, StopCriteria
from flex_optimization.stop_criteria import StopIterationEvaluation, StopAbsoluteChange


class SciPyBase(ActiveMethod):
    """
    https://docs.scipy.org/doc/scipy/tutorial/optimize.html?highlight=bfgs#optimization-scipy-optimize

    """

    def __init__(self,
                 problem: Problem,
                 stop_criterion: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 x0: list | tuple | np.ndarray,
                 multiprocess: bool | int = False,
                 recorder: Recorder = None,
                 options: dict = None,
                 _method: str = None):

        self.x0 = x0
        self.options = options if options is not None else {}
        self._method = _method

        super().__init__(problem, stop_criterion, multiprocess, recorder)

    def method_init(self):
        self._flag_init = True
        for var in self.problem.variables:
            if isinstance(var, DiscreteVariable):
                raise NotSupported("Discrete variables are not currently supported for this algorithm. ")

        # stopping information
        for stop in self.stop_criterion:
            if stop is isinstance(stop, list):
                continue  # compound stop criteria evaluated in flex_optimization not scipy
            if isinstance(stop, StopIterationEvaluation):
                if 'options' in self.options:
                    self.options["options"] = self.options["options"] | {"maxiter": stop.num_eval}
                else:
                    self.options["options"] = {"maxiter": stop.num_eval}

            elif isinstance(stop, StopAbsoluteChange):
                self.options["tol"] = stop.cut_off_value

        # add defaults
        bounds = []
        for var in self.problem.variables:
            bounds.append([var.min_, var.max_])
        self.options["bounds"] = bounds

    def run_steps(self, algo_steps: int = 1):
        if not self._flag_init:
            self.method_init()

        try:
            if self.problem.type_ == OptimizationType.MAX:
                def maximize_func(*args, **kwargs):
                    return -1 * self.problem.evaluate_capture(*args, **kwargs)

                func = maximize_func
            else:
                func = self.problem.evaluate_capture

            result = minimize(func, self.x0, method=self._method, callback=self.callback, **self.options)
            self._check_result(result)

        except KeyboardInterrupt as e:
            self.recorder._error_exit(e)

        except Exception as e:
            print(e)
            self.recorder._error_exit(e)

    def callback(self, *args, **kwargs):
        self.iteration_count += 1
        point = []
        result = []
        metric = []
        for i in range(len(self.problem._temp_data)):
            temp = self.problem._temp_data.pop(0)
            point.append(temp[0])
            result.append(temp[1])
            metric.append(temp[2])
        super()._tell(point, result, metric)

    def _check_result(self, result):
        if result.success:
            return

        self.recorder.record(self.recorder.WARNING, text="SciPy: " + result.message)

    def get_point(self) -> list:
        raise NotImplementedError("This algorithm does not support this function. ")
