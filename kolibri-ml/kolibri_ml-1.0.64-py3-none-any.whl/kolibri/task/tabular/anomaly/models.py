from kolibri.backend.tensorflow.autoencoder import SimpleAutoencoder
from kolibri.backend.tensorflow.autoencoder import Conv1DAutoencoder
from kolibri.backend.tensorflow.autoencoder import SequenceAutoencoder
from kolibri.backend.tensorflow.autoencoder.variational_autoencoder import VariationalAutoencoder


def get_model(model_type, hyper_parameters=None):
    return {
        'mlp': SimpleAutoencoder(hyper_parameters=hyper_parameters),
        'conv': Conv1DAutoencoder(hyper_parameters=hyper_parameters),
        'deep': SequenceAutoencoder(hyper_parameters=hyper_parameters),
        'variational': VariationalAutoencoder(hyper_parameters=hyper_parameters)
    }.get(model_type.lower(), None)
