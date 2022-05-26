"""
This file contains classes needed for ELBO progress Tracker
"""
import os
import json
import shutil
import sys
import tempfile

import gpustat
import psutil

import elbo.connector
from enum import Enum
from elbo.actions import cp
from collections import namedtuple
import logging

from elbo.utils.misc_utils import generate_short_rand_string

logging.basicConfig()


class ProgressTileType(str, Enum):
    heart_beat = "Heart Beat"
    key_metric_numeric = "Key Numeric Metric"
    message = "Message"
    image = "Image"


ProgressTile = namedtuple("ProgressTile", 'name type value')


class TaskTracker(object):
    ELBO_PROGRESS_TRACKER_LOGS_DIRECTORY = "logs"
    ELBO_MESSAGE_TILE_NAME = "Messages"
    MELBO_CLIENT_APP_TARGET_PREFIX = "melbo_00002"

    def __init__(self, experiment_name, experiment_id=None):
        self._experiment_id = experiment_id
        if self._experiment_id is None:
            self._experiment_id = self.get_random_human_friendly_experiment_id()
        self._elbo_connector = elbo.connector.ElboConnector()
        self._target_prefix = os.path.join(self.MELBO_CLIENT_APP_TARGET_PREFIX, self._experiment_id,
                                           self.ELBO_PROGRESS_TRACKER_LOGS_DIRECTORY)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self._progress_tiles: [ProgressTile] = []
        self._payload = {
            'name': experiment_name,
            'tiles': self._progress_tiles
        }
        self._images = []
        self._output_dir = tempfile.mkdtemp()
        self._logger.debug(f"Saving to {self._output_dir}")

    @staticmethod
    def get_random_human_friendly_experiment_id():
        # TODO Generate a human friendly name like - fanciful-society-1
        return generate_short_rand_string()

    def convert_tiles_to_dictionary_with_metadata(self) -> dict:
        """
        Convert all progress tiles to dictionary and add metadata
        :return: A dictionary that can be serialized and written to
        """
        output = {'name': self._payload['name']}
        try:
            gpu_info = gpustat.GPUStatCollection.new_query().jsonify()
        except Exception as e:
            self._logger.warning(f"Unable to get gpu information - {e}")
            gpu_info = {}

        output['gpu_info'] = gpu_info

        # noinspection PyProtectedMember
        memory_info = psutil.virtual_memory()._asdict()
        cpu_time_info = psutil.cpu_times_percent()
        cpu_count = psutil.cpu_count()

        output['cpu_count'] = cpu_count
        output['cpu_time_info'] = cpu_time_info
        output['memory_info'] = memory_info

        output['tiles'] = []
        for tile in self._progress_tiles:
            tile_dict = {'name': tile.name}
            if tile.type == ProgressTileType.image:
                tile_dict['image'] = tile.value
            elif tile.type == ProgressTileType.message:
                tile_dict['message'] = tile.value
            elif tile.type == ProgressTileType.key_metric_numeric:
                tile_dict['metric'] = tile.value
            else:
                self._logger.error(f"Unknown tile type - {tile}")

            output['tiles'].append(tile_dict)

        return output

    def upload_logs(self):
        payload_dict = self.convert_tiles_to_dictionary_with_metadata()
        json_log = json.dumps(payload_dict, indent=4, sort_keys=True, default=str)
        temp_file = os.path.join(self._output_dir, "elbo.json")
        with open(temp_file, "w") as fd:
            fd.write(json_log)

        self._logger.debug(json_log)
        self._logger.debug(f"Uploading elbo json file {temp_file}")
        cp.cp_to_elbo(self._elbo_connector, temp_file, self._target_prefix)
        self._logger.debug(f"Upload completed {temp_file}")

        try:
            # Get any experiment configs the user has set in WANDB and copy them over to App
            modulename = 'wandb'
            if modulename in sys.modules:
                import wandb
                config = wandb.config
                temp_file = os.path.join(self._output_dir, "wandb.config.json")
                json_log = json.dumps(config.as_dict(), indent=4, sort_keys=True, default=str)
                with open(temp_file, "w") as fd:
                    fd.write(json_log)

                self._logger.debug(f"Uploading WANDB config {temp_file}")
                cp.cp_to_elbo(self._elbo_connector, temp_file, self._target_prefix)
                self._logger.debug(f"Upload completed {temp_file}")
        except Exception as e:
            self._logger.error(f"Unable to get wandb config - {e}")

        for image in self._images:
            shutil.copyfile(image, os.path.join(self._output_dir, os.path.basename(image)))
            cp.cp_to_elbo(self._elbo_connector, image, self._target_prefix)
            self._logger.debug(f"Upload completed {image}")

        self._logger.debug(f"Logs in {self._output_dir}")
        return self._output_dir

    def log_message(self, message):
        message_tile = ProgressTile(name=self.ELBO_MESSAGE_TILE_NAME,
                                    type=ProgressTileType.message,
                                    value=message)
        self._progress_tiles.append(message_tile)

    def log_key_metric(self, key_metric: str, key_metric_value):
        """
        Log a key metric with the given name and value. Note that this overwrites the last value

        :param key_metric: The key metric
        :param key_metric_value: The metric value
        :return:
        """
        numeric_tile = ProgressTile(name=key_metric,
                                    type=ProgressTileType.key_metric_numeric,
                                    value=key_metric_value)
        self._progress_tiles.append(numeric_tile)

    def log_image(self, image_title, image_file_path):
        temp_file_name = tempfile.NamedTemporaryFile(suffix='.png').name
        # Copy the image in case there is a name conflict
        shutil.copyfile(image_file_path, temp_file_name)
        image_tile = ProgressTile(name=image_title,
                                  type=ProgressTileType.image,
                                  value=os.path.basename(temp_file_name))
        self._progress_tiles.append(image_tile)
        self._images.append(temp_file_name)


if __name__ == "__main__":
    _tracker = TaskTracker(experiment_name="Test",
                           experiment_id="TestId")
    _tracker.log_image("Some image", "/root/img.png")
    _tracker.log_image("Some other image", "/root/img2.png")
    _tracker.log_message(f"Do or not do. There is no try.")
    _tracker.log_key_metric('Loss', 0.1)
    _tracker.log_key_metric('KL', -0.112)
    _tracker.log_message(f"Completed experiment")

    _json_output = _tracker.convert_tiles_to_dictionary_with_metadata()
    print(_json_output)
    _tracker.upload_logs()