import datetime
import gc
import os
import sys
import time
import traceback
import warnings
from copy import deepcopy
from kolibri.utils.common import infer_task_type
from kolibri.core.pipeline import Pipeline
from kolibri.core.component import Component
import numpy as np
import pandas as pd
from kolibri.preprocess.tabular.infer_datatype import AutoInferDatatype
from kolibri.preprocess.tabular.data_imputer import DataImputer, IterativeImputer
from kolibri.preprocess.tabular.zero_variance_remover import NearZeroVariance
from kolibri.preprocess.tabular.rare_levels import Catagorical_variables_With_Rare_levels
from kolibri.preprocess.tabular.reduce_cardinality import Reduce_Cardinality_with_Counts, Reduce_Cardinality_with_Clustering
from kolibri.preprocess.tabular.ordinal_transformer import Ordinal
from kolibri.preprocess.tabular.binning import Binning
from kolibri.preprocess.tabular.normalize import Normalizer
from kolibri.preprocess.tabular.time_features_extractor import TimeFeatures
from kolibri.preprocess.tabular.dummy_converter import DummyConverter
from kolibri.preprocess.tabular.outlier_remover import Outlier
from kolibri.preprocess.tabular.cluster import ClusterDataset
from kolibri.preprocess.tabular.feature_selection import Boruta_Feature_Selection, Advanced_Feature_Selection_Classic
from kolibri.preprocess.tabular.multicollinearity import Fix_multicollinearity, Fix_Perfect_collinearity
from kolibri.preprocess.tabular.reduce_dimensionality import DimensionalityReduction
from kolibri.config import TaskType
from kolibri.logger import get_logger
from kolibri.core.pipeline import Pipeline
from kdmt.dict import update

warnings.filterwarnings("ignore")

_available_plots = {}


logger=get_logger(__name__)



class DataPreprocessingPipeline(Pipeline, Component):
    defaults = {
        "fixed":{
            "categorical-features":[],
            "categorical-iterative-imputer": "lightgbm",
            "numerical-features" : [],
            "ordinal-features": [],
            "create-date-features": True,
            "time-features":[],
            "infer-datatypes":True,
            "train-tetst-split":0.7,
            "numeric-iterative-imputer": "lightgbm",
            "normalization-method": "zscore",
            "unknown_categorical_method": "least_frequent",
            "features-to-drop":[],
            "remove-multicollinearity": False,
            "multicollinearity-threshold":  0.9,
            "remove-perfect-collinearity": True,
            "create-clusters": False,
            "feature-selection": False,
            "feature-selection-method": "classic",
            "fix-imbalance-method": "",
            "transform-target-method": "box-cox",
            "dummify-categorical": True,
            "n_jobs": -1,
            "log-experiment": False,
            "experiment-name":  None,
            "dimentionality-reduction": False
        },
        "tunable":{
            "imputer": ["simple"],
            "imputer-categorical-strategy":{
                    "value":"most_frequent",
                    "type": "string",
                    "values":["constant", "most_frequent"]
            },
            "imputer-numeric-strategy": {
                "value":"mean"
            },
            "transformation_method": {
                "value":"yeo-johnson",
                "type": "string",
                "values":["yeo-johnson", "quantile"]
            },
            "pca-method": {
                "value":"linear",
                "type": "string",
                "values":[
                    "linear","kernel", "incremental","pls"
                ]
            },
            "pca-components":{"value": None,
                              "type": "float",
                              "values":[0,1]
                              },
            "combine_rare_levels": {"value":False},
            "remove-low-variance":{"value":True},
            "rare-level-threshold": {"value":0.10},
            "bin_numeric_features": {"value":False},
            "remove-outliers": {"value":False},
            "outliers-threshold": {"value":0.05},
            "feature-selection_threshold": {0.8},
            "high-cardinality-algorithm": {
                "value":"frequency",
                "type": "string",
                "values":[
                    "frequency", "clustering"
                ]
            }
        }

}
    

    def __init__(self, params):
     
        """
        preprocessing starts here
        """
        super(DataPreprocessingPipeline, self).__init__(parameters=params)

        logger.info("Declaring preprocessing parameters")
    
        self._do_infer_datatype =self.get_parameter("infer-datatypes", True)
        # categorical features
        self.cat_features = self.get_parameter("categorical-features", [])
    
        # numeric features
        self.numeric_features = self.get_parameter("numeric_features", [])
    
        # drop features
        self.ignore_features = self.get_parameter("features-to-drop", [])
    
        # date features
        self.date_features = self.get_parameter("date_features", [])

        self.ml_task=self.get_parameter("ml-task")
        apply_binning_pass = False if self.get_parameter("bin_numeric_features") is None else True
        self._do_features_to_bin = self.get_parameter("bin_numeric_features", [])

    
        # ordinal_features
        self._do_apply_ordinal_encoding = True if self.get_parameter("ordinal-features",[])!=[] else False

    
        self._do_apply_cardinality_reduction = (
            True if self.get_parameter("high-cardinality-features") is not None else False
        )


        self._do_normalize = self.get_parameter("normalize-method")!="none"

        # transform target method
        self._do_transform_target = self.get_parameter("transform_target")
        self._do_transform_target_method = self.get_parameter("transform-target-method")
    
        # create n_jobs_param
        self._n_jobs_param = self.get_parameter("n_jobs")

        self._do_zero_nearZero_variance=self.get_parameter("ignore_low_variance")
    
        self.imputation_regressor = self.get_parameter("numeric-iterative-imputer")
        self.imputation_classifier = self.get_parameter("categorical-iterative-imputer")
        if self.get_parameter("imputer") == "iterative":
            logger.info("Setting up iterative imputation")

            self.imputation_regressor=self.get_parameter("numerical-iterative-imputer")
            self.imputation_classifier=self.get_parameter("categorical-iterative-imputer")

        self.build_pipeline()


    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, DataPreprocessingPipeline.defaults)
        super().update_default_hyper_parameters()

    def build_pipeline(self):


        #infer data types
        dtypes=None
        if self.get_parameter("infer-datatypes"):
            dtypes= AutoInferDatatype(self.hyperparameters)

        #missing values imputation
        imputer=None
        if self.get_parameter("imputation-type") == "simple":
             imputer= DataImputer(self.defaults)
        elif self.get_parameter("imputation-type")=="iterative":
            imputer=IterativeImputer(self.hyperparameters)

        # remove zero orn near zero variance
        low_var=None
        if self._do_zero_nearZero_variance == True:
            low_var=NearZeroVariance(self.hyperparameters)

        # combine classes with low cardinality:
        rare_levels=None
        if self.get_parameter("combine_rare_levels") == True:
            rare_levels = Catagorical_variables_With_Rare_levels(self.hyperparameters)

        # cardinality:
        cardinality=None
        if self._do_apply_cardinality_reduction == True and self.get_parameter("high-cardinality-features") == "clustering":
            cardinality = Reduce_Cardinality_with_Clustering(self.hyperparameters)

        elif self._do_apply_cardinality_reduction == True and self.get_parameter("high-cardinality-features") == "frequency":
            cardinality = Reduce_Cardinality_with_Counts(self.hyperparameters)


        # ordinal coding
        ordinal=None
        if self._do_apply_ordinal_encoding == True:
            ordinal = Ordinal(self.hyperparameters)

        # binning
        binn=None
        if self._do_features_to_bin == True:
            binn = Binning(self.hyperparameters)


        # scaling & power transform
        scaling=None
        if self._do_normalize == True:
            scaling = Normalizer(self.hyperparameters )

        # for Time Variables
        feature_time=None
        if self.get_parameter("create-date-features") and self.get_parameter("ordinal-features")!=[]:
            feature_time = TimeFeatures(self.hyperparameters)
        dummy=None
        if self.get_parameter("dummify-categorical") == True:
            dummy = DummyConverter(self.hyperparameters)


        # remove putliers
        outliers=None
        if self.get_parameter("remove-outliers") == True:
            outliers = Outlier(self.hyperparameters)


        # cluster all data:
        cluster_all=None
        if self.get_parameter("create-clusters") == True:
            cluster_all = ClusterDataset(self.hyperparameters)


        # feature selection
        feature_select=None
        if self.get_parameter("feature-selection"):
            # TODO: add autoselect
            if self.get_parameter("feature-selection-method") == "boruta":
                feature_select = Boruta_Feature_Selection(self.hyperparameters)
            else:
                feature_select = Advanced_Feature_Selection_Classic(self.hyperparameters)


        # removing multicollinearity
        fix_multi=None
        if self.get_parameter("remove-multicollinearity") == True:
            if self.ml_task !=TaskType.MULTI_TARGET_CLASSIFICATION and self.ml_task !=TaskType.MULTI_TARGET_REGRESSION:
                fix_multi = Fix_multicollinearity(self.hyperparameters)
            else:
                fix_multi = Fix_multicollinearity(self.hyperparameters)


        # remove 100% collinearity
        fix_perfect=None
        if self.get_parameter("remove-perfect-collinearity") == True:
            fix_perfect = Fix_Perfect_collinearity(self.hyperparameters)

        # apply pca
        dim_reduction=None
        if self.get_parameter("dimentionality-reduction"):
            dim_reduction = DimensionalityReduction(self.hyperparameters)

        self.add_steps([tuple for tuple in [
                ("dtypes", dtypes),
                ("imputer", imputer),
                ("ordinal", ordinal),
                ("cardinality", cardinality),
                ("low_var", low_var),
                ("rare_levels", rare_levels),
                ("feature_time", feature_time),
                ("scaling", scaling),
                ("binn", binn),
                ("rem_outliers", outliers),
                ("cluster_all", cluster_all),
                ("dummy", dummy),
                ("fix_perfect", fix_perfect),
                ("feature_select", feature_select),
                ("fix_multi", fix_multi),
                ("dim_reduction", dim_reduction),
            ] if tuple[1] is not None])

    def log_experiment(self):

        # determining target type
        if _is_multiclass(self.get_parameter("task-type")):
            target_type = "Multiclass"
        else:
            target_type = "Binary"

        # generate values for grid show
        missing_values = X_train.isna().sum().sum()
        missing_flag = True if missing_values > 0 else False

        normalize_grid = self.get_parameter("normalize-method")

        transformation_grid = self.get_parameter("transformation_method")

        pca_method_grid = self.get_parameter("pca_method")

        pca_components_grid = self.get_parameter("pca")

        rare_level_threshold_grid = self.get_parameter("rare_level_threshold")

        numeric_bin_grid = False if self.get_parameter("bin_numeric_features") is None else True

        outliers_threshold_grid = self.get_parameter("outliers_threshold") if self.get_parameter(
            "remove_outliers") else None

        multicollinearity_threshold_grid = (
            self.get_parameter("multicollinearity-threshold") if self.get_parameter(
                "remove-multicollinearity") else None
        )

        polynomial_degree_grid = self.get_parameter("polynomial_degree") if self.get_parameter(
            "polynomial_features") else None

        feature_selection_threshold_grid = (
            self.get_parameter("feature-selection_threshold") if self.get_parameter("feature-selection") else None
        )

        ordinal_features_grid = False if self.get_parameter("ordinal-features") is None else True

        group_features_grid = False if self.get_parameter("group_features") is None else True

        high_cardinality_features_grid = (
            False if self.get_parameter("high-cardinality-features") is None else True
        )

        high_cardinality_method_grid = (
            self.get_parameter("high-cardinality-algorithm") if high_cardinality_features_grid else None
        )

        exp_name_dict = {
            TaskType.CLASSIFICATION: "clf-default-name",
            TaskType.REGRESSION: "reg-default-name",
            TaskType.CLUSTERING: "cluster-default-name",
            TaskType.ANOMALY: "anomaly-default-name",
        }

        float_type = 0
        cat_type = 0

        for i in dtypes.learned_dtypes:
            if "float" in str(i):
                float_type += 1
            elif "object" in str(i):
                cat_type += 1
            elif "int" in str(i):
                float_type += 1

        if self.get_parameter("experiment-name") is None:
            exp_name_ = exp_name_dict[self.get_parameter("task-type")]
        else:
            exp_name_ = self.get_parameter("experiment-name")

        exp_name_log = exp_name_

        functions = pd.DataFrame(
            [["session", self.get_parameter("random-state")], ]
            + ([["Target", target]] if not _is_unsupervised(self.get_parameter("task-type")) else [])
            + (
                [["Target Type", target_type], ["Label Encoded", label_encoded], ]
                if self.get_parameter("task-type") == TaskType.CLASSIFICATION
                else []
            )
            + [
                ["Original Data", data_before_preprocess_shape],
                ["Missing Values", missing_flag],
                ["Numeric Features", str(float_type)],
                ["Categorical Features", str(cat_type)],
            ]
            + (
                [
                    ["Ordinal Features", ordinal_features_grid],
                    ["High Cardinality Features", high_cardinality_features_grid],
                    ["High Cardinality Method", high_cardinality_method_grid],
                ]
            )
            + (
                [
                    ["Transformed Train Set", X_train.shape],
                    ["Transformed Test Set", X_test.shape],
                    ["Shuffle Train-Test", str(self.get_parameter("data-split-shuffle"))],
                    ["Stratify Train-Test", str(data_split_stratify)],
                    ["Fold Generator", type(fold_generator).__name__],
                    ["Fold Number", fold_param],
                ]
                if not _is_unsupervised(self.get_parameter("task-type"))
                else [["Transformed Data", X.shape]]
            )
            + [

                ["Log Experiment", logging_param],
                ["Experiment Name", exp_name_],

            ]
            + (
                [
                    ["Imputation Type", imputation_type],
                    [
                        "Iterative Imputation Iteration",
                        iterative_imputation_iters_param
                        if imputation_type == "iterative"
                        else "None",
                    ],
                    ["Numeric Imputer", numeric_imputation],
                    [
                        "Iterative Imputation Numeric Model",
                        imputation_regressor_name
                        if imputation_type == "iterative"
                        else "None",
                    ],
                    ["Categorical Imputer", categorical_imputation],
                    [
                        "Iterative Imputation Categorical Model",
                        imputation_classifier_name
                        if imputation_type == "iterative"
                        else "None",
                    ],
                    ["Unknown Categoricals Handling", unknown_categorical_method_grid],
                    ["Normalize", normalize],
                    ["Normalize Method", normalize_grid],
                    ["Transformation", transformation],
                    ["Transformation Method", transformation_grid],
                    ["PCA", pca],
                    ["PCA Method", pca_method_grid],
                    ["PCA Components", pca_components_grid],
                    ["Ignore Low Variance", ignore_low_variance],
                    ["Combine Rare Levels", combine_rare_levels],
                    ["Rare Level Threshold", rare_level_threshold_grid],
                    ["Numeric Binning", numeric_bin_grid],
                    ["Remove Outliers", remove_outliers],
                    ["Outliers Threshold", outliers_threshold_grid],
                    ["Remove Multicollinearity", remove_multicollinearity],
                    ["Multicollinearity Threshold", multicollinearity_threshold_grid],
                    ["Remove Perfect Collinearity", remove_perfect_collinearity],
                    ["Clustering", create_clusters],
                    ["Clustering Iteration", cluster_iter_grid],
                    ["Polynomial Features", polynomial_features],
                    ["Polynomial Degree", polynomial_degree_grid],
                    ["Trignometry Features", trigonometry_features],
                    ["Polynomial Threshold", polynomial_threshold_grid],
                    ["Group Features", group_features_grid],
                    ["Feature Selection", feature_selection],
                    ["Feature Selection Method", feature_selection_method],
                    ["Features Selection Threshold", feature_selection_threshold_grid],
                    ["Feature Interaction", feature_interaction],
                    ["Feature Ratio", feature_ratio],
                    ["Interaction Threshold", interaction_threshold_grid],
                ]

            )
            + (
                [
                    ["Fix Imbalance", fix_imbalance_param],
                    ["Fix Imbalance Method", fix_imbalance_model_name],
                ]
                if self.get_parameter("task-type") == TaskType.CLASSIFICATION
                else []
            )
            + (
                [
                    ["Transform Target", transform_target_param],
                    ["Transform Target Method", transform_target_method_param],
                ]
                if self.get_parameter("task-type") == TaskType.REGRESSION
                else []
            ),
            columns=["Description", "Value"],
        )

        """
        Final display Ends
        """

        # log into experiment
        experiment__.append(("Setup Config", functions))
        if not _is_unsupervised(self.get_parameter("task-type")):
            experiment__.append(("X_training Set", X_train))
            experiment__.append(("y_training Set", y_train))
            experiment__.append(("X_test Set", X_test))
            experiment__.append(("y_test Set", y_test))
        else:
            experiment__.append(("Transformed Data", X))
        experiment__.append(("Transformation Pipeline", prep_pipe))

        # end runtime
        runtime_end = time.time()
        runtime = np.array(runtime_end - runtime_start).round(2)


from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(DataPreprocessingPipeline.name, DataPreprocessingPipeline)