
from argparse import Namespace

from flex_optimization import OptimizationType
from flex_optimization.methods import MethodType, MethodClassification
from flex_optimization.core.recorder import Recorder
from flex_optimization.core.variable import ContinuousVariable, DiscreteVariable
from flex_optimization.core.problem import Problem
from flex_optimization.core.method_subclass import ActiveMethod
from flex_optimization.core.stop_criteria import StopCriteria


def _check_for_package():
    try:
        import dragonfly
    except ImportError:
        raise ImportError("Flex-optimization: Optional requirement."
                          "\n\nTo use this method you will need to install DragonFly (pip install dragonfly-opt).\n"
                          "For more information see: https://dragonfly-opt.readthedocs.io/en/master/install/\n")


def dragonfly_setup(options, config):
    # Customizable algorithm settings
    dragon_options = Namespace(
        # batch size (number of new experiments you want to query at each iteration)
        build_new_model_every=options["build_new_model_every"],
        # number of initialization experiments (-1 is included since Dragonfly generates n+1 expts)
        init_capital=options["init_capital"] - 1,
        # Criterion for tuning GP hyperparameters. Options: 'ml' (works well for smooth surfaces), 'post_sampling',
        # or 'ml-post_sampling' (algorithm default).
        gpb_hp_tune_criterion=options["gpb_hp_tune_criterion"]
    )

    # Create optimizer object
    from dragonfly.exd.experiment_caller import CPFunctionCaller
    from dragonfly.opt.gp_bandit import CPGPBandit
    func_caller = CPFunctionCaller(None, config.domain, domain_orderings=config.domain_orderings)
    optimizer = CPGPBandit(func_caller, 'default', ask_tell_mode=True, options=dragon_options)
    optimizer.initialise()  # this generates initialization points

    return optimizer


class MethodBODragon(ActiveMethod):
    """ Setup for single objective only"""

    def __init__(self,
                 problem: Problem,
                 stop_criteria: StopCriteria | list[StopCriteria] | list[list[StopCriteria]],
                 init_expts: int = 5,
                 options: dict = None,
                 multiprocess: bool | int = False,
                 recorder: Recorder = None):
        _check_for_package()

        default_options = dict(
            build_new_model_every=1,
            init_capital=init_expts,
            gpb_hp_tune_criterion='ml-post_sampling',
            moors_scalarisation='tchebychev',
        )
        if options is not None:
            default_options = default_options | options  # overwrite defaults
        self.options = default_options

        super().__init__(problem, stop_criteria, multiprocess, recorder)

        self.optimizer = dragonfly_setup(self.options, self._get_config())
        self._init_points = self.optimizer.ask(init_expts)
        self._tell_check = False  # False is not ready

    def _get_config(self):
        domain = []
        for var in self.problem.variables:
            if isinstance(var, ContinuousVariable):
                domain.append(dict(
                    name=var.name,
                    type=var.type_.__name__,  # needs to be string ["float", "int"]
                    min=var.min_,
                    max=var.max_
                ))
            elif isinstance(var, DiscreteVariable):
                domain.append(dict(
                    name=var.name,
                    type='discrete',
                    items=var.items
                ))
            else:
                raise NotImplementedError

        from dragonfly import load_config
        return load_config({'domain': domain})

    def get_point(self) -> list:
        if not self._flag_init:  # Initialization phase
            point = self._init_points.pop()
            if not self._init_points:  # no more initialization points
                self._flag_init = True
            return point

        # refinement phase
        self.optimizer._build_new_model()  # key line! update model using prior results
        self.optimizer._set_next_gp()  # key line! set next GP
        return self.optimizer.ask()

    def _tell(self, point, result, metric):
        super()._tell(point, result, metric)

        # DragonFly is a maximizer, so this enables minimization
        if self.problem.type_ == OptimizationType.MIN:
            metric = -1*metric

        if len(point) > 1:
            for p, r in zip(point, metric):
                self.optimizer.step_idx += 1  # increment experiment number
                self.optimizer.tell([(p, r[0])])  # return result to algorithm
        else:
            self.optimizer.step_idx += 1  # increment experiment number
            self.optimizer.tell([(point[0], metric[0])])  # return result to algorithm

    def _multi_run_step(self, algo_steps: int):
        if not self._flag_init:  # Initialization phase
            self._multi_run_step_init()
            algo_steps -= 1
            if not self._check_stop_criterion():
                return

        # refinement phase
        num_points = self.options["build_new_model_every"]
        self.recorder.record(self.recorder.NOTES,
                             text=f"Multiprocessing | Refinement phase : {num_points} "
                                  f"will be evaluated each loop.\n")

        for step in range(algo_steps):
            self.iteration_count += 1
            self.optimizer._build_new_model()  # key line! update model using prior results
            self.optimizer._set_next_gp()  # key line! set next GP
            points = [self.optimizer.ask() for _ in range(num_points)]
            result = self.problem.evaluate_multiprocessing(points, self._get_pool_size())
            metric = self.problem.metric(result)
            self._tell(points, result, metric)
            if not self._check_stop_criterion():
                break

            self.recorder.record(self.recorder.NOTES, text=f"/ Step | {step}/{algo_steps} complete.")

    def _multi_run_step_init(self):
        points = self._init_points
        self.recorder.record(self.recorder.NOTES,
                             text=f"Multiprocessing | Initialization ran (points being evaluated: "
                                  f"{len(self._init_points)})")
        self._flag_init = True
        result = self.problem.evaluate_multiprocessing(points, self._get_pool_size())
        metric = self.problem.metric(result)
        self._tell(points, result, metric)


method_class = MethodClassification(
    name="random",
    func=MethodBODragon,
    type_=MethodType.ACTIVE_BAYESIAN
)
