from pathlib import Path
from typing import Dict, List, Sequence

from pydantic import BaseModel
from strictyaml import YAML, load

import TweetAnalysis

# Project Directories
PACKAGE_ROOT = Path(TweetAnalysis.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"


class AppConfig(BaseModel):
    """
    Application-level config.
    """

    PACKAGE_NAME: str
    DATA_FILE_PATH: str
    MODELS_PATH: str
    # PACKAGE_SAVE_FILE: str
    SEED: int
    DATASET_COLUMNS: List[str]
    DATASET_ENCODING: str

    MODEL_NAME: str
    TOKENIZER_NAME: str
    CLASSES_NAME: str
    EMBEDDED_MATRIX_NAME: str


class TwitterConfig(BaseModel):
    """
    Twitter-level config.
    """


class KafkaConfig(BaseModel):
    """
    Kafka-level config.
    """

    KAFKA_TOPIC_NAME: str
    KAFKA_HOST: str

class CassandraConfig(BaseModel):
    """
    Cassandra-level config.
    """

    CASSANDRA_HOST: str

class ModelConfig(BaseModel):
    """
    All configuration relevant to model
    training and feature engineering.
    """

    TARGET: str
    NEUTRAL_MIN: float
    NEUTRAL_MAX: float
    CLASSES: List[str]
    NEGATIVE_INDEX: int
    NEUTRAL_INDEX: int
    POSITIVE_INDEX: int
    TEST_SIZE: float
    INPUT_LEN: int
    VOCAB_LEN: int
    EMBEDDING_DIMENSIONS: int
    EPOCHS: int
    BATCH_SIZE: int


class Config(BaseModel):
    """Master config object."""

    app: AppConfig
    twitter: TwitterConfig
    kafka: KafkaConfig
    cassandra: CassandraConfig
    model: ModelConfig


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")


def fetch_config_from_yaml(cfg_path: Path = None) -> YAML:
    """Parse YAML containing the package configuration."""

    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    # specify the data attribute from the strictyaml YAML type.
    _config = Config(
        app=AppConfig(**parsed_config.data),
        twitter=TwitterConfig(**parsed_config.data),
        kafka=KafkaConfig(**parsed_config.data),
        cassandra=CassandraConfig(**parsed_config.data),
        model=ModelConfig(**parsed_config.data),
    )

    return _config


config = create_and_validate_config()
