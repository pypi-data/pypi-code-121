# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Helper functions for model loading."""

import os
import json
import importlib
import inspect
import tempfile
import types

from keras.utils.generic_utils import CustomObjectScope
import keras
import tensorflow as tf

from eff.core import Archive, ArtifactType
from eff.callbacks import KerasContentCallback, StringContentCallback

from tao_byom.layers.custom_layers import CUSTOM_OBJS


def save_lambda_functions(lambda_dict, results_dir, model_name):
    """Save lambda functions used during model conversion."""
    node_to_keras = {}
    for k, v in lambda_dict.items():
        node_to_keras[k] = v.__qualname__  # function name

    with open(os.path.join(results_dir, f'{model_name}_mapping.json'), mode='w', encoding="utf-8") as f:
        json.dump(node_to_keras, f, indent=4, separators=(',', ': '))


def save_eff(k_model,
             output_dir,
             model_name,
             metadata={},
             passphrase=None,
             extension="tltb",
             custom_obj={},
             custom_layer_path=None,
             verbose=False):
    """Store Keras Model as EFF Archive.

    Args:
        k_model (keras.models.Model): Keras Model to convert.
        output_dir (str): Dir to save the eff file.
        model_name (str): Name of the model.
        metadata (dict): Additional metadata to append to EFF.
        passphrase (str): Key to load EFF file.
        extension (str): file extension for EFF.
        custom_objs (dict): dictionary of custom objects.
        custom_layer_path (str): file name where custom layer implementations are stored.
        verbose (bool): EFF verbosity.

    Returns:
        arch_file (str): Path of the stored eff file.
    """
    arch_file = os.path.join(output_dir, f"{model_name}.{extension}")

    # If specific custom layer is provided, then aappend the code to existing custom layer
    if custom_layer_path:
        if not os.path.exists(custom_layer_path):
            raise FileNotFoundError("The provided custom file does not exist")

        with open(custom_layer_path, "r", encoding="utf8") as f:
            custom_src = f.read()
    else:
        custom_src = ''

    plugin_name = "tao_byom.layers.custom_layers"
    plugin_module = importlib.import_module(plugin_name)
    source_code = custom_src + inspect.getsource(plugin_module)

    # Update CUSTOM_OBJS if user has a new custom layer
    if custom_obj:
        final_custom_objs = {**CUSTOM_OBJS, **custom_obj}
    else:
        final_custom_objs = CUSTOM_OBJS

    class_names = []
    for _, v in final_custom_objs.items():
        class_names.append(v.__name__)

    with Archive.create(save_path=arch_file, passphrase=passphrase, meta_info="BYOM eff") as effa:
        # Add Meta data
        effa.metadata.add(**metadata)

        # Save Custom Layer
        effa.artifacts.create(
            name="custom_layers.py",
            description="Custom Keras Layers Implementation",
            class_names=class_names,
            artifact_type=ArtifactType.MEMORY,
            content=source_code,
        )
        model_effa = effa.artifacts.create(
            name=f"{model_name}.hdf5",
            description="HDF5 Model",
            keras_version=keras.__version__,
            tf_version=tf.__version__,
            content_callback=KerasContentCallback,
        )
        model_effa.set_content([k_model.get_weights(), k_model.to_json()])

        effa.artifacts.add(
            name=f"{model_name}_summary.txt",
            filepath=os.path.join(output_dir, f"{model_name}_summary.txt"),
            description="Model Summary",
            content_callback=StringContentCallback
        )

        if verbose:
            print(effa.pretty(detailed=True))
    return arch_file


def deserialize_custom_layers(art):
    """Deserialize the code for custom layer from EFF."""
    # Get class.
    source_code = art.get_content()

    # Save the custom implementation in a tmp dir
    # Ref:
    # https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
    with tempfile.TemporaryDirectory() as temp_d:
        temp_f = os.path.join(temp_d, "custom_layer.py")
        with open(temp_f, "w", encoding="utf-8") as f:
            f.write(source_code)

        loader = importlib.machinery.SourceFileLoader('helper', temp_f)
        helper = types.ModuleType(loader.name)
        loader.exec_module(helper)

    final_dict = {}
    # Get class name from attributes.
    class_names = art["class_names"]
    for cn in class_names:
        final_dict[cn] = getattr(helper, cn)
    return final_dict


def restore_eff(model_name, eff_path, passphrase=None):
    """Restore Keras Model from EFF Archive.

    Args:
        eff_path (str): Path to the eff file.
        passphrase (str): Key to load EFF file.

    Returns:
        model (keras.models.Model): Loaded keras model.
    """
    with Archive.restore_from(restore_path=eff_path, passphrase=passphrase) as restored_effa:
        EFF_CUSTOM_OBJS = deserialize_custom_layers(restored_effa.artifacts['custom_layers.py'])

        art = restored_effa.artifacts[f'{model_name}.hdf5']
        weights, m = art.get_content()

    with CustomObjectScope(EFF_CUSTOM_OBJS):
        model = keras.models.model_from_json(m, custom_objects=EFF_CUSTOM_OBJS)
        model.set_weights(weights)

    return model, EFF_CUSTOM_OBJS


def bring_your_own_layer(meta_json_path):
    """Incorporates custom layer implementation from user into BYOM converter

    Args:
        meta_json_path (str): Path to the meta json file.

    Returns:
        additional_converters (dict): To be added to AVAILABLE_CONVERTERS.
        custom_layer_file (str): Path to the custom layer implementation python file.
        custom_objs (dict): To be added to CUSTOM_OBJS
    """
    if not os.path.exists(meta_json_path):
        raise FileNotFoundError("Provided meta json file for custom layer does not exist!")

    with open(meta_json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    additional_converters = {}
    top_dir = meta['TOP_DIR']
    conversion_file, custom_layer_file = meta['FILE_NAMES']['conversion'], meta['FILE_NAMES']['custom_layer']

    if not os.path.exists(os.path.join(meta['ABS_TOP_DIR'], conversion_file)):
        raise FileNotFoundError("Provided onnx conversion implementation file does not exist!")
    if not os.path.exists(os.path.join(meta['ABS_TOP_DIR'], custom_layer_file)):
        raise FileNotFoundError("Provided custom layer implementation file does not exist!")

    conversion_file = conversion_file.replace(".py", "")
    conversion_module = f"{top_dir}.{conversion_file}"

    conv_mod = importlib.import_module(conversion_module)
    # Loop through conversion functions
    for onnx_node, conversion_func in meta['ONNX_NODES'].items():
        additional_converters[onnx_node] = getattr(conv_mod, conversion_func)

    temp_custom_layer_file = custom_layer_file.replace(".py", "")
    custom_module = f"{top_dir}.{temp_custom_layer_file}"
    custom_objs = {}

    mod = importlib.import_module(custom_module)
    # Loop through custom layer classes
    for n, layer in meta['CUSTOM_OBJS'].items():
        custom_objs[n] = getattr(mod, layer)

    custom_layer_file = os.path.join(top_dir, custom_layer_file)

    return additional_converters, custom_layer_file, custom_objs


def load_model_from_config(conf):
    """Simple function to load model from json."""
    with CustomObjectScope(CUSTOM_OBJS):
        model = keras.models.Model.from_config(conf)
    return model
