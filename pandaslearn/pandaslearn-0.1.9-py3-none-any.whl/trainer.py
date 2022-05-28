import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from pydantic import BaseModel
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

from .dataset import Dataset
from .loguru_handler import LoguruHandler
from .model import Model

# For both sweep() and train(), at the start of the routine
# TODO: SANITY-CHECK: for categorical variables, check if categories in train/test match, alert mismatches
# TODO: SANITY-CHECK: for features, check if columns in train/test match
# TODO: SANITY-CHECK: check if target role is specified and in train and not in test
# TODO: SANITY-CHECK: check if stratify role is specified and in train, alert if it is in test


class Trainer(BaseModel):
    run_id: str
    run_id_str: Optional[str]
    description: Optional[str]
    artefacts: Union[str, Path]
    paths: Optional[List[Path]]
    dataset: Dataset
    model: Model
    pipeline: Optional[Any]  # TODO: fix the type
    model_performance: Dict = {}
    log_cache: List[str] = []
    logger: Any = None

    class Config:
        arbitrary_types_allowed = True

    def add_to_log(self, message: str):
        self.log_cache += [message]

    def log(self, messages: Union[str, List[str]]):
        if isinstance(messages, str):
            messages = [messages]
        if self.logger is None:
            fns = [print, self.add_to_log]
        else:
            fns = [self.logger.logger.info]
        [[fn(message) for fn in fns] for message in messages]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.init_paths(self.run_id)
        self.init_logger()

        self.log(
            [
                f"Trainer instantiated, run_id: {self.run_id}, run_id_str: {self.run_id_str}",
                f"Trainer instantiated, paths: {self.paths}",
                f"Model instantiated, model_config: {self.model.model_config}",
                f"Model instantiated, fit_config: {self.model.fit_config}",
                f"Model instantiated, log_cache: {self.model.log_cache}",
                f"Dataset instantiated, root: {self.dataset.root}",
                f"Dataset instantiated, data, training_data: {self.dataset.describe()}",
                f"Dataset instantiated, roles: {self.dataset.roles.describe()}",
                f"Dataset instantiated, preprocessing_steps: {self.dataset.preprocessing_steps}",
                f"Dataset instantiated, log_cache: {self.dataset.log_cache}",
            ]
        )

    def init_paths(self, run_id: str):
        paths = {}
        run_id_str = (
            self.run_id
            + "_"
            + datetime.strftime(
                datetime.now(),
                "%Y%m%d-%H%M%S",
            )
        )
        paths["root"] = Path(self.artefacts) / run_id_str
        paths["root"].mkdir(parents=True, exist_ok=True)
        paths["trainer_path"] = paths["root"] / f"trainer_{run_id_str}.pkl"
        paths["pipeline_path"] = paths["root"] / f"pipeline_{run_id_str}.pkl"
        paths["submission_path"] = paths["root"] / f"submission_{run_id_str}.csv"
        paths["preds_path"] = paths["root"] / f"preds_{run_id_str}.npy"
        paths["oof_path"] = paths["root"] / f"oof_{run_id_str}.npy"
        paths["log_md_path"] = paths["root"] / f"log_{run_id_str}.md"
        paths["log_json_path"] = paths["root"] / f"log_{run_id_str}.json"
        self.paths = paths
        self.run_id_str = run_id_str
        return self

    def init_logger(self):
        self.logger = LoguruHandler(logger=logger)
        self.logger.add_logger()
        self.logger.add_logger(filename=self.paths["log_md_path"])
        self.logger.add_logger(filename=self.paths["log_json_path"])
        self.dataset.logger = self.logger
        self.model.logger = self.logger
        return self

    def serialize(self, savepath: Optional[Union[str, Path]] = None):
        # Check savepath is a folder
        if savepath is None:
            savepath_trainer = self.paths["trainer_path"]
            savepath_pipeline = self.paths["pipeline_path"]
        else:
            savepath_trainer = Path(savepath) / f"trainer_{self.run_id_str}.pkl"
            savepath_pipeline = Path(savepath) / f"pipeline_{self.run_id_str}.pkl"
        self.log(f"Saving Trainer instance to {savepath_trainer}")
        self.log(f"Saving pipeline to {savepath_pipeline}")
        self.logger = None
        self.dataset.logger = None
        self.model.logger = None
        joblib.dump(self, str(savepath_trainer))
        joblib.dump(self.pipeline, str(savepath_pipeline))
        self.init_logger()
        self.log(f"Finished saving Trainer instance to {savepath_trainer}")
        self.log(f"Finished saving pipeline to {savepath_pipeline}")
        return self

    def apply_sampling_strategy(self, *, sampling_strategy: str):
        if sampling_strategy is None:
            self.dataset.split_none()
        elif sampling_strategy == "default":
            self.dataset.split_default()
        elif sampling_strategy == "timeseries":
            self.dataset.split_timeseries()
        else:
            raise ValueError(
                f"Received wrong value for `sampling_strategy` ({sampling_strategy}). Allowed: `default`, `timeseries` or None!"
            )

        if sampling_strategy in ["default", "timeseries"]:
            eval_set = (
                self.dataset.training_data.X_validation,
                self.dataset.training_data.y_validation,
            )
            self.model.fit_config["model__eval_set"] = [eval_set]
            # TODO: Should I be storing eval_set inside .model.fit_config?
            # (it inflates the model size. store it inside trainer?)
            # TODO: May be have a separate Config class and store it in Trainer

        return self

    def sweep(
        self,
        *,
        trainer_config: Dict,
        sampling_strategy: str = "default",
    ):
        self.pipeline = Pipeline(steps=self.dataset.preprocessing_steps)
        self.apply_sampling_strategy(sampling_strategy=sampling_strategy)

        random_searcher = RandomizedSearchCV(self.model.model, **trainer_config)
        self.pipeline.steps.append(("model", random_searcher))

        start = time.time()
        self.pipeline.fit(
            self.dataset.training_data.X_train,
            self.dataset.training_data.y_train,
            **self.model.fit_config,
        )
        end = time.time()

        fi_tmp = pd.DataFrame()
        fi_tmp["feature"] = self.pipeline["model"].best_estimator_.feature_name_
        fi_tmp["importance"] = self.pipeline[
            "model"
        ].best_estimator_.feature_importances_
        self.model.importances = self.model.importances.append(fi_tmp)
        self.model.preds = self.pipeline.predict_proba(
            self.dataset.data.test[self.dataset.roles.features],
        )[:, -1]
        np.save(str(self.paths["preds_path"]), self.model.preds)

        self.model_performance = {
            "time_elapsed": end - start,
            "best_params": self.pipeline["model"].best_params_,
            "best_score": self.pipeline["model"].best_score_,
            "feature_importances": self.model.importances,
        }
        if sampling_strategy in ["default", "timeseries"]:
            self.model_performance["test_score"] = (
                self.pipeline.score(
                    self.dataset.training_data.X_validation,
                    self.dataset.training_data.y_validation,
                ),
            )
        print(self.model_performance)
        self.dataset.data.submission.loc[
            :, self.dataset.roles.target
        ] = self.model.preds
        self.dataset.data.submission.to_csv(self.paths["submission_path"], index=False)
        # TODO: create a separate create_submission function

        return self

    def sweep_optuna(
        self,
        *,
        trainer_config: Dict,
        sampling_strategy: str = "default",
    ):
        pass

    def predict(self, df: pd.DataFrame):
        preds = self.pipeline.predict(df)
        return preds

    def train(
        self,
        trainer_config: Dict,
        sampling_strategy: str = "default",
    ):
        # TODO: remove trainer_config? only picking up cv and random_state
        self.pipeline = Pipeline(steps=self.dataset.preprocessing_steps)
        self.apply_sampling_strategy(sampling_strategy=sampling_strategy)

        self.pipeline.steps.append(("model", self.model.model))

        X = (
            self.dataset.training_data.X_train
        )  # TODO: reset_index? or train_test_split() does it?
        y = pd.DataFrame({"claim": self.dataset.training_data.y_train})
        # TODO: train_test_split: is it converting df to np?
        features = sorted(self.dataset.roles.features)
        test = self.dataset.data.test  # TODO: test may not be available always

        skf = StratifiedKFold(
            n_splits=trainer_config["cv"],
            shuffle=True,
            random_state=trainer_config["random_state"],
        )
        stratify = self.dataset.training_data.X_train.loc[
            :, self.dataset.roles.stratify
        ]
        if (
            self.dataset.roles.stratify
            in self.dataset.training_data.X_train.columns.values
        ):
            stratify = self.dataset.training_data.X_train.loc[
                :, self.dataset.roles.stratify
            ]
        elif (
            self.dataset.roles.stratify
            in self.dataset.training_data.y_train.columns.values
        ):
            stratify = self.dataset.training_data.y_train.loc[
                :, self.dataset.roles.stratify
            ]
            # TODO: This won't work in multi-label setting
        for fold, (trn_idx, val_idx) in enumerate(
            skf.split(
                X=X,
                y=stratify,
                # TODO: y=y,
                # TODO: y=self.dataset.roles.stratify (index issues because original train-val split is not done on the stratification var, may be extract stratification var later)
                # May be I can go with str instead of pd.Series for stratify
                # Note: split should ideally be done on target variable?!
            )
        ):
            print(f"===== fold {fold} =====")
            X_train = X[features].iloc[trn_idx]
            y_train = y.iloc[trn_idx]
            X_valid = X[features].iloc[val_idx]
            y_valid = y.iloc[val_idx]
            X_test = test[features]  # TODO: test may not be available always

            start = time.time()

            self.pipeline.fit(
                X_train,
                y_train,
                # **self.model.fit_config,
            )
            # self.logger.logger.info(self.pipeline.transform(X_train).columns)
            # self.logger.logger.info(self.pipeline.transform(X_valid).columns)
            # self.logger.logger.info(self.pipeline.transform(X_test).columns)

            fi_tmp = pd.DataFrame()
            # # LGBM
            # if self.pipeline["model"].feature_name_ is not None:
            #     fi_tmp["feature"] = self.pipeline["model"].feature_name_
            # # XGBOOST
            # if self.pipeline["model"].get_booster is not None:
            #     fi_tmp["feature"] = self.pipeline["model"].get_booster().feature_names

            # fi_tmp["importance"] = self.pipeline["model"].feature_importances_
            # fi_tmp["fold"] = fold
            # fi_tmp["seed"] = 42

            self.model.importances = self.model.importances.append(fi_tmp)

            self.model.oof[val_idx] = self.pipeline.predict_proba(X_valid)[:, -1]
            self.model.oof_target[val_idx] = y_valid.iloc[:, 0].to_numpy()
            # TODO: Should y-vars always be pd.Series or np.array?
            self.model.preds += (
                self.pipeline.predict_proba(X_test)[:, -1] / trainer_config["cv"]
            )

            elapsed = time.time() - start
            auc = roc_auc_score(y_valid, self.model.oof[val_idx])
            print(f"fold {fold} - lgb auc: {auc:.6f}, elapsed time: {elapsed:.2f}sec\n")

        # print(f"oof lgb roc (on training) = {roc_auc_score(self.dataset.training_data.y_train, self.model.oof)}")
        print(
            f"(this is probably wrong) oof lgb roc (on training) = {roc_auc_score(self.dataset.data.train[self.dataset.roles.target], self.model.oof)}"
        )
        # print(f"oof lgb roc (on training) = {roc_auc_score(y, self.model.oof)}")

        np.save(str(self.paths["oof_path"]), self.model.oof)
        np.save(str(self.paths["preds_path"]), self.model.preds)

        # order = list(
        #     self.model.importances.groupby("feature")
        #     .mean()
        #     .sort_values("importance", ascending=False)
        #     .index
        # )

        # import matplotlib.pyplot as plt
        # import numpy as np
        # import seaborn as sns
        # fig = plt.figure(figsize=(16, 16), tight_layout=True)
        # sns.barplot(
        # x="importance",
        # y="feature",
        # data=lgb_importances.groupby("feature").mean().reset_index(),
        # order=order,
        # )
        # plt.title("LightGBM feature importances")
        self.dataset.data.submission.loc[
            :, self.dataset.roles.target
        ] = self.model.preds
        self.dataset.data.submission.to_csv(self.paths["submission_path"], index=False)
        return self
