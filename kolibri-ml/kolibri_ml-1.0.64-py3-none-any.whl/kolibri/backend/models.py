

from kdmt.file import read_json_file
from pathlib import Path
from kolibri.task.text.topics import get_available_models as get_topics_available_models
import kolibri.task.text.topics.topics_estimator
from kolibri.data.text.resources import resources
from kolibri.config import TaskType
import pandas as pd

try:
    sklearn_classifier_path= resources.get(str(Path('models', 'sklearn', 'classifiers.json'))).path
    sklearn_classification_models=read_json_file(sklearn_classifier_path)
    sklearn_classification_models_names=list(sklearn_classification_models.keys())

    sklearn_regressor_path= resources.get(str(Path('models', 'sklearn', 'regressors.json'))).path
    sklearn_regression_models=read_json_file(sklearn_regressor_path)
    sklearn_regression_models_names=list(sklearn_regression_models.keys())


    sklearn_clustering_path= resources.get(str(Path('models', 'sklearn', 'unsupervised.json'))).path
    sklearn_clustering_models=read_json_file(sklearn_clustering_path)
    sklearn_clustering_models_names=list(sklearn_clustering_models.keys())

    anomaly_models_path= resources.get(str(Path('models', 'sklearn', 'anomaly.json'))).path
    anomaly_models=read_json_file(anomaly_models_path)
    anomaly_models_names=list(anomaly_models.keys())
except Exception as e:
    print(e)
    pass


def get_classification_model(model_name, weights=None, bakend='tensorflow'):
    if isinstance(model_name, list) and len(model_name)>1:
        models_ = [sklearn_classification_models.get(model, None) for model in model_name]

        if weights is None:
            weights = [1 for model in model_name]
        model_cict={
      "class": "sklearn.ensemble.VotingClassifier",
      "name": "voting_classifier",
      "parameters": {
        "estimators": {
          "value": models_
        },
        "voting": {
          "value": "soft",
          "type": "categorical",
          "values": ["soft", "hard"]
        },
        "weights": {
          "value": weights
        },
        "n_jobs":{
            "value": -1
        }
      }
    }

        return model_cict

    elif isinstance(model_name, list) and len(model_name)==1:
        model= sklearn_classification_models.get(model_name[0], None)
    else:
        model= sklearn_classification_models.get(model_name, None)
    if model is not None:
        return model
    else:
        return model_name

def get_unsupervised_model(model_name, weights=None):

    if isinstance(model_name, list) and len(model_name)==1:
        model= sklearn_clustering_models.get(model_name[0], None)
    else:
        model= sklearn_clustering_models.get(model_name, None)
    if model is not None:
        return model
    else:
        return model_name

def get_model(model_name, weights=None, task_type=TaskType.CLASSIFICATION):

    if task_type==TaskType.ANOMALY_DETECTION:
        models=anomaly_models
    elif task_type==TaskType.CLUSTERING:
        models=sklearn_clustering_models
    elif task_type==TaskType.REGRESSION:
        models=sklearn_regression_models
    else:
        models=sklearn_classification_models
        models_ = [sklearn_classification_models.get(model, None) for model in model_name]

        if weights is None:
            weights = [1 for model in model_name]
        model_cict = {
            "class": "sklearn.ensemble.VotingClassifier",
            "name": "voting_classifier",
            "parameters": {
                "estimators": {
                    "value": models_
                },
                "voting": {
                    "value": "soft",
                    "type": "categorical",
                    "values": ["soft", "hard"]
                },
                "weights": {
                    "value": weights
                },
                "n_jobs": {
                    "value": -1
                }
            }
        }

        return model_cict

    if isinstance(model_name, list) and len(model_name)==1:
        model= models.get(model_name[0], None)
    else:
        model= models.get(model_name, None)

    if model is not None:
        return model
    else:
        return model_name

def get_available_models(model_type):

    if model_type not in ["classification", "clustering", "regression", "anomaly_detection", "topics", "all"]:
        print("Wrong model_type parameter. Available options are: 'classification', 'clustering', 'regression', 'anomaly_detection', 'topics'")

    model_dic=None
    if model_type=="classification":
        model_dic=sklearn_classification_models
    elif model_type=="clustering":
        model_dic = sklearn_classification_models

    elif model_type=="regression":
        model_dic = sklearn_regression_models
    elif model_type=="anomaly_detection":
        model_dic = anomaly_models

    if model_dic is not None:
        model_id=model_dic.keys()
        model_name=[v["name"] for v in model_dic.values()]

        df = pd.DataFrame({"ID": model_id, "Name": model_name})

        df.set_index("ID", inplace=True)
    elif model_type=="topics":
        df=kolibri.task.text.topics.topics_estimator.get_available_models()

    if model_type=="all":
        model_type=["classification" for v in sklearn_classification_models.values()]
        model_id=list(sklearn_classification_models.keys())
        model_name=[v["name"] for v in sklearn_classification_models.values()]

        model_id.extend(list(sklearn_clustering_models.keys()))
        model_name.extend([v["name"] for v in sklearn_clustering_models.values()])
        model_type.extend(["clustering" for v in sklearn_clustering_models.values()])

        model_id.extend(list(sklearn_regression_models.keys()))
        model_name.extend([v["name"] for v in sklearn_regression_models.values()])
        model_type.extend(["regression" for v in sklearn_regression_models.values()])

        model_id.extend(list(anomaly_models.keys()))
        model_name.extend([v["name"] for v in anomaly_models.values()])
        model_type.extend(["anomaly_detection" for v in anomaly_models.values()])

        topics = get_topics_available_models()

        model_id.extend(topics.index.values)
        model_name.extend((topics['Name'].values))
        model_type.extend(['topics' for v in topics["Name"].values])

        df = pd.DataFrame({"ID": model_id, "Name": model_name, "type": model_type})
        df.set_index("ID", inplace=True)
    return df



if __name__=="__main__":

    models_=get_unsupervised_model("KMeans")
    print(models_)