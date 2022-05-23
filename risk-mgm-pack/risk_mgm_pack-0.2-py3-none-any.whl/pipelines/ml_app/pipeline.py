from kedro.pipeline import Pipeline, node
from .nodes import *


def create_pipeline():
    return Pipeline([
        node(
            func=create_random_alpha,
            inputs=dict(ohlc="ohlc",
                        ),
            outputs=dict(alphas="model_alphas"),
            tags=["alphas"]
        ),
        node(
            func=create_features_targets,
            inputs=dict(instances="instances",
                        model_alphas="model_alphas",
                        target_ind_params="params:target_ind_params",
                        feature_ind_params="params:feature_ind_params",
                        lag_ind_params="params:lag_ind_params",
                        ),
            outputs=dict(features="features",
                         targets="targets"),
            tags=["searching", "benchmarking"]
            # tags=["benchmarking"]
    ),

        node(
            func=run_cross_validation,
            inputs=dict(features="features",
                        targets="targets",
                        cv_search_params="params:cv_search_params",
                        search_params="params:search_params",
                        metrics="params:metrics",
                        ),
            outputs=dict(search_result="search_result"),
            tags=["searching"]
        ),
        node(
            func=benchmark_best_model,
            inputs=dict(features="features",
                        targets="targets",
                        best_params="params:best_params",
                        benchmark_cv_params="params:benchmark_cv_params",
                        metrics="params:metrics",
                        ),
            outputs=dict(benchmark_result="benchmark_result"),
            tags=["benchmarking"]
        ),
        node(
            func=train_predict_best_params,
            inputs=dict(instances="instances",
                        target_ind_params="params:target_ind_params",
                        feature_ind_params="params:feature_ind_params",
                        lag_ind_params="params:lag_ind_params",
                        best_params="params:best_params",
                        benchmark_cv_params="params:benchmark_cv_params"
                        ),
            outputs=dict(prediction_result="prediction_result"),
            name="train_predict_best_params",
            tags=["benchmarking"]
        ),
        node(
            func=create_alpha,
            inputs=dict(instances="instances",
                        prediction_result="prediction_result"
                        ),
            outputs=dict(alphas="alphas"),
            name="create_alphas",
            tags=["benchmarking"]
        ),
        node(
            func=train_best_model_to_deploy,
            inputs=dict(instances="instances",
                        target_ind_params="params:target_ind_params",
                        feature_ind_params="params:feature_ind_params",
                        lag_ind_params="params:lag_ind_params",
                        best_params="params:best_params",
                        final_train_len="params:final_train_len"
                        ),
            outputs=dict(best_model="best_model"),
            name="training_name",
            tags=["training"]
        ),
        node(
            func=inference_model,
            inputs=dict(instances="instances", 
                        best_model="best_model",
                        lag_ind_params="params:lag_ind_params",
                        ),
            outputs="inference_result",
            name="inference_userapp",
            tags=["inference"]
        )
    ])
