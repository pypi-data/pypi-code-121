from typing import Any, Dict, List, MutableMapping

import mlflow


def flatten_dict(
    source_dict: MutableMapping[str, Any],
    pre_list: List[str] = [],
    result_dict: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """ネストされた辞書系の変数を、平坦な辞書に変換する。

    Parameters
    ----------
    source_dict : MutableMapping[str, Any]
        変換元辞書
    pre_list : List[str], optional
        内部変数のため使用時は指定しない, by default []
    result_dict : Dict[str, Any], optional
        内部変数のため使用時は指定しない, by default {}

    Returns
    -------
    Dict[str, Any]
        平坦化された辞書
    """
    for k, v in source_dict.items():
        current_list = pre_list + [k]

        if isinstance(v, MutableMapping):
            flatten_dict(v, pre_list=current_list, result_dict=result_dict)
        else:
            result_dict["__".join(current_list)] = v

    return result_dict


def generate_mlflow_active_run(url: str, experiment_name: str) -> mlflow.ActiveRun:
    """指定されたURLと実験名でMLflowの実験管理オブジェクトを生成する。

    Parameters
    ----------
    url : str
        MLflowのURL
    experiment_name : str
        実験名

    Returns
    -------
    mlflow.ActiveRun
        MLflow実験管理オブジェクト
    """
    mlflow.set_tracking_uri(url)

    mlflow.set_experiment(experiment_name)
    mlflow_experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id

    return mlflow.start_run(experiment_id=mlflow_experiment_id)
