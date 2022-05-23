from kolibri.config import TaskType

class ModulesRegistry:

    registry = {
        'Estimators':{
        },
        'kolibri':{}
    }

    for task_type in TaskType:
        registry['Estimators'][task_type.name]={}


    @staticmethod
    def add_algorithm(
        task_name,
        model_class,
        model_params,
        required_preprocessing,
        additional,
        default_params,
    ):
        model_information = {
            "class": model_class,
            "params": model_params,
            "required_preprocessing": required_preprocessing,
            "additional": additional,
            "default_params": default_params,
        }
        ModulesRegistry.registry['Estimator'][task_name][
            model_class.algorithm_short_name
        ] = model_information

    @staticmethod
    def add_module(
        module_name,
        module_class,
    ):
        ModulesRegistry.registry['kolibri'][module_name] = {'class':module_class}


# from kolibri import features
# from kolibri.task.text import classification
# from kolibri import autolearn
# from kolibri.preprocess import tabular
# from kolibri.task.tabular.clustering.clustering import ClusteringEstimator
# from kolibri.task.text.topics import TopicModelEstimator
# from kolibri.tokenizers import WordTokenizer, RegexpTokenizer, KolibriTokenizer, SentenceTokenizer, CharTokenizer
# from kolibri.preprocess.tabular import *
# from kolibri.task.tabular.anomaly.anomaly_estimator import AnomalyEstimator