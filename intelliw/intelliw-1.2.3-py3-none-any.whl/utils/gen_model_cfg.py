from intelliw.config.cfg_parser import load_config
import yaml
import os
from functools import wraps

def verify_and_generate_model_cfg(func):
    @wraps(func)
    def verify(*args):
        if not os.path.exists(args[1]):
            if not os.path.exists(args[0]):
                raise ValueError("missing algorithm.yaml at path: {}".format(args[0]))
            print('model.yaml does not exists, generating model.yaml to [{}] based on [{}].'.format(
                args[1], args[0]))
            func(*args)
    return verify


@verify_and_generate_model_cfg
def generate_model_config_from_algorithm_config(algorithm_config_path, model_config_path, location="model"):
    """
    根据 algorithm.yaml 生成 model.yaml

    :param algorithm_config_path: algorithm.yaml path
    :param model_config_path: model.yaml path
    :param location: model path
    """
    algo_cfg = load_config(algorithm_config_path)
    model_cfg = {
        "Model": {
            "name": algo_cfg["AlgorithmInformation"]["name"],
            "desc": algo_cfg["AlgorithmInformation"]["desc"],
            "location": location,
            "algorithm": {
                "name": algo_cfg["AlgorithmInformation"]["name"],
                "desc": algo_cfg["AlgorithmInformation"]["desc"],
            }
        }
    }
    if "metadata" in algo_cfg["AlgorithmInformation"]["algorithm"]:
        model_cfg["Model"]["metadata"] = algo_cfg["AlgorithmInformation"]["algorithm"]["metadata"]
    if "transforms" in algo_cfg["AlgorithmInformation"]["algorithm"]:
        model_cfg["Model"]["transforms"] = algo_cfg["AlgorithmInformation"]["algorithm"]["transforms"]
    if "parameters" in algo_cfg["AlgorithmInformation"]["algorithm"] and isinstance(algo_cfg["AlgorithmInformation"]["algorithm"]["parameters"], list):
        params = {}
        for item in algo_cfg["AlgorithmInformation"]["algorithm"]["parameters"]:
            if "key" in item and "val" in item:
                params[item["key"]] = item["val"]
        model_cfg["Model"]["parameters"] = params

    model = yaml.dump(model_cfg, default_flow_style=False, allow_unicode=True)

    f = open(model_config_path, 'w', encoding='utf-8')
    f.write(model)
    f.close()



