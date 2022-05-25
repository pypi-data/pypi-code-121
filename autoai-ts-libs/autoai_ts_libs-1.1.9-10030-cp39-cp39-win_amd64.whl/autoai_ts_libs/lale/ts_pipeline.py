# Copyright 2020 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from autoai_ts_libs.utils.ts_pipeline import (  # type: ignore # noqa
    TSPipeline as model_to_be_wrapped,
)

import lale.docstrings
import lale.operators


class _TSPipelineImpl:
    def __init__(self, steps, feature_columns=[], target_columns=[], prediction_horizon=1, **kwargs):
        self._wrapped_model = model_to_be_wrapped(
            steps=steps,
            feature_columns=feature_columns,
            target_columns=target_columns,
            prediction_horizon=prediction_horizon,
            **kwargs)

    def fit(self, X, y=None, **fit_params):
        self._wrapped_model.fit(X, y, **fit_params)
        return self

    def predict(self, X=None, **predict_params):
        return self._wrapped_model.predict(X, **predict_params)


_hyperparams_schema = {
    "allOf": [
        {
            "description": "This first object lists all constructor arguments with their types, but omits constraints for conditional hyperparameters.",
            "type": "object",
            "additionalProperties": True,
            "required": ["steps", "feature_columns", "target_columns", "prediction_horizon"],
            "relevantToOptimizer": [],
            "properties": {
                "steps": {
                    "description": "The pipeline steps.",
                    "type": "array",
                    "items": {"laleType": "Any"},
                },
                "feature_columns": {
                    "description": """""",
                    "anyOf": [{"type": "array", "items": {"type": "integer"}}, {"enum": [None]}],
                    "default": [],
                },
                "target_columns": {
                    "description": """Column indices for columns to be forecasted.""",
                    "anyOf": [{"type": "array", "items": {"type": "integer"}}, {"enum": [None]}],
                    "default": [],
                },
                "prediction_horizon": {
                    "description": "The number of time points to predict into the future. The estimator(s) will be trained to predict all of these time points.",
                    "type": "integer",
                    "default": 1,
                },
            },
        }
    ]
}

_input_fit_schema = {
    "type": "object",
    "required": ["X"],
    "additionalProperties": False,
    "properties": {
        "X": {  # Handles 1-D arrays as well
            "anyOf": [
                {"type": "array", "items": {"laleType": "Any"}},
                {
                    "type": "array",
                    "items": {"type": "array", "items": {"laleType": "Any"}},
                },
            ]
        },
        "y": {"laleType": "Any"},
    },
}

_input_predict_schema = {
    "type": "object",
    "required": ["X"],
    "additionalProperties": False,
    "properties": {
        "X": {  # Handles 1-D arrays as well
            "anyOf": [
                {"type": "array", "items": {"laleType": "Any"}},
                {
                    "type": "array",
                    "items": {"type": "array", "items": {"laleType": "Any"}},
                },
            ]
        }
    },
}

_output_predict_schema = {
    "description": "Features; the outer array is over samples.",
    "anyOf": [
        {"type": "array", "items": {"laleType": "Any"}},
        {
            "type": "array",
            "items": {"type": "array", "items": {"laleType": "Any"}},
        },
    ],
}

_combined_schemas = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": """Operator from `autoai_ts_libs`_.
.. _`autoai_ts_libs`: https://pypi.org/project/autoai-ts-libs""",
    "documentation_url": "https://lale.readthedocs.io/en/latest/modules/autoai_ts_libs.lale.ts_pipeline.html",
    "import_from": "autoai_ts_libs.utils.ts_pipeline",
    "type": "object",
    "tags": {"pre": [], "op": ["classifer", "regressor", "estimator"], "post": []},
    "properties": {
        "hyperparams": _hyperparams_schema,
        "input_fit": _input_fit_schema,
        "input_predict": _input_predict_schema,
        "output_predict": _output_predict_schema,
    },
}

TSPipeline = lale.operators.make_operator(_TSPipelineImpl, _combined_schemas)
lale.docstrings.set_docstrings(TSPipeline)
