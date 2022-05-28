import os

from myelin.admin.myelin_admin import MyelinAdmin

__ADMIN_CLIENT__ = MyelinAdmin()


def data_path(default_value=None):
    return os.environ.get('DATA_PATH') or default_value


def model_path(default_value=None):
    return os.environ.get('MODEL_PATH') or default_value


def task(task_name, axon=None, namespace=None, default_value=None):
    return __ADMIN_CLIENT__.task(get_axon(axon), task_name, get_namespace(namespace), default_value)


def model_backend(model_graph, model, model_backend_name, axon=None, namespace=None, default_value=None):
    return __ADMIN_CLIENT__.model_backend(get_axon(axon), model_graph, model, model_backend_name,
                                          get_namespace(namespace),
                                          default_value)


def get_axon(axon=None):
    return axon or os.environ.get('AXON_NAME')


def get_namespace(namespace=None):
    return namespace or os.environ.get('NAMESPACE')
