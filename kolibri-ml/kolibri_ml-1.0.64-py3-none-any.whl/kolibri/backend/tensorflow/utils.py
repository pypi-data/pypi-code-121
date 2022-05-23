# encoding: utf-8
"""
@author: BrikerMan
@contact: eliyar917@gmail.com
@blog: https://eliyar.biz

@version: 1.0
@license: Apache Licence
@file: helpers.py
@time: 2019-05-17 11:37

"""
import json
import pathlib
import pydoc
import random
import time
from typing import List, Optional, Dict

import tensorflow
from tensorflow.python import keras, saved_model

custom_objects = tensorflow.keras.utils.get_custom_objects()
# from kolibri.dnn.embeddings.base_embedding import Embedding
from kolibri.backend.tensorflow.layers.crf import ConditionalRandomField as CRF

import logging
import os

import numpy as np

logger = logging.getLogger(__name__)


# from kolibri.dnn.tasks.classification.base_model import BaseTextClassificationModel
# from kolibri.dnn.tasks.labeling.base_model import BaseLabelingModel


def unison_shuffled_copies(a, b):
    assert len(a) == len(b)
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    return list(a), list(b)


def get_list_subset(target: List, index_list: List[int]) -> List:
    return [target[i] for i in index_list if i < len(target)]


def custom_object_scope():
    return tensorflow.keras.utils.custom_object_scope(custom_objects)


def load_model(model_path: str,
               load_weights: bool = True):
    """
    Load saved model from saved model from `model.save` function
    Args:
        model_path: model folder path
        load_weights: only load model structure and vocabulary when set to False, default True.

    Returns:

    """
    with open(os.path.join(model_path, 'model_info.json'), 'r') as f:
        model_info = json.load(f)

    model_class = pydoc.locate(f"{model_info['module']}.{model_info['class_name']}")
    model_json_str = json.dumps(model_info['tf_model'])

    model = model_class()
    model.tf_model = tensorflow.keras.models.model_from_json(model_json_str, custom_objects)
    if load_weights:
        model.tf_model.load_weights(os.path.join(model_path, 'model_weights.h5'))

    embed_info = model_info['embedding']
    embed_class = pydoc.locate(f"{embed_info['module']}.{embed_info['class_name']}")
    embedding = embed_class._load_saved_instance(embed_info,
                                                 model_path,
                                                 model.tf_model)

    model.embedding = embedding

    if type(model.tf_model.layers[-1]) == CRF:
        model.layer_crf = model.tf_model.layers[-1]

    return model


def load_indexer(model_path: str):
    """
    Load indexer from model
    When we using tf-serving, we need to use model's indexer to pre-process texts
    Args:
        model_path:

    Returns:

    """
    with open(os.path.join(model_path, 'model_info.json'), 'r') as f:
        model_info = json.load(f)

    indexer_info = model_info['embedding']['indexer']
    indexer_class = pydoc.locate(f"{indexer_info['module']}.{indexer_info['class_name']}")
    indexer = indexer_class(**indexer_info['config'])
    return indexer


def convert_to_saved_model(model,
                           model_path: str,
                           version: str = None,
                           inputs: Optional[Dict] = None,
                           outputs: Optional[Dict] = None):
    """
    Export model for tensorflow serving
    Args:
        model: Target model
        model_path: The path to which the SavedModel will be stored.
        version: The model version code, default timestamp
        inputs: dict mapping string input names to tensors. These are added
            to the SignatureDef as the inputs.
        outputs:  dict mapping string output names to tensors. These are added
            to the SignatureDef as the outputs.
    """
    pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
    if version is None:
        version = round(time.time())
    export_path = os.path.join(model_path, str(version))

    if inputs is None:
        inputs = {i.my_name: i for i in model.tf_model.inputs}
    if outputs is None:
        outputs = {o.my_name: o for o in model.tf_model.outputs}
    sess = keras.backend.get_session()
    saved_model.simple_save(session=sess,
                            export_dir=export_path,
                            inputs=inputs,
                            outputs=outputs)

    with open(os.path.join(export_path, 'model_info.json'), 'w') as f:
        f.write(json.dumps(model.info(), indent=2, ensure_ascii=True))
        f.close()


def load_data_object(data, **kwargs):
    """
    Load Object From Dict
    Args:
        data:
        **kwargs:

    Returns:

    """
    module_name = f"{data['__module__']}.{data['__class_name__']}"
    obj = pydoc.locate(module_name)(**data['config'], **kwargs)
    if hasattr(obj, '_override_load_model'):
        obj._override_load_model(data)

    return obj


def load_word_embeddings(file_path, vocab=None):
    """
    Loads a word embedding model text file into a word(str) to numpy vector dictionary

    Args:
        file_path (str): path to model file
        vocab (list of str): optional - vocabulary

    Returns:
        list: a dictionary of numpy.ndarray vectors
        int: detected word embedding vector size
    """
    with open(file_path, encoding="utf-8") as fp:
        word_vectors = {}
        size = None
        for line in fp:
            line_fields = line.split()
            if len(line_fields) < 5:
                continue
            if line[0] == " ":
                word_vectors[" "] = np.asarray(line_fields, dtype="float32")
            elif vocab is None or line_fields[0] in vocab:
                word_vectors[line_fields[0]] = np.asarray(line_fields[1:], dtype="float32")
                if size is None:
                    size = len(line_fields[1:])
    return word_vectors, size


def fill_embedding_mat(src_mat, src_lex, emb_lex, emb_size):
    """
    Creates a new matrix from given matrix of int words using the embedding
    model provided.

    Args:
        src_mat (numpy.ndarray): source matrix
        src_lex (dict): source matrix lexicon
        emb_lex (dict): embedding lexicon
        emb_size (int): embedding vector size
    """
    emb_mat = np.zeros((src_mat.shape[0], src_mat.shape[1], emb_size))
    for i, sen in enumerate(src_mat):
        for j, w in enumerate(sen):
            if w > 0:
                w_emb = emb_lex.get(str(src_lex.get(w)).lower())
                if w_emb is not None:
                    emb_mat[i][j] = w_emb
    return emb_mat


def get_embedding_matrix(embeddings: dict, vocab, embedding_size: int = None, lowercase_only: bool = False):
    """
    Generate a matrix of word embeddings given a vocabulary

    Args:
        embeddings (dict): a dictionary of embedding vectors
        vocab (Vocabulary): a Vocabulary
        embedding_size (int): custom embedding matrix size

    Returns:
        a 2D numpy matrix of lexicon embeddings
    """
    emb_size = len(next(iter(embeddings.values())))
    if embedding_size:
        mat = np.zeros((embedding_size, emb_size))
    else:
        mat = np.zeros((len(vocab), emb_size))
    if lowercase_only:
        for word, wid in vocab.vocab.items():
            vec = embeddings.get(word.lower(), None)
            if vec is not None:
                mat[wid] = vec
    else:
        for word, wid in vocab.vocab.items():
            vec = embeddings.get(word, None)
            if vec is None:
                vec = embeddings.get(word.lower(), None)
            if vec is not None:
                mat[wid] = vec
    return mat


def load_embedding_file(filename: str, dim: int = None) -> dict:
    """Load a word embedding file

    Args:
        filename (str): path to embedding file

    Returns:
        dict: dictionary with embedding vectors
    """
    if filename is not None and os.path.exists(filename):
        logger.info("Loading external word embeddings from {}".format(filename))
    embedding_dict = {}
    with open(filename, encoding="utf-8") as fp:
        for line in fp:
            split_line = line.split()
            word = split_line[0]
            vec = np.array([float(val) for val in split_line[1:]])
            embedding_dict[word] = vec
    return embedding_dict


def get_loss_object(loss_str, **kwargs):
    if loss_str=='mae':
        return tensorflow.keras.losses.MeanAbsoluteError(**kwargs)
    elif loss_str == 'mse':
        return tensorflow.keras.losses.MeanSquaredError(**kwargs)
    elif loss_str=='mape':
        return tensorflow.keras.losses.MeanAbsolutePercentageError(**kwargs)
    elif loss_str=='msle':
        return tensorflow.keras.losses.MeanSquaredLogarithmicError(**kwargs)
    elif loss_str=='categorical':
        return tensorflow.keras.losses.CategoricalCrossentropy(**kwargs)
    elif loss_str=='binary':
        return tensorflow.keras.losses.BinaryCrossentropy(**kwargs)
    elif loss_str=="kld":
        return tensorflow.keras.losses.KLDivergence(**kwargs)


if __name__ == "__main__":
    path = ''
    p = load_indexer(path)

    print(p.label2idx)
    print(p.token2idx)
