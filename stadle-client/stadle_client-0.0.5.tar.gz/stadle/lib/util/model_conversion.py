from copy import deepcopy

from stadle.lib.util.states import BaseModelConvFormat
from stadle.lib.env.handler import EnvironmentHandler

import numpy as np

def extract_weights_dict(model, base_model_type):
    model = deepcopy(model)

    if (base_model_type == BaseModelConvFormat.pytorch_format):
        # PyTorch
        if EnvironmentHandler.pt_installed_flag():
            import torch
        weights = model.to('cpu').state_dict()
        d = dict()
        for key, val in weights.items():
            if ('weight' in key or 'bias' in key):
                d[key] = weights[key].numpy()
        return d

    elif (base_model_type == BaseModelConvFormat.keras_format):
        d = dict()

        model_weights = model.get_weights()
        for i, w in enumerate(model_weights):
            d[f'layer_{i}'] = w

        return d

    # Needs specific testing (keras vs tf)
    elif (base_model_type == BaseModelConvFormat.tensorflow_format):
        d = dict()

        for model_var in model.trainable_variables:
            layer_name = model_var.name

            # TODO verification over multiple different models to verify weight layer "keywords"
            if ('kernel' in layer_name):
                d[layer_name] = model_var.numpy()

        return d

    else:
        raise ValueError("No valid base_model_type found when attempting to extract weights")


def merge_model_weights(base_model, model_dict, base_model_type):
    if (base_model_type == BaseModelConvFormat.pytorch_format):
        if EnvironmentHandler.pt_installed_flag():
            import torch

        model = deepcopy(base_model)
        model_state_dict = model.state_dict()

        for key, val in model_dict.items():
            model_state_dict[key] = torch.from_numpy(np.asarray(model_dict[key]))

        model.load_state_dict(model_state_dict)
        return model

    elif (base_model_type == BaseModelConvFormat.keras_format):
        model = deepcopy(base_model)
        model_weights = model.get_weights()

        for k in model_dict:
            idx = int(k[6:])
            model_weights[idx] = model_dict[k]

        model.set_weights(model_weights)
        return model

    # Needs specific testing (keras vs tf)
    elif (base_model_type == BaseModelConvFormat.tensorflow_format):
        for model_var in base_model.trainable_variables:
            layer_name = model_var.name

            if (layer_name in model_dict):
                model_var.assign(model_dict[layer_name])

    else:
        raise ValueError("No valid base_model_type found when attempting to extract weights")

    return base_model
