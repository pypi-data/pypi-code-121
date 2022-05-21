import pandas as pd

def create_quantile_alphas(instances: pd.DataFrame, prediction_result: pd.DataFrame, quantile_threshold) -> pd.DataFrame:
    """
    - based on prediction result and quantile threshold (symeteric), creates +1, 0, -1 signals
    - returns columns with Prediction (the same as input) + Signal (+1, 0, -1)
    """

    assert len(prediction_result.columns) == 1, "prediction has more than one column"
    assert 0 < quantile_threshold < 1, f"quantiles need to be between 0 and 1, provided: {quantile_threshold}"

    alphas = prediction_result.copy()
    alphas.columns = ["Prediction"]

    alphas = alphas[alphas.index.isin(prediction_result.index)]
    alphas = pd.concat([alphas, instances], axis=1)

    # todo: just dropped na
    alphas = alphas.dropna()

    alphas["Signal"] = 0
    quant_low = quantile_threshold
    quant_high = 1 - quantile_threshold

    low = alphas["Prediction"].quantile(quant_low)
    high = alphas["Prediction"].quantile(quant_high)

    alphas.loc[alphas["Prediction"] < low, "Signal"] = -1
    alphas.loc[alphas["Prediction"] > high, "Signal"] = 1

    return alphas

def create_absolute_prediction_alphas(instances: pd.DataFrame, prediction_result: pd.DataFrame) -> pd.DataFrame:
    """
    - use the prediction as alpha signal
    """
    assert len(prediction_result.columns) == 1, "prediction has more than one column"

    alphas = prediction_result.copy()
    alphas.columns = ["Prediction"]

    alphas = alphas[alphas.index.isin(prediction_result.index)]
    alphas = pd.concat([alphas, instances], axis=1)

    # todo: just dropped na
    alphas = alphas.dropna()

    alphas["Signal"] = alphas["Prediction"]
    return alphas