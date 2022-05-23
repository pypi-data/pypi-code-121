from kolibri.core import modules
from kolibri.logger import get_logger
import datetime
import numpy as np
try:
    import tensorflow as tf
except:
    pass

from kolibri.metadata import Metadata
from kolibri.core.pipeline import Pipeline
from kdmt.file import create_dir
from kdmt.objects import module_path_from_object
from pathlib import Path
from kolibri.core.modules import validate_requirements
from kolibri.optimizers.optuna.objective import PipelineObjective
from kolibri.utils.parallel import create_dask_client, close_dask_client
import os
import pandas as pd
import psutil, shutil
import uuid
from kolibri.optimizers.optuna.tuner import OptunaTuner
import time
from kolibri.config import ModelConfig, is_unsupervised
from kolibri.utils.common import get_target_type
from kolibri.utils.config import get_parameter_from_config
from kolibri.config import TaskType
logger = get_logger(__name__)

MINIMUM_COMPATIBLE_VERSION = "0.0.1"


class ModelTrainer(object):
    """Trainer will load the texts and train all components.

    Requires a pipeline specification and configuration to use for
    the training."""

    SUPPORTED_LANGUAGES = ["fr", "en", "nl"]

    config={
        'save-evaluation-output': True,
        'evaluate-performance': False,
        'max-time-for-learner': 3600,
        'max-time-for-optimization': 3600,
        'random-state': 42,
        'track-experiments':False,
        'experiment-name': 'experiment_1',
        'ml-task': None,
        'explain-level': 2,
        'opt-metric-name': 'f1-score',
        'optimize-pipeline': False,
        'optimizer': 'optuna',
        'output-folder': '.',
        'n-jobs': -1,
        'log-data':True,
        'log-data-profile':True,
        'log-model':True,
        'combine-rare-classes': False,
        'rare-classes-name': 'Other',
        'rare-classes-threshold': 10,
        'log-experiment':False,
        'log-experiment-location': None,
        'log-cross-validated-data':True,
        "experiment_custom_tags":None,
        'log-plots': False,
        'log-plot-location': None

    }

    def __init__(self, params, skip_validation=False):

        self._dask_client=None
        self.override_default_parameters(params.as_dict())

        if psutil.cpu_count()>1 and(self.config['n-jobs']>1 or  self.config['n-jobs']==-1):
            self._dask_client=create_dask_client(cpu_count = self.config['n-jobs'] if self.config['n-jobs'] > 1 else psutil.cpu_count() if self.config[
                                                                                                  'n-jobs'] == -1 else 1)
        if self.config['evaluate-performance']==False:
            self.config['save-evaluation-output']=False

        if self.config['save-evaluation-output']==True:
            try:
                import openpyxl
            except:
                raise Exception("The library 'openpyxl' in not installed. To save evaluation result, You must install 'openpyxl' or chaange 'save-evaluation-output' to False")
        logger.debug("ModelTrainer.__init__")
        self.uid = str(uuid.uuid4())
        if not isinstance(params, ModelConfig):
            raise ValueError("Config erro: Configuration object is not of type ModelConfig")

        for i in ["pipeline", "model"]:  # mandatory parameters
            if i not in params:
                msg = "Missing '{0}' parameter in Model Trainer params".format(i)
                logger.error(msg)
                raise ValueError(msg)

        self._explain_level = params.get("explain-level")

        self.train_time = None
        self.final_loss = None
        self.metric_name = None
        self._threshold = None  #for binary classifiers

        # the automl random state from AutoML constructor, used in Optuna optimizer
        self._random_state = params.get("random-state")


#        self.config



        # Before instantiating the component classes, lets check if all
        # required packages are available
        if not skip_validation:
            validate_requirements(params['pipeline'])
        self.performance_data=None
        # build pipeline

        self.pipeline = self._build_pipeline(params)

        self.all_params=self.pipeline.parameters

    @staticmethod
    def _build_pipeline(params):
        """Transform the passed names of the pipeline components into classes"""

        steps = []
        # Transform the passed names of the pipeline components into classes
        for component_name in params['pipeline']:
            component = modules.create_component_by_name(
                component_name, params)
            steps.append((component_name, component))

        return Pipeline(steps)


    def fit_transformers(self, X, y, X_val=None, y_val=None):
        return self.pipeline.fit_transformers(X, y, X_val, y_val)

    def fit_estimator(self, X, y, X_val=None, y_val=None):
        self.pipeline.fit_estimator(X, y, X_val, y_val)

        return self.pipeline.estimator


    def fit(self, X, y, X_val=None, y_val=None):
        """Trains the underlying pipeline using the provided training texts."""
        logger.debug(f"ModelTrainer.fit {self.config.get('models')}")
        if type(X).__module__ == np.__name__:
            self.original_data=pd.DataFrame(np.vstack((X,y)).T)


        start_time = time.time()
        if self.config.get('optimize-pipeline'):
            logger.debug(f"ModelTrainer.fit - optimizing pipeline")
            self.optimize(X, y)
        try:
            self.pipeline.fit(X, y, X_val, y_val)
        except:
            self.pipeline.fit(X, y)


        if self.config['save-evaluation-output']==True and self.pipeline.estimator.validatation_data is not None:
            self.performance_data=pd.DataFrame(X)
            self.performance_data['class']=y
            self.performance_data['prediction']=self.pipeline.estimator.validatation_data[:,0]
            self.performance_data['probability']=self.pipeline.estimator.validatation_data[:,1]

        self.train_time=time.time()-start_time
        close_dask_client(self._dask_client)
        self._log_experiment(self.config['track-experiments'], X, y, X_val, y_val)
        return self.pipeline

    def objective(self, X, y):
        objective=PipelineObjective(X, y, self.pipeline, None, eval_metric=self.config['opt-metric-name'],n_jobs=-1, random_state=42)
        return objective


    def optimize(self, X, y):
        try:
            optimizer = OptunaTuner(
                    self.config['output-folder'],
                    eval_metric=self.config['opt-metric-name'],
                    time_budget=self.config['max-time-for-optimization'],
                    init_params={},
                    verbose=True,
                    n_jobs=-1,
                    random_state=self.config['random-state'],
                )

            start_time = time.time()
            self.hyperparameters = optimizer.optimize(
                objective=self.objective(X, y),
                learner_params=self.pipeline.parameters
            )
            self.optimization_time=time.time()-start_time


        except Exception as e:
            raise Exception('Could not optimize model. Exception raised: '+str(e))

    def override_default_parameters(self, custom):

        if custom:
            if isinstance(custom, dict):
                for key in self.config:
                    v= custom.get(key,None )
                    if v:
                        self.config[key]=v

    def _log_experiment(self, logging_param, X_train, y_train, X_test, y_test):
        if logging_param:
            import secrets
            USI = secrets.token_hex(nbytes=2)
            logger.info(f"USI: {USI}")

            pipe_profile = pd.DataFrame(
                [
                    ["session_id", self.config["random-state"]],
                ]
                + ([["Target", self.config["target"]]] if "target" in self.config else [])
                + (
                    [
                        ["Target Type", get_target_type(pd.Series(y_train))],
                    ]
                    if not is_unsupervised(get_parameter_from_config(self.all_params,"task-type",None))
                    else []
                )
                + [
                    ["Original Data", self.original_data.shape],
                    ["Missing Values", self.original_data.isna().sum().sum()],
                    # ["Numeric Features", str(float_type)],
                    # ["Categorical Features", str(cat_type)],
                ]
                # + (
                #     [
                #         ["Ordinal Features", ordinal_features_grid],
                #         ["High Cardinality Features", high_cardinality_features_grid],
                #         ["High Cardinality Method", high_cardinality_method_grid],
                #     ]
                # )
                + (
                    [
                        ["Transformed Train Set",np.array(X_train).shape],
                        ["Transformed Test Set",np.array(X_test).shape],
                        ["Shuffle Train-Test",
                         str(get_parameter_from_config(self.all_params, "fold-shuffle", default=False))],
                        ["Stratify Train-Test", str(get_parameter_from_config(self.all_params,"data-split-stratify", default=False))],
                        ["Fold Number", get_parameter_from_config(self.all_params,"fold", default=None)],
                    ]
                    if not is_unsupervised(get_parameter_from_config(self.all_params,"task-type"))
                    else [["Transformed Data", np.array(X_train).shape]]
                )
                + [
                    ["CPU Jobs", self.config["n-jobs"]],
                    ["Use GPU", len(tf.config.list_physical_devices('GPU'))],
                    ["Log Experiment", logging_param],
                    ["Experiment Name", self.config["experiment-name"]],
                    ["USI", USI],
                ]
                + (
                    [
                        ["Imputation Type", get_parameter_from_config(self.all_params,"imputation-type", default=4)  ],
                        ["Normalize",  get_parameter_from_config(self.all_params, "normalization-method", None) is not None],
                        ["Normalize Method", get_parameter_from_config(self.all_params, "normalization-method", None)],
                        ["Dimensionality Reduction", get_parameter_from_config(self.all_params, "pca-method", None) is not None],
                        ["Dimensionality Reduction Method", get_parameter_from_config(self.all_params, "pca-method", None)],
                        ["PCA Components", get_parameter_from_config(self.all_params, "pca-components", 0)],
                        ["Ignore Low Variance", 'NearZeroVariance' in list(self.all_params.keys())],
                        ["Combine Rare Levels", 'Catagorical_variables_With_Rare_levels'  in list(self.all_params.keys())],
                        ["Rare Level Threshold", get_parameter_from_config(self.all_params, "rare-level-threshold", None)],
                        ["Numeric Binning", 'Binning' in list(self.all_params.keys())],
                        ["Remove Outliers", 'Outlier' in list(self.all_params.keys())],
    #                    ["Outliers Threshold", outliers_threshold_grid],
                        ["Remove Multicollinearity", 'Fix_multicollinearity' in list(self.all_params.keys())],
                        ["Multicollinearity Threshold",  get_parameter_from_config(self.all_params, "colinearity-threshold", None)],
                        ["Remove Perfect Collinearity", get_parameter_from_config(self.all_params, "correlation-with-target-threshold", 0)==1],
                        ["Clustering", 'ClusterDataset' in list(self.all_params.keys())],
                        ["Group Features", "Reduce_Cardinality_with_Clustering"  in list(self.all_params.keys())],
                        ["Feature Selection", "Advanced_Feature_Selection_Classic"  in list(self.all_params.keys())],
                        ["Top Features Selected", get_parameter_from_config(self.all_params,"top-features-to-pick", None)],
                    ]
                )
                + (
                    [
                        ["Fix Imbalance", get_parameter_from_config(self.all_params, "sampler", None) is not None],
                        ["Fix Imbalance Method", get_parameter_from_config(self.all_params, "sampler", "")],
                    ]
                    if not is_unsupervised(get_parameter_from_config(self.all_params, "task-type"))
                    else []
                )
                + (
                    [
                        ["Transform Target", get_parameter_from_config(self.all_params,"transform-target-method", None) is not None],
                        ["Transform Target Method", get_parameter_from_config(self.all_params,"transform-target-method", "")],
                    ]
                    if get_parameter_from_config(self.all_params, "task-type") == TaskType.REGRESSION
                    else []
                ),
                columns=["Description", "Value"]
            )

            logger.info("Logging experiment in MLFlow")

            import mlflow

            try:
                mlflow.create_experiment(self.config["experiment-name"])
            except:
                logger.warning("Couldn't create mlflow experiment. Exception:")


            # mlflow logging
            mlflow.set_experiment(self.config["experiment-name"])

            run_name_ = f"Session Initialized {USI}"

            mlflow.end_run()
            mlflow.start_run(run_name=run_name_)

            # Get active run to log as tag
            RunID = mlflow.active_run().info.run_id

            k = pipe_profile.copy()
            k.set_index("Description", drop=True, inplace=True)
            kdict = k.to_dict()
            params = kdict.get("Value")
            mlflow.log_params(params)

            # set tag of compare_models
            mlflow.set_tag("Source", "setup")

            # set custom tags if applicable
            if isinstance(self.config["experiment_custom_tags"], dict):
                mlflow.set_tags(self.config["experiment_custom_tags"])

            import secrets

            URI = secrets.token_hex(nbytes=4)
            mlflow.set_tag("URI", URI)
            mlflow.set_tag("USI", USI)
            mlflow.set_tag("Run Time", self.get_train_time())
            mlflow.set_tag("Run ID", RunID)

            # Log pandas profile
            if self.config["log-data-profile"]:
                import pandas_profiling

                pf = pandas_profiling.ProfileReport( self.original_data)
                pf.to_file("Data_Profile.html")
                mlflow.log_artifact("Data_Profile.html")
                os.remove("Data_Profile.html")

            # Log training and testing set
            if self.config["log-data"]:
                if not is_unsupervised(self.config["ml-task"]):
                    self.original_data.to_csv("Train.csv")
                    if X_test is not None:
                        pd.DataFrame(np.vstack((X_test, y_test)).T).to_csv("Test.csv")
                        mlflow.log_artifact("Test.csv")
                        os.remove("Test.csv")
                    mlflow.log_artifact("Train.csv")

                    os.remove("Train.csv")

                else:
                    X_train.to_csv("Dataset.csv")
                    mlflow.log_artifact("Dataset.csv")
                    os.remove("Dataset.csv")
            if self.config['log-model']:
                self.persist(self.config['output-folder'], self.config["experiment-name"])
                model_file=os.path.join(self.config['output-folder'], self.config["experiment-name"]+".tgz")
                mlflow.log_artifact(model_file)
                os.remove(model_file)
            if self.config['log-cross-validated-data'] and self.performance_data is not None:
                validated_data_file=os.path.join(self.config['output-folder'], 'validatation_data_.xlsx')
                self.performance_data.to_excel(validated_data_file)
                mlflow.log_artifact(validated_data_file)
                os.remove(validated_data_file)

    def get_train_time(self):
        return self.train_time

    def persist(self, path, fixed_model_name=None):
        """Persist all components of the pipeline to the passed path.

        Returns the directory of the persisted model."""


        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        metadata = {
            "pipeline": [],
        }

        if fixed_model_name:
            model_name = fixed_model_name
        else:
            model_name = "model_" + timestamp

        path = Path(path).resolve()
        dir_name = os.path.join(path, model_name)

        create_dir(dir_name)

        #        if self.training_data:
        #            metadata.update(self.training_data.persist(dir_name))

        for component in self.pipeline.steps.values():
            update = component.persist(dir_name)
            component_meta = component.hyperparameters
            if update:
                component_meta.update(update)
            component_meta["label"] = module_path_from_object(component)
            component_meta["name"] = component.name

            metadata["pipeline"].append(component_meta)

        Metadata(metadata, dir_name).persist(dir_name)


        if self.performance_data is not None:
            self.performance_data.to_excel(os.path.join(path, 'validatation_data_.xlsx'))
        import tarfile
        tar = tarfile.open(dir_name+".tgz", "w:gz")
        tar.add(dir_name, arcname=fixed_model_name)
        tar.close()
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
        logger.info("Successfully saved model into "
                    "'{}'".format(os.path.abspath(dir_name)))
        return dir_name



