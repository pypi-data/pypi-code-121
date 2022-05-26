import tempfile
import typing

import mlflow
from packaging.version import parse

from mlfoundry.exceptions import MlFoundryException
from mlfoundry.frameworks.base_registry import BaseRegistry


def get_tf():
    try:
        import tensorflow as tf

        return tf
    except ImportError as ex:
        raise ImportError(
            "Tensorflow package is required to use TfSavedModelArtifact."
        ) from ex


# right now only tensorflow 2 is supported
# I will take up if tf1 if there is any requirement
def assert_tf_2():
    tf = get_tf()
    version_string = tf.__version__
    major_version = parse(version_string).release[0]
    if major_version < 2:
        raise MlFoundryException(
            f"Only Tensorflow 2 is supported. Found tensorflow version {version_string}"
        )


class TensorflowRegistry(BaseRegistry):
    def log_model(
        self,
        model,
        artifact_path: str,
        signatures=None,
        options=None,
        tf_signature_def_key: typing.Optional[str] = None,
    ):
        assert_tf_2()
        tf = get_tf()
        tf_signature_def_key = (
            tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
            if tf_signature_def_key is None
            else tf_signature_def_key
        )
        with tempfile.TemporaryDirectory() as local_dir:
            tf.saved_model.save(
                obj=model,
                export_dir=local_dir,
                signatures=signatures,
                options=options,
            )
            mlflow.tensorflow.log_model(
                tf_saved_model_dir=local_dir,
                tf_meta_graph_tags=None,
                tf_signature_def_key=tf_signature_def_key,
                artifact_path=artifact_path,
            )

    def load_model(self, model_file_path: str, **kwargs):
        assert_tf_2()
        return mlflow.tensorflow.load_model(model_file_path)
