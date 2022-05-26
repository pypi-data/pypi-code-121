from pathlib import Path
from typing import Sequence

from pydantic import BaseModel, validator
from strictyaml import load, YAML
import tensorboard

# Project Directories
CONFIG_FILE_PATH = Path("config/config.yml")

"""
Configuration setup inspired by
https://github.com/trainindata/testing-and-monitoring-ml-deployments/tree/master/packages/gradient_boosting_model
"""


class ModelCheckpointConfig(BaseModel):
    monitor: str
    mode: str
    save_best_only: bool
    save_weights_only: bool


class TensorBoardConfig(BaseModel):
    update_freq: int


class EarlyStoppingConfig(BaseModel):
    monitor: str
    mode: str
    min_delta: int
    patience: int


class FileNameConfig(BaseModel):
    # file names
    model_weights: str
    raw_data: str
    representations: str
    captions: str
    images: str
    idx_to_word: str
    word_to_idx: str
    predictions: str


class Config(BaseModel):
    filenames: FileNameConfig
    early_stopping: EarlyStoppingConfig
    tensorboard: TensorBoardConfig
    model_checkpoint: ModelCheckpointConfig

    # data locations
    input_filepath: str
    output_filepath: str
    model_folder: str
    log_folder: str

    # set train/test split
    test_val_size: int
    random_state: int

    # training
    batch_size: int
    epochs: int
    learning_rate: float
    experiment_name: str
    verbose: bool
    loss: str
    metric: str


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Path = None) -> YAML:
    """Parse YAML."""
    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    # specify the data attribute from the strictyaml YAML type.
    _config = Config(
        filenames=FileNameConfig(**parsed_config.data),
        early_stopping=EarlyStoppingConfig(**parsed_config.data),
        tensorboard=TensorBoardConfig(**parsed_config.data),
        model_checkpoint=ModelCheckpointConfig(**parsed_config.data),
        **parsed_config.data,
    )

    return _config


config = create_config()
