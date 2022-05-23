from kedro.pipeline import Pipeline, node
from .nodes import *


def create_pipeline():
    return Pipeline([
        node(
            func=predict,
            inputs=dict(instances="instances",
                        model="pipeline_inference_model"),
            outputs="predications_userapp",
            tags=["user_app"]
        )
    ])
