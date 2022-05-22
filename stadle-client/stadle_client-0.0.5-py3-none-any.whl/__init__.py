import os
from os.path import dirname

from stadle.lib.constants.environment import ConfigFileType
from stadle.lib.env.handler import EnvironmentHandler
from stadle.lib.env.handler import EnvironmentVar

TF_INSTALLED_FLAG = True
PT_INSTALLED_FLAG = True

# Only print errors to console, hide debugging info (for TF)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    import tensorflow as tf 
except ImportError:
    TF_INSTALLED_FLAG = False

try:
    import torch
except ImportError:
    PT_INSTALLED_FLAG = False

# if (not (TF_INSTALLED_FLAG or PT_INSTALLED_FLAG)):
#     raise ImportError('At least one of PyTorch and TensorFlow must be installed in the environment to facilitate model handling')

if TF_INSTALLED_FLAG:
    """
    Fix to make Keras models work with pickle
    """

    from tensorflow.keras.models import Model
    from tensorflow.python.keras.layers import deserialize, serialize
    from tensorflow.python.keras.saving import saving_utils

    def unpack(model, training_config, weights):
        restored_model = deserialize(model)
        if training_config is not None:
            restored_model.compile(
                **saving_utils.compile_args_from_training_config(
                    training_config
                )
            )
        restored_model.set_weights(weights)
        return restored_model
    # Hotfix function
    def make_keras_picklable():
        def __reduce__(self):
            model_metadata = saving_utils.model_metadata(self)
            training_config = model_metadata.get("training_config", None)
            model = serialize(self)
            weights = self.get_weights()
            return (unpack, (model, training_config, weights))
        cls = Model
        cls.__reduce__ = __reduce__
    # Run the function
    make_keras_picklable()
    """
    End fix
    """

# setup default environment variables

env_handler = EnvironmentHandler()
current_dir = dirname(__file__)

env_handler.add_variable(EnvironmentVar.STADLE_MODULE_PATH.value, current_dir)
env_handler.add_variable(EnvironmentVar.STADLE_CONFIG_PATH.value, os.path.join(env_handler.module_path, "configs"))
# settle default STADLE_AGENT_CONFIG_PATH
env_handler.add_variable(EnvironmentVar.STADLE_AGENT_CONFIG_PATH.value,
                         os.path.join(env_handler.config_path, ConfigFileType.STADLE_AGENT.value))
# settle default STADLE_ADMIN_AGENT_CONFIG_PATH
env_handler.add_variable(EnvironmentVar.STADLE_ADMIN_AGENT_CONFIG_PATH.value,
                         os.path.join(env_handler.config_path, ConfigFileType.STADLE_ADMIN_AGENT.value))

env_handler.add_variable(EnvironmentVar.PT_INSTALLED_FLAG.value, str(PT_INSTALLED_FLAG))
env_handler.add_variable(EnvironmentVar.TF_INSTALLED_FLAG.value, str(TF_INSTALLED_FLAG))

# Moved to bottom in order to use pt installed flag for conditional import of torch.nn
from stadle.client.base_admin_agent import AdminAgent
from stadle.client.client import Client
from stadle.client.client import ClientState
from stadle.lib.logging.logger import Logger
from stadle.lib.util.debug import debug_with_stdout
from stadle.lib.util.helpers import read_config
from stadle.lib.util.states import BaseModelConvFormat
from stadle.client.client import BasicClient, IntegratedClient
