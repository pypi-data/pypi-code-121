"""
The ``mlflow.sklearn`` module provides an API for logging and loading scikit-learn models. This
module exports scikit-learn models with the following flavors:

Python (native) `pickle <https://scikit-learn.org/stable/modules/model_persistence.html>`_ format
    This is the main flavor that can be loaded back into scikit-learn.

:py:mod:`mlflow.pyfunc`
    Produced for use by generic pyfunc-based deployment tools and batch inference.
"""

from __future__ import absolute_import

import math
import os
from multiprocessing import Pool
import torch
import yaml
import transformers
from transformers import BertConfig, BertForSequenceClassification, BertTokenizer, XLNetConfig, \
    XLNetForSequenceClassification, XLNetTokenizer, XLMConfig, XLMForSequenceClassification, XLMTokenizer, \
    RobertaConfig, RobertaForSequenceClassification, RobertaTokenizer, DistilBertConfig, \
    DistilBertForSequenceClassification, DistilBertTokenizer, InputExample, InputFeatures, \
    get_linear_schedule_with_warmup, AdamW
from transformers import glue_compute_metrics as compute_metrics
from transformers import glue_processors as processors
from transformers import glue_output_modes as output_modes
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from torch.utils.data.distributed import DistributedSampler
import numpy as np

import mlflow
from mlflow import pyfunc
from mlflow.exceptions import MlflowException
from mlflow.models import Model
from mlflow.protos.databricks_pb2 import RESOURCE_ALREADY_EXISTS
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.utils.environment import _mlflow_conda_env
from mlflow.utils.model_utils import _get_flavor_configuration

from mlflow.utils.file_utils import TempDir
from infinstor_mlflow_plugin import transformers as infinstor_transformers

FLAVOR_NAME = "transformers"

MODEL_CLASSES = {
    'bert': (BertConfig, BertForSequenceClassification, BertTokenizer, 'bert-base-uncased'),
    'xlnet': (XLNetConfig, XLNetForSequenceClassification, XLNetTokenizer, 'xlnet-base-cased'),
    'xlm': (XLMConfig, XLMForSequenceClassification, XLMTokenizer, 'xlm-mlm-enfr-1024'),
    'roberta': (RobertaConfig, RobertaForSequenceClassification, RobertaTokenizer, 'distilbert-base-uncased'),
    'distilbert': (DistilBertConfig, DistilBertForSequenceClassification, DistilBertTokenizer, 'roberta-base'),
}

SERIALIZATION_FORMAT_PICKLE = "pickle"
SERIALIZATION_FORMAT_CLOUDPICKLE = "cloudpickle"

SUPPORTED_SERIALIZATION_FORMATS = [
    SERIALIZATION_FORMAT_PICKLE,
    SERIALIZATION_FORMAT_CLOUDPICKLE
]


def get_default_conda_env(include_cloudpickle=False):
    """
    :return: The default Conda environment for MLflow Models produced by calls to
             :func:`save_model()` and :func:`log_model()`.
    """
    pip_deps = None
    if include_cloudpickle:
        import cloudpickle
        pip_deps = ["cloudpickle=={}".format(cloudpickle.__version__)]
    return _mlflow_conda_env(
        additional_conda_deps=[
            "transformers={}".format(transformers.__version__),
        ],
        additional_pip_deps=pip_deps,
        additional_conda_channels=None
    )


def save_model(transformers_model, tokenizer, path, conda_env=None, mlflow_model=Model()):
    """
    Save a scikit-learn model to a path on the local file system.

    :param transformers_model: scikit-learn model to be saved.
    :param path: Local path where the model is to be saved.
    :param conda_env: Either a dictionary representation of a Conda environment or the path to a
                      Conda environment yaml file. If provided, this decsribes the environment
                      this model should be run in. At minimum, it should specify the dependencies
                      contained in :func:`get_default_conda_env()`. If `None`, the default
                      :func:`get_default_conda_env()` environment is added to the model.
                      The following is an *example* dictionary representation of a Conda
                      environment::

                        {
                            'name': 'mlflow-env',
                            'channels': ['defaults'],
                            'dependencies': [
                                'python=3.7.0',
                                'scikit-learn=0.19.2'
                            ]
                        }

    :param mlflow_model: :py:mod:`mlflow.models.Model` this flavor is being added to.
    :param tokenizer: tokenizer
    """
    if os.path.exists(path):
        raise MlflowException(message="Path '{}' already exists".format(path),
                              error_code=RESOURCE_ALREADY_EXISTS)
    os.makedirs(path)
    model_data_subpath = ""
    _save_model(transformers_model, tokenizer, model_path=os.path.join(path, model_data_subpath))
    conda_env_subpath = "conda.yaml"
    if conda_env is None:
        conda_env = get_default_conda_env(
            include_cloudpickle=SERIALIZATION_FORMAT_CLOUDPICKLE == SERIALIZATION_FORMAT_CLOUDPICKLE)
    elif not isinstance(conda_env, dict):
        with open(conda_env, "r") as f:
            conda_env = yaml.safe_load(f)
    with open(os.path.join(path, conda_env_subpath), "w") as f:
        yaml.safe_dump(conda_env, stream=f, default_flow_style=False)
    pyfunc.add_to_model(mlflow_model, loader_module="infinstor_mlflow_plugin.transformers", data=model_data_subpath,
                        env=conda_env_subpath)
    mlflow_model.add_flavor(FLAVOR_NAME,
                            pickled_model=model_data_subpath,
                            transformers_version=transformers.__version__)
    mlflow_model.save(os.path.join(path, "MLmodel"))


def log_model(model, tokenizer, conda_env=None):
    return transformers_log(artifact_path='infinstor/model',
                                  transformers_model=model,
                                  tokenizer=tokenizer,
                                  flavor=infinstor_transformers,
                                  registered_model_name=None,
                                  conda_env=conda_env)

def transformers_log(artifact_path, transformers_model, tokenizer, flavor, registered_model_name=None,
                     **kwargs):
    """
    Log model using supplied flavor module. If no run is active, this method will create a new
    active run.

    :param artifact_path: Run relative path identifying the model.
    :param transformers_model: The transformers model to log.
    :param tokenizer: The tokenizer to log.
    :param flavor: Flavor module to save the model with. The module must have
                   the ``save_model`` function that will persist the model as a valid
                   MLflow model.
    :param registered_model_name: Note:: Experimental: This argument may change or be removed
                                  in a future release without warning. If given, create a model
                                  version under ``registered_model_name``, also creating a
                                  registered model if one with the given name does not exist.
    :param kwargs: Extra args passed to the model flavor.
    """
    with TempDir() as tmp:
        local_path = tmp.path("model")
        save_model(transformers_model, tokenizer, local_path, None, Model())
        mlflow.tracking.fluent.log_artifacts(local_path, artifact_path)
        if registered_model_name is not None:
            run_id = mlflow.tracking.fluent.active_run().info.run_id
            mlflow.register_model("runs:/%s/%s" % (run_id, artifact_path),
                                  registered_model_name)

def _load_model_from_local_file(model_type, model_path):
    """Load a scikit-learn model saved as an MLflow artifact on the local file system."""
    config_class, model_class, tokenizer_class, _ = MODEL_CLASSES[model_type]
    config = config_class.from_pretrained(model_path)
    tokenizer = tokenizer_class.from_pretrained(model_path)
    model = model_class.from_pretrained(model_path, config=config)
    return model, tokenizer, config


def _load_pyfunc(path):
    """
    Load PyFunc implementation. Called by ``pyfunc.load_pyfunc``.

    :param path: Local filesystem path to the MLflow Model with the ``transformers`` flavor.
    """
    return _transformer_load_pyfunc(path)


def _transformer_load_pyfunc(path, model_type=None):
    if not model_type:
        model_type = "bert"
    model, tokenizer, config = _load_model_from_local_file(model_type, path)
    return _TransformersModelWrapper(model, tokenizer, config)

class _TransformersModelWrapper:
    def __init__(self, model, tokenizer, config):
        self.l_model = model
        self.l_tokenizer = tokenizer
        self.l_config = config

    def predict(self, dataframe):
        column_name = dataframe.columns[0]
        sentiments = []
        for headline in dataframe[column_name].values:
            max_len = 512
            n = 0
            sentiment = 0
            import nltk
            nltk.download('punkt')
            for input_sent in nltk.sent_tokenize(headline):
                n += 1
                import pandas as pd
                i_df = pd.DataFrame([input_sent])
                i_tokenized = i_df[0].apply((lambda x:self.l_tokenizer.encode(x, add_special_tokens=True)))
                i_padded = np.array([i + [0]*(max_len-len(i)) for i in i_tokenized.values])
                i_attention_mask = np.where(i_padded != 0, 1, 0)
                i_input_ids = torch.tensor(i_padded)  
                i_attention_mask = torch.tensor(i_attention_mask)
                i_predictions = []
                with torch.no_grad():
                    i_last_hidden_states = self.l_model(i_input_ids, attention_mask=i_attention_mask)

                i_logits = i_last_hidden_states[0]

                # Store predictions and true labels
                i_predictions.append(i_logits)
                i_pred_label = np.argmax(i_predictions[0], axis=1).flatten()

                #print('Sentiment for ' + input_sent + ' = ' + str(i_pred_label[0].numpy()))
                sentiment += i_pred_label[0].numpy()
            sentiments.append(int(round(sentiment/n)))

        rv = pd.Series(sentiments)
        return rv

def _save_model(transformers_model, tokenizer, model_path):
    """
    :param transformers_model: The scikit-learn model to serialize.
    :param model_path: The file path to which to write the serialized model.
    :param tokenizer: Tokenizer to save.
    """
    transformers_model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)


def load_model(model_type, model_uri=None):
    """
    Load a transformer-learn model from a local file or a run.
    :param model_type: The type of transformer model we are using
    :param model_uri: The location, in URI format, of the MLflow model, for example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                      artifact-locations>`_.

    :return: A transformers-learn model.
    """
    run_id = mlflow.tracking.fluent._get_or_start_run().info.run_id
    model_save_dir = os.path.join("runs:/", run_id)
    model_save_dir = os.path.join(model_save_dir, "model")
    if not model_uri:
        local_model_path = _download_artifact_from_uri(artifact_uri=model_save_dir)
    else:
        local_model_path = _download_artifact_from_uri(artifact_uri=model_uri)
    flavor_conf = _get_flavor_configuration(model_path=local_model_path, flavor_name=FLAVOR_NAME)
    transformers_model_artifacts_path = os.path.join(local_model_path, flavor_conf['pickled_model'])
    return _load_model_from_local_file(model_type=model_type, model_path=transformers_model_artifacts_path)
