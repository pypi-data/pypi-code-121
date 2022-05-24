# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Controller for integration of Boulder Opal automated closed-loop optimizers and M-LOOP.
"""
import re
from typing import (
    Any,
    List,
    Optional,
    Union,
)
from warnings import warn

import mloop.learners as mll
import numpy as np
from mloop.controllers import Controller
from mloop.interfaces import Interface
from qctrl import Qctrl
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.preconditions import check_argument


class QctrlController(Controller):
    """
    Controller for optimizations that uses Boulder Opal automated
    closed-loop optimizers.

    You can use this controller to integrate an experiment managed by
    M-LOOP to a Boulder Opal automated closed-loop optimizer. Notice that
    you need to set up an M-LOOP Interface to your experiment, initiate a
    Boulder Opal session, and define your choice of Boulder Opal automated
    closed-loop optimizer prior to using this class.

    Arguments
    ---------
    interface : mloop.interfaces.Interface
        The M-LOOP interface from where you obtain the cost value of the
        test points.
    qctrl : qctrl.Qctrl
        The object representing the Boulder Opal session. You must initiate
        it before calling the controller.
    optimizer : qctrl.types.closed_loop_optimization_step.Optimizer
        The Boulder Opal automated closed-loop optimizer that you want to
        use. It must be a valid optimizer object (containing either an
        initializer or a state from a previous optimization run), as
        described in the Boulder Opal reference documentation.
    test_point_count : int, optional
        The requested number of test points that the Boulder Opal automated
        closed-loop optimizer generates at each step. If chosen, it must be
        greater than zero. This is a hint only. The Boulder Opal automated
        closed-loop optimizer might choose differently.
    learner : mloop.learners.Learner, optional
        The M-LOOP Learner that this controller uses to obtain extra test
        points, before there are enough results to run a step of the
        Boulder Opal automated closed-loop optimizer. Defaults to None, in
        which case this controller uses a `RandomLearner`.
    training_run_count : int, optional
        The minimum number of training points that the controller obtains
        before calling the Boulder Opal automated closed-loop optimizer.
        Defaults to 0, in which case the controller uses the minimum number
        of points that the Boulder Opal automated closed-loop optimizer
        requires.
    interleaved_run_count : int, optional
        The minimum number of test points that the controller obtains from
        the `learner` between two calls of the Boulder Opal automated
        closed-loop optimizer, in addition to the points that Boulder Opal
        requested. Defaults to 0.
    kwargs : dict
        All the extra arguments that the Controller class from M-LOOP
        accepts.
    """

    def __init__(
        self,
        interface: Interface,
        qctrl: Qctrl,
        optimizer: Any,
        test_point_count: Optional[int] = None,
        learner: Optional[mll.Learner] = None,
        training_run_count: int = 0,
        interleaved_run_count: int = 0,
        **kwargs,
    ):
        super().__init__(interface, **kwargs)

        # Auxiliary learner, used to get the initial test points before
        # there are enough points to run Boulder Opal automated closed-loop
        # optimization.
        self.learner = learner
        if self.learner is None:
            self.learner = mll.RandomLearner(**self.remaining_kwargs)
        self._update_controller_with_learner_attributes()

        if test_point_count is not None:
            check_argument(
                test_point_count > 0,
                "The value of test_point_count must be greater than zero.",
                {"test_point_count": test_point_count},
            )

        self._test_point_count = test_point_count

        self._types_namespace = qctrl.types.closed_loop_optimization_step
        self._optimization_step = (
            qctrl.functions.calculate_closed_loop_optimization_step
        )

        if optimizer.state is not None:
            minimum_training_run_count = 0
        elif optimizer.cross_entropy_initializer is not None:
            minimum_training_run_count = np.ceil(
                2 / optimizer.cross_entropy_initializer.elite_fraction
            )
        elif optimizer.gaussian_process_initializer is not None:
            minimum_training_run_count = 2
        else:
            minimum_training_run_count = 2 * self.learner.num_params
            warn(
                f"Unrecognized optimizer {optimizer}, falling back to "
                f"{minimum_training_run_count} as the minimum number of "
                "training runs."
            )

        self._training_run_count = max(training_run_count, minimum_training_run_count)

        check_argument(
            interleaved_run_count >= 0,
            "The value of interleaved_run_count must not be negative.",
            {"interleaved_run_count": interleaved_run_count},
        )

        self._interleaved_run_count = interleaved_run_count

        self._optimizer = optimizer

    def _call_boulder_opal(self, cost_function_results: List[Any]) -> List[np.ndarray]:
        """
        Manages each call to Boulder Opal.
        """
        result = self._optimization_step(
            optimizer=self._optimizer,
            results=cost_function_results,
            test_point_count=self._test_point_count,
        )

        self._optimizer = self._types_namespace.Optimizer(state=result.state)

        return [np.array(test_point.parameters) for test_point in result.test_points]

    def _transform_cost(self) -> Union[float, np.ndarray]:
        """
        Adapts the cost values according to the needs of each learner.
        """
        cost = self.curr_cost

        if self.curr_bad:
            cost = float("inf")

        return cost

    def _optimization_routine(self):
        """
        The main optimization routine.

        This overrides a method from the parent class in M-LOOP.
        """
        cost_function_results: List[Any] = []
        boulder_opal_parameters: List[np.ndarray] = []

        # Number of costs obtained before this function calls the BOULDER
        # OPAL automated closed-loop optimizer.
        required_run_count = self._training_run_count

        while self.check_end_conditions():
            # Call Boulder Opal only if the number of required runs has
            # been reached and there is at least one result to pass.
            if (self.num_in_costs >= required_run_count) and (
                len(cost_function_results) > 0
            ):
                boulder_opal_parameters = self._call_boulder_opal(cost_function_results)
                cost_function_results = []
                # The total number of runs before the next call to BOULDER
                # OPAL, which is: the current number of runs, plus the
                # number of runs that Boulder Opal requested, plus the
                # number of extra interleaved runs that the auxiliary
                # learner requests.
                required_run_count = (
                    self.num_in_costs
                    + len(boulder_opal_parameters)
                    + self._interleaved_run_count
                )

            # Obtain parameters from the Boulder Opal automated closed-loop
            # optimizer if any are available.
            use_boulder_opal_parameters = len(boulder_opal_parameters) > 0
            if use_boulder_opal_parameters:
                parameters = boulder_opal_parameters.pop(0)
            # Use auxiliary learner if the Boulder Opal automated
            # closed-loop optimizer doesn't have more parameters to suggest.
            else:
                parameters = self.learner_params_queue.get()

            # Communicate parameters to the experimental interface, and
            # obtain the results of the cost function.
            self._put_params_and_out_dict(parameters)
            self._get_cost_and_in_dict()

            self.save_archive()

            # Store cost function result in the learner's queue if it was
            # requested by the auxiliary learner.
            if not use_boulder_opal_parameters:
                self.learner_costs_queue.put(
                    (parameters, self._transform_cost(), self.curr_uncer, self.curr_bad)
                )

            # Store cost function result in the list to be used by Boulder Opal.
            if not self.curr_bad:
                cost_function_results.append(
                    self._types_namespace.CostFunctionResult(
                        parameters=self.curr_params,
                        cost=self.curr_cost,
                        cost_uncertainty=self.curr_uncer,
                    )
                )


def qctrl_controller(
    interface: Interface,
    initializer_name: str,
    api_root: Optional[str] = None,
    test_point_count: Optional[int] = None,
    learner_name: Optional[str] = None,
    training_run_count: int = 0,
    interleaved_run_count: int = 0,
    **kwargs,
):
    """
    Creates a `QctrlController` using serializable parameters.

    You can use this to create a `QctrlController` when calling BOULDER
    OPAL from an M-LOOP configuration file. To do this, add the line
    ``controller_type="qctrlmloop:qctrl_controller"`` to the configuration
    file, and follow it with all the parameters that you want to pass to
    this function. Notice that you must prefix all the parameters for the
    optimizer with the prefix ``initializer_``. For example, to pass the
    parameter ``elite_fraction=0.1`` to the `CrossEntropyInitializer`,
    write ``initializer_name="CrossEntropyInitializer"`` and
    ``initializer_elite_fraction=0.1`` in the configuration file.

    Parameters
    ----------
    interface : mloop.interfaces.Interface
        The M-LOOP interface from where you obtain the cost value of the
        test points.
    initializer_name : str
        A string representing the name of the initializer that you want to
        use. You must write the name in PascalCase. For example, write
        ``"CrossEntropyInitializer"`` to use the cross entropy method.
        You must prefix all the parameters that you want to pass to the
        initializer with ``initializer_`` and include them in the keyword
        arguments of this function.
    api_root : str, optional
        The URL of the Boulder Opal API that you want to use. Defaults to
        ``None``, in which case the default API server is used.
    test_point_count : int, optional
        The requested number of test points that the Boulder Opal automated
        closed-loop optimizer generates at each step. If chosen, it must be
        greater than zero. This is a hint only. The Boulder Opal automated
        closed-loop optimizer might choose differently.
    learner_name : str, optional
        The name of the M-LOOP Learner that this controller uses to obtain
        extra test points, before there are enough results to run a step of
        the Boulder Opal automated closed-loop optimizer. Defaults to
        ``None``, in which case this controller uses a `RandomLearner`.
    training_run_count : int, optional
        The minimum number of training points that the controller obtains
        before calling the Boulder Opal automated closed-loop optimizer.
        Defaults to 0, in which case the controller uses the minimum number
        of points that the Boulder Opal automated closed-loop optimizer
        requires.
    interleaved_run_count : int, optional
        The minimum number of test points that the controller obtains from
        the learner between two calls of the Boulder Opal automated
        closed-loop optimizer, in addition to the points that Boulder Opal
        requested. Defaults to 0.
    **kwargs : dict
        All the extra arguments that the Controller class from M-LOOP
        accepts.

    Returns
    -------
    QctrlController
        The controller that integrates Boulder Opal with M-LOOP.

    Raises
    ------
    QctrlArgumentsValueError
        Raised if the names provided for `initializer_name` and
        `learner_name` don't match valid object classes.
    """
    # Create Qctrl object.
    qctrl = Qctrl(api_root=api_root)

    # Create Initializer object.
    try:
        initializer_class = getattr(
            qctrl.types.closed_loop_optimization_step, initializer_name
        )
    except AttributeError as exception:
        raise QctrlArgumentsValueError(
            "Unable to find initializer class"
            f" qctrl.types.closed_loop_optimization_step.{initializer_name}.",
            {"initialize_name": initializer_name},
        ) from exception

    initializer_kwargs = {
        key[len("initializer_") :]: value
        for key, value in kwargs.items()
        if key.startswith("initializer_")
    }
    remaining_kwargs = {
        key: value for key, value in kwargs.items() if key not in initializer_kwargs
    }
    initializer = initializer_class(**initializer_kwargs)

    # Create Optimizer object.
    snake_case_name = re.sub("(.)([A-Z])", "\\1_\\2", initializer_name).lower()
    optimizer_kwargs = {snake_case_name: initializer}
    optimizer = qctrl.types.closed_loop_optimization_step.Optimizer(**optimizer_kwargs)

    # Create Learner object.
    learner: Optional[mll.Learner] = None
    if learner_name is not None:
        try:
            learner_class = getattr(mll, learner_name)
        except AttributeError as exception:
            raise QctrlArgumentsValueError(
                f"Unable to find learner class mloop.learners.{learner_name}.",
                {"learner_name": learner_name},
            ) from exception
        learner = learner_class(**remaining_kwargs)

    return QctrlController(
        interface=interface,
        qctrl=qctrl,
        optimizer=optimizer,
        test_point_count=test_point_count,
        learner=learner,
        training_run_count=training_run_count,
        interleaved_run_count=interleaved_run_count,
        **remaining_kwargs,
    )
