import time
from datetime import datetime

import numpy as np

from flex_optimization.core.recorder import Recorder
from flex_optimization.core.logger_ import logger


def _obj_to_list(obj):
    obj_ = []
    if isinstance(obj, (list, tuple)):
        for row in obj:
            if isinstance(row, list):
                obj_.append(row)
            elif isinstance(row, tuple):
                obj_.append(list(row))
            elif isinstance(row, np.ndarray):
                obj_.append(row.tolist())
            elif isinstance(row, (int, float, str)):
                obj_.append([row])
    elif isinstance(obj, np.ndarray):
        for i in obj:
            obj_.append([i.tolist()])

    return obj_


def shape_check(point, result, metric) -> (list[list], list[list], list[list]):
    return _obj_to_list(point), _obj_to_list(result), _obj_to_list(metric)


class RecorderFull(Recorder):
    def __init__(self, problem=None, method=None):
        self.start_time = None
        self.end_time = None
        self._first_eval = True
        self.num_data_points: int = 0
        super().__init__(problem, method)
        logger.setLevel(logger.DEBUG)

    @property
    def duration(self):
        return self.end_time - self.start_time

    def _error_exit(self, e):
        """ Save data if something goes wrong in the middle of the optimization. """
        from datetime import datetime

        self._error = e
        if len(self.data) > 1:
            filename = f"data_error_export_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            logger.error(f"Error Occurred!!!!!!!! Data saved as '{filename}'")
            self.save(filename)
        else:
            logger.error(f"Error Occurred!!!!!!!!")

        raise e

    def record(self, type_: int, **kwargs):
        if type_ == self.EVALUATION:
            self._record_evaluation(**kwargs)
        elif type_ == self.SETUP:
            self._record_setup()
        elif type_ == self.RUNNING:
            self._record_running()
        elif type_ == self.STOP:
            self._record_stop(**kwargs)
        elif type_ == self.FINISH:
            self._record_finish()
        elif type_ == self.NOTES:
            self._record_notes(**kwargs)
        elif type_ == self.WARNING:
            self._record_warning(**kwargs)
        elif type_ == self.ERROR:
            self._record_error(**kwargs)
        else:
            raise NotImplementedError("The full recorder should implement everything!")

    def _record_setup(self):
        # log problem
        logger.info(f"{type(self.problem).__name__} | {repr(self.problem)}")

        # log variables
        for var in self.problem.variables:
            logger.info(f"{type(var).__name__} | {repr(var)}")

        # log method
        logger.info(f"{type(self.method).__name__} | {repr(self.method)}")

    def _record_running(self):
        self.start_time = datetime.now()
        logger.info(f"\nOptimization Running | start:{self.start_time}")

    def _record_evaluation(self, point, result, metric):
        show_metric = True
        show_iteration = False
        if result == metric:
            show_metric = False
        if hasattr(self.method, "iteration_count"):
            show_iteration = True

        if self._first_eval:
            self._first_eval = False
            self._create_header(show_metric, show_iteration)

        point, result, metric = shape_check(point, result, metric)
        for p, r, m in zip(point, result, metric):
            # save data
            if show_metric:
                self.data.append(p + r)
            else:
                self.data.append(p + r + m)

            # send data to logger
            mes = f"{self.num_data_points} |"
            if show_iteration:
                mes += f" {self.method.iteration_count} |"
            mes += f" {p} --> {r}"
            if show_metric:
                mes += f" --> {m}"
            logger.monitor(mes)
            self.num_data_points += 1

        self._up_to_date = False

    def _create_header(self, show_metric: bool = False, show_iteration: bool = False):
        mes = "counter |"
        if show_iteration:
            mes += " iteration | "
        mes += f"{[self.problem.variable_names]} --> result"
        if show_metric:
            mes += " --> metric"
        logger.monitor(mes)
        logger.monitor("-" * len(mes))

    @staticmethod
    def _record_stop(text: str):
        logger.info(text)

    def _record_finish(self):
        self.end_time = datetime.now()
        logger.info(f"Calculation time: {self.duration}")
        time.sleep(0.1)

        logger.info(f"\nBest Result: {self.best_result}")

    @staticmethod
    def _record_notes(text: str):
        logger.info(text)

    @staticmethod
    def _record_warning(text: str):
        logger.warn(text)

    @staticmethod
    def _record_error(text: str):
        logger.error(text)
