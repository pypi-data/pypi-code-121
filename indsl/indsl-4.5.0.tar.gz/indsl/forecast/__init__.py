# Copyright 2021 Cognite AS
from .arma_predictor import arma_predictor
from .holt_winters_predictor import holt_winters_predictor


TOOLBOX_NAME = "Forecast"

__all__ = ["arma_predictor", "holt_winters_predictor"]
