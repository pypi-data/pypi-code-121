from fair_dynamic_rec.core.rankers.random import *
from fair_dynamic_rec.core.rankers.naive_greedy import *
from fair_dynamic_rec.core.rankers.naive_epsilon_greedy import *
from fair_dynamic_rec.core.rankers.thompson_sampling import *
from fair_dynamic_rec.core.rankers.kl_upper_confidence_bound import *
from fair_dynamic_rec.core.rankers.linear_submodular_bandit import *
from fair_dynamic_rec.core.rankers.linear_upper_confidence_bound import *
from fair_dynamic_rec.core.rankers.hybrid_lsb_linucb import *
from fair_dynamic_rec.core.rankers.lsb_random import *
from fair_dynamic_rec.core.rankers.ea_linear_submodular_bandit import *
from fair_dynamic_rec.core.rankers.ea_linear_upper_confidence_bound import *
from fair_dynamic_rec.core.rankers.ea_hybrid_lsb_linucb import *
from fair_dynamic_rec.core.rankers.ears_linear_thompson_sampling import EARSLinearTS
from fair_dynamic_rec.core.rankers.ears_linear_submodular_bandit import EARSLSB
from fair_dynamic_rec.core.rankers.ears_linear_upper_confidence_bound import EARSLinUCB
from fair_dynamic_rec.core.rankers.ears_hybrid_lsb_linucb import EARSHybridLSBLinUCB
from tqdm import tqdm

RankerModel = {'random': Random, 'naive_greedy': NaiveGreedy, 'naive_epsilon_greedy': NaiveEpsilonGreedy,
               'thompson_sampling': ThompsonSampling, 'kl_upper_confidence_bound': KLUCB, 'linear_submodular_bandit': LSB,
               'linear_upper_confidence_bound': LinUCB, 'hybrid_lsb_linucb': HybridLSBLinUCB, 'lsb_random': LSBRandom,
               'ea_linear_submodular_bandit': EALSB, 'ea_linear_upper_confidence_bound': EALinUCB, 'ea_hybrid_lsb_linucb': EAHybridLSBLinUCB,
               'ears_linear_thompson_sampling': EARSLinearTS, 'ears_linear_submodular_bandit': EARSLSB,
               'ears_linear_upper_confidence_bound': EARSLinUCB, 'ears_hybrid_lsb_linucb': EARSHybridLSBLinUCB}


def set_rankers(config, dataObj):
    rankers = []
    print('config.rankers=' + str(len(config.rankers)))
    for params in tqdm(config.rankers):
        print(params["single_val_params"]["name"]["value"])
        if len(params["multiple_val_params"]) > 0:
            for param in params["multiple_val_params"]:
                print('params["multiple_val_params"]=' + str(len(params["multiple_val_params"])))
                _conf = dict(list(params["single_val_params"].items()) + list(param.items()))
                rankers.append(
                    {'ranker': RankerModel[params["single_val_params"]["name"]["value"]](config, dataObj, _conf),
                     'config': _conf}
                )
        elif len(params["single_val_params"]) > 0:
            rankers.append(
                {'ranker': RankerModel[params["single_val_params"]["name"]["value"]](config, dataObj, params["single_val_params"]),
                 'config': params["single_val_params"]}
            )
        # _ranker = RankerModel[params["single_val_params"]["name"]](config, dataObj)
        # # _ranker.load_data(config, dataObj)
        # _config = dict(list(config.items()) + list(params["single_val_params"].items()))
        # for param in params["multiple_val_params"]:
        #     _ranker.config = dict(list(_ranker.config.items()) + list(param.items()))
        #
        # rankers.append({'ranker': _ranker, 'config': _config})
    return rankers