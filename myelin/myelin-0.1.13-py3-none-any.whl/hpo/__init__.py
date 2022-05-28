import os
import json
import base64

import myelin.metric


def hpo_enabled():
    return 'HPO_PARAMS' in os.environ


def get_hpo_config():
    hpo_params = os.environ.get('HPO_PARAMS')
    if hpo_params is None:
        return {}
    return json.loads(base64.b64decode(hpo_params))


def get_hpo_params():
    hpo_params = get_hpo_config()
    if hpo_params == {}:
        return {}
    return extract_hpo_params(hpo_params)


def publish_result(loss_metric, loss_value, params, tags, additional_metrics):
    loss_value = float(loss_value)
    info_map = {'loss value': loss_value}
    config_map = get_hpo_config()
    config_id = config_map['config-id']
    budget = config_map['budget']
    config = extract_hpo_params(config_map)

    myelin.metric.post_hpo_result(config_id, config, budget, loss_metric, loss_value, params, tags, info_map,
                                  additional_metrics)


def extract_hpo_params(config_map):
    return json.loads(config_map["hpo-conf"])
