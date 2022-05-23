import datetime
import os
from kdmt.file import read_json_file, write_json_to_file
from kolibri import version as ver
from kolibri.errors import *
from kolibri.config import component_config_from_pipeline

class Metadata(object):
    """Captures all information about a model_type to load and prepare it."""

    @staticmethod
    def load(model_dir):
        """Loads the metadata from a models directory.

        Args:
            model_dir (str): the directory where the model_type is saved.
        Returns:
            Metadata: A metadata object describing the model_type
        """
        try:
            metadata_file = os.path.join(model_dir, 'metadata.json')
            data = read_json_file(metadata_file)
            return Metadata(data, model_dir)
        except Exception as e:
            abspath = os.path.abspath(os.path.join(model_dir, 'metadata.json'))
            raise InvalidProjectError("Failed to load model_type metadata "
                                      "from '{}'. {}".format(abspath, e))

    def __init__(self, metadata, model_dir):

        self.metadata = metadata
        self.model_dir = model_dir

    def get(self, property_name, default=None):
        return self.metadata.get(property_name, default)

    @property
    def component_classes(self):
        if self.get('pipeline'):
            return [c.get("label") for c in self.get('pipeline', [])]
        else:
            return []

    @property
    def language(self):
        """Language of the underlying model_type"""

        return self.get('language')

    def persist(self, model_dir):
        """Persists the metadata of a model_type to a given directory."""

        metadata = self.metadata.copy()

        metadata.update({
            "trained_at": datetime.datetime.now().strftime('%Y%m%d-%H%M%S'),
            "kolibri_version": ver.__version__,
        })

        filename = os.path.join(model_dir, 'metadata.json')
        write_json_to_file(filename, metadata, indent=4)

    def for_component(self, name, defaults=None):
        return component_config_from_pipeline(name,
                                              self.get('pipeline', []),
                                              defaults)
