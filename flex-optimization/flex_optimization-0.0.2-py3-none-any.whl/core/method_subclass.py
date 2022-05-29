from abc import ABC, abstractmethod

from flex_optimization.core.recorder import Recorder
from flex_optimization.core.problem import Problem
from flex_optimization.core.method import Method
from flex_optimization.core.stop_criteria import StopCriteria


def temp_func(func, point):
    result = func(point)
    return point, result


class PassiveMethod(Method, ABC):
    def __init__(self, problem: Problem, multiprocess: bool | int = False, recorder: Recorder = None):
        self.number_points = None
        super().__init__(problem, multiprocess, recorder)

    @abstractmethod
    def get_points(self):
        pass

    def run(self):
        self.recorder.record(self.recorder.RUNNING)

        try:
            points = self.get_points()
            self.number_points = len(points)
            self.recorder.record(self.recorder.NOTES, text=f"\tNumber of evaluations to preform: {self.number_points}")

            if self.multiprocess >= 1:
                self._run_multiproessing(points)
            else:
                self._run_single(points)

            self.recorder.record(self.recorder.FINISH)

        except KeyboardInterrupt as e:
            self.recorder._error_exit(e)

        except Exception as e:
            print(e)
            self.recorder._error_exit(e)

    def _run_single(self, points):
        for point in points:
            result = self.problem.evaluate(point)
            metric = self.problem.metric(result)
            self.recorder.record(self.recorder.EVALUATION, point=[point], result=result, metric=metric)

    def _run_multiproessing(self, points):

        def callback(results):
            point_, result = results
            metric = self.problem.metric(result)
            self.recorder.record(self.recorder.EVALUATION, point=[point_], result=result, metric=metric)

        from functools import partial
        from flex_optimization.core.utils import PoolHandler
        pool = PoolHandler(
            func=partial(temp_func, func=self.problem.evaluate),
            pool_size=self._get_pool_size(),
            pool_points=points,
            callback=callback
        )
        pool.run()


class ActiveMethod(Method, ABC):

    def __init__(self,
                 problem: Problem,
                 stop_criterion: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):
        if not isinstance(stop_criterion, list):
            stop_criterion = [stop_criterion]
        self.stop_criterion: list[StopCriteria] = stop_criterion
        self.iteration_count = 0
        self._flag_init = False  # False = Not initialized
        super().__init__(problem, multiprocess, recorder)

    def method_init(self):
        self._flag_init = True

    @abstractmethod
    def get_point(self):
        pass

    def run(self, guard_value: int = 1_000_000):
        """ Run optimization. """
        self.recorder.record(self.recorder.RUNNING)
        self.run_steps(guard_value)
        self.recorder.record(self.recorder.FINISH)

    def run_steps(self, algo_steps: int = 1):
        """
        Step through optimization

        Parameters
        ----------
        algo_steps: int
            algorithm steps to preform
            * may be multiple function evaluations
            * initialization is one algorithm step

        Returns
        -------

        """
        if not self._flag_init:
            self.method_init()

        try:
            if self.multiprocess:
                self._multi_run_step(algo_steps)
                return

            # main optimization loop
            for _ in range(algo_steps):
                self.iteration_count += 1
                point = self.get_point()
                result = self.problem.evaluate(point)
                metric = self.problem.metric(result)
                self._tell([point], result, metric)
                if not self._check_stop_criterion():
                    break

        except KeyboardInterrupt as e:
            self.recorder._error_exit(e)

        except Exception as e:
            print(e)
            self.recorder._error_exit(e)

    def _multi_run_step(self, step: int):
        """ Sub-classed for multiprocessing capabilities. """
        raise NotImplementedError("Multi-processing not implemented yet.")

    def _tell(self, point, result, metric):
        """ Update optimizer with new values"""
        self.recorder.record(self.recorder.EVALUATION, point=point, result=result, metric=metric)

    def _check_stop_criterion(self):
        """
        Check stop criterion
        True = Continue; False = Stop
        """
        for criteria in self.stop_criterion:
            if isinstance(criteria, list):
                if not self._multi_stop_criterion(criteria):
                    self.stop_criteria = criteria
                    self.recorder.record(self.recorder.STOP, text=f"Stop Criteria met:{criteria}")
                    return False

            elif not criteria.evaluate(self):
                self.stop_criteria = criteria
                self.recorder.record(self.recorder.STOP, text=f"Stop Criteria met:{criteria}")
                return False

        return True

    def _multi_stop_criterion(self, criterion):
        """ If multiple stop criterion, check to see if all are False. ('and' stop criteria)"""
        stopping_results = []
        for criteria in criterion:
            stopping_results.append(criteria.evaluate(self))

        return any(stopping_results)
