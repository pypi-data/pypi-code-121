try:
    import optuna
    has_optuna=True
except:
    has_optuna=False
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_predict
EPS = 1e-8
from kolibri.optimizers.metric import Metric
from kolibri.core.pipeline import Pipeline
import warnings
from copy import deepcopy
from sklearn.model_selection import train_test_split
from kdmt.objects import class_from_module_path, class_name
from kolibri.config import ParamType
warnings.filterwarnings("ignore")



class Objective:
    def __init__(
        self,
        X,
        y,
        estimator,
        sample_weight,
        eval_metric=Metric({"name": "f1-score"}),
        random_state=41,
        n_jobs=-1,
        sample_weight_validation=None,
        direction='maximize'
        ):
        self.X = X
        self.y = y
        self.sample_weight = sample_weight
        self.parameters=deepcopy(estimator.parameters)
        self.eval_metric = Metric({"name": "f1-score"})
        self.eval_metric_name="f1-score"
        self.n_jobs = n_jobs
        self.seed = random_state
        self.sample_weight_validation = sample_weight_validation
        self.estimator=estimator
        self.direction=direction

    def get_parameters(self, trial):
        params = deepcopy(self.parameters)
        for component, component_val in params.items():
            path=str(component)
            tunable=component_val["tunable"]
            path=path+".tunable"
            if tunable:
                for tuneable_key, tuneable_val in tunable.items():
                    if "type" in tuneable_val:
                        path2=tuneable_key
                        if tuneable_val["type"] == "categorical" and "values" in tuneable_val:
                            tuneable_val["value"] = trial.suggest_categorical(path2, tuneable_val["values"])
                        elif tuneable_val["type"] == "integer" and "values" in tuneable_val:
                            tuneable_val["value"] = trial.suggest_int(path2, low=tuneable_val["values"][0],
                                                                      high=tuneable_val["values"][-1])
                        elif tuneable_val["type"] == "integer" and "range" in tuneable_val:
                            tuneable_val["value"] = trial.suggest_int(path2, low=tuneable_val["range"][0],
                                                                      high=tuneable_val["range"][-1])
                        elif tuneable_val["type"] == "float" and "values" in tuneable_val:
                            tuneable_val["value"] = trial.suggest_float(path2, low=tuneable_val["values"][0],
                                                                       high=tuneable_val["values"][-1])
                        elif tuneable_val["type"] == "float" and "range" in tuneable_val:
                            tuneable_val["value"] = trial.suggest_float(path2, low=tuneable_val["range"][0],
                                                                       high=tuneable_val["range"][-1])

                    else:
                        tuneable_val["value"] = tuneable_val["value"]

        return params

    def __call__(self, trial):
        raise NotImplementedError



class EstimatorObjective(Objective):

    def get_estimator_parameters(self, original_params, trial, path=[]):

        for tuneable_key, tuneable_val in original_params.items():
            if len(path)==0 or path[-1]!=tuneable_key:
                path.append(tuneable_key)
            if isinstance(tuneable_val, dict):
                if "type" in tuneable_val and "values" in tuneable_val:
                    if tuneable_val["type"] in [ParamType.CATEGORICAL, "categorical"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_categorical('.'.join(path), tuneable_val["values"])
                    elif tuneable_val["type"] in [ParamType.INTEGER, "integer"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_int('.'.join(path), low=tuneable_val["values"][0],
                                                                  high=tuneable_val["values"][-1])
                    elif tuneable_val["type"] in [ParamType.RANGE, "float"]:
                        print(path)
                        tuneable_val["value"] = trial.suggest_float('.'.join(path), low=tuneable_val["values"][0],
                                                                    high=tuneable_val["values"][-1])
                elif isinstance(tuneable_val, dict):
                    self.get_estimator_parameters(tuneable_val, trial, path)
                else:
                    tuneable_val[tuneable_key] = tuneable_val["value"]
            elif isinstance(tuneable_val, list):
                for i, val in enumerate(tuneable_val):
                    if isinstance(val, dict):
                        path.append(str(i))
                        self.get_estimator_parameters(val, trial, path)
                    path.pop()
            if len(path)>0:
                path.pop()
        return original_params

    def __call__(self, trial):
        try:
            params=self.get_estimator_parameters(deepcopy(self.parameters), trial, path=[])


            model = class_from_module_path(class_name(self.estimator))(params)

            preds=cross_val_predict(model.model_type, self.X, self.y, cv=3, n_jobs=self.n_jobs)


            score = self.eval_metric(self.y, preds)
            if self.direction=='maximize':
                score *= -1.0

        except optuna.exceptions.TrialPruned as e:
            raise e
        except Exception as e:
            print("Exception in EstimatorObjective", str(e))
            if self.direction=="maximize":
                return -100000
            else:
                return 100000


        return score



class PipelineObjective(Objective):

    def __call__(self, trial):
        try:
            params=self.get_parameters(trial)


            pipeline = Pipeline.from_configs(params)


            X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size = 0.3, random_state = 42)


            pipeline.fit(X_train, y_train)
            pred=pipeline.predict(X_test)
            pred=[p['name'] for p in pred['label']]


            score = self.eval_metric(y_test, pred)
            if self.direction=='maximize':
                score *= -1.0

        except optuna.exceptions.TrialPruned as e:
            raise e
        except Exception as e:
            print("Exception in EstimatorObjective", str(e))
            if self.direction=="maximize":
                return -100000
            else:
                return 100000


        return score


