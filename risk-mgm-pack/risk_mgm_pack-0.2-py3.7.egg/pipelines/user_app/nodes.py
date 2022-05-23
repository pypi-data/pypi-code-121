import pandas as pd
from moosir_feature.trades.alpha_manager import create_absolute_prediction_alphas
from moosir_feature.transformers.managers.feature_manager import FeatureCreatorManager
from moosir_feature.transformers.managers.settings import IndicatorLagSettings, TargetSettings
from kedro_mlflow.io.models import MlflowModelSaverDataSet

def predict(instances: pd.DataFrame, model):

    # target_settings = TargetSettings()
    # feature_ind_settings = []
    # lag_ind_settings = [IndicatorLagSettings(**lag_ind_params)]
    #
    # fc_mgr = FeatureCreatorManager(target_settings=target_settings,
    #                                feature_settings_list=feature_ind_settings,
    #                                lag_settings_list=lag_ind_settings)
    #
    # features, _ = fc_mgr.create_features(instances=instances)
    # features = features.dropna()


    preds = model.predict(instances)

    # todo: move this to the feature package
    if len(preds) == 0:
        alphas = pd.DataFrame(columns=['Prediction', 'Signal'])
        alphas.index.name = "Timestamp"
        return alphas

    # prediction_result = pd.DataFrame(data={"preds": preds}, index=instances.index)
    prediction_result = preds

    alphas = create_absolute_prediction_alphas(instances=instances,
                                               prediction_result=prediction_result)

    return alphas
