from kedro.pipeline import node, pipeline
from .nodes import *


def create_pipeline(**kwargs):
    return pipeline(
        [
            node(
                func=move_market_ohlc_to_model_data,
                inputs=dict(orig_data="raw_market_data",
                            start="params:start_datetime",
                            end="params:end_datetime"),
                outputs=dict(instances="instances",),
                name="moving_data",
            )
        ]
    )