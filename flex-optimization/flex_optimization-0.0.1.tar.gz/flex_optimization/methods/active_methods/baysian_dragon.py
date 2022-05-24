import multiprocessing
from argparse import Namespace
from typing import Union

try:
    import dragonfly
    from dragonfly import load_config
    from dragonfly.exd.experiment_caller import CPFunctionCaller, CPMultiFunctionCaller
    from dragonfly.opt.gp_bandit import CPGPBandit
except ImportError:
    print("To use this method you will need to install DragonFly (pip install dragonfly-opt).\n"
          "For more information see: https://dragonfly-opt.readthedocs.io/en/master/install/\n")

from flex_optimization.problem_statement import ActiveMethod, Problem, StopCriteria, ContinuousVariable, \
    DiscreteVariable
from flex_optimization.method_logger import logger


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
    func_caller = CPFunctionCaller(None, config.domain, domain_orderings=config.domain_orderings)
    optimizer = CPGPBandit(func_caller, 'default', ask_tell_mode=True, options=options)
    optimizer.initialise()  # this generates initialization points

    return optimizer


class MethodBODragon(ActiveMethod):
    def __init__(self,
                 problem: Problem,
                 stop_criteria: Union[StopCriteria, list[StopCriteria], list[list[StopCriteria]]],
                 multiprocess: Union[bool, int] = False,
                 init_expts: int = 5,
                 options: dict = None):
        default_options = dict(
            build_new_model_every=1,
            init_capital=init_expts,
            gpb_hp_tune_criterion='ml-post_sampling',
            moors_scalarisation='tchebychev',
        )
        if options is not None:
            default_options = default_options | options  # overwrite defaults
        self.options = default_options

        super().__init__(problem, stop_criteria, multiprocess)

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

        return load_config({'domain': domain})

    def method_init(self):
        pass

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

    def _tell(self, point, result):
        if isinstance(point[0], list):
            for p, r in zip(point, result):
                self.optimizer.step_idx += 1  # increment experiment number
                self.optimizer.tell([(p, r)])  # return result to algorithm
        else:
            self.optimizer.step_idx += 1  # increment experiment number
            self.optimizer.tell([(point, result)])  # return result to algorithm

    def _multi_run_step(self, algo_steps: int):
        if not self._flag_init:  # Initialization phase
            self._multi_run_step_init()
            algo_steps -= 1
            if not self._check_stop_criterion():
                return

        # refinement phase
        num_points = self.options["build_new_model_every"]
        logger.info(f"Multiprocessing | Refinement phase : {num_points} will be evaluated each loop.\n")

        for step in range(algo_steps):
            self.optimizer._build_new_model()  # key line! update model using prior results
            self.optimizer._set_next_gp()  # key line! set next GP
            points = [self.optimizer.ask() for _ in range(num_points)]
            with multiprocessing.Pool(self._get_pool_size()) as p:
                result = p.map(self.problem.evaluate, points)
            logger.monitor(f"/ Step | {step}/{algo_steps} complete.")
            self._tell(points, result)
            self._save_data(points, result)
            if not self._check_stop_criterion():
                break

    def _multi_run_step_init(self):
        points = self._init_points
        logger.info(f"Multiprocessing | Initialization ran (points being evaluated: "
                    f"{len(self._init_points)})")
        self._flag_init = True

        with multiprocessing.Pool(self._get_pool_size()) as p:
            result = p.map(self.problem.evaluate, points)
        self._tell(points, result)
        self._save_data(points, result)
