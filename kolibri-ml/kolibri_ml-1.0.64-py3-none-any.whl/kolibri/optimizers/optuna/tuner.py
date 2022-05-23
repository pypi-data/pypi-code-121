import os
import json
from kdmt.dict import update
import joblib
import psutil
try:
    import optuna
    from optuna.pruners import SuccessiveHalvingPruner
    has_optuna=True
except:
    has_optuna=False
    pass

from kdmt.file import create_dir


class OptunaTuner:
    def __init__(
        self,
        results_path,
        eval_metric,
        time_budget=3600,
        init_params={},
        verbose=True,
        n_jobs=-1,
        random_state=42,
        direction="maximize"
    ):

        if not has_optuna:
            raise Exception("optuna package not found please install it using 'pip install optuna' ")


        self.study_dir = os.path.join(results_path, "optimizer")
        create_dir(self.study_dir)
        self.tuning_fname = os.path.join(self.study_dir, "optuna.json")
        self.tuning = init_params
        self.eval_metric = eval_metric

        self.direction = direction
        self.n_warmup_steps = (
            50  # set large enough to give small learning rates a chance
        )
        self.time_budget = time_budget
        self.verbose = verbose
#        self.ml_task = ml_task
        self.n_jobs = n_jobs
        self.random_state = random_state


        self.load()
        if not self.verbose:
            optuna.logging.set_verbosity(optuna.logging.CRITICAL)


    def optimize2(
        self,
        objective,
        learner_params,
    ):
        algorithm=learner_params["fixed"]["name"]
        defaults=learner_params["fixed"]['default-params']

        if self.verbose:
            print(
                f"Optuna optimizes {algorithm} with time budget {self.time_budget} seconds "
                f"eval_metric {self.eval_metric} ({self.direction})"
            )

        study = optuna.create_study(
            direction=self.direction,
            sampler=optuna.samplers.TPESampler(seed=self.random_state),
            pruner=SuccessiveHalvingPruner(),
        )
        study.enqueue_trial(defaults)
        study.optimize(objective, n_trials=5000, timeout=self.time_budget)

        joblib.dump(study, os.path.join(self.study_dir, str(algorithm) + ".joblib"))

        best = study.best_params
        best["metric"] = objective.eval_metric_name
        best["feature_pre_filter"] = False
        best["seed"] = objective.seed


        self.save()

        return update(learner_params, best)

    def optimize(self, objective, learner_params):
        algorithm="pipeline"
        defaults=learner_params

        if self.verbose:
            print(
                f"Optuna optimizes {algorithm} with time budget {self.time_budget} seconds "
                f"eval_metric {self.eval_metric} ({self.direction})"
            )

        study = optuna.create_study(
                direction=self.direction,
                sampler=optuna.samplers.TPESampler(seed=self.random_state),
                pruner=SuccessiveHalvingPruner()
            )
        study.enqueue_trial(defaults)
        study.optimize(objective, timeout=self.time_budget, n_jobs=self.n_jobs)

        joblib.dump(study, os.path.join(self.study_dir, str(algorithm) + ".joblib"))

        best = study.best_params

        self.save()

        return update(learner_params, best)


    def save(self):
        with open(self.tuning_fname, "w", encoding='utf-8') as fout:
            fout.write(json.dumps(self.tuning, indent=4))

    def load(self):
        if os.path.exists(self.tuning_fname):
            params = json.loads(open(self.tuning_fname).read(), encoding='utf-8')
            for k, v in params.items():
                self.tuning[k] = v
