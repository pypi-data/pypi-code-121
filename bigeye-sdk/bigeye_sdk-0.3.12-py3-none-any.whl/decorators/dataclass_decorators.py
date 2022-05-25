import inspect
import yaml

from bigeye_sdk.log import get_logger

log = get_logger(__file__)


def add_from_dict(cls):
    def from_dict(env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })

    cls.from_dict = from_dict
    return cls


def loadable(cls):
    # As of YAML 1.2, YAML is a true superset of JSON and you can use the yaml.safe_load call to
    # properly load JSON or YAML files.
    def load_from_file(source_config_file: str):
        with open(source_config_file, 'r') as stream:
            bsc = cls(**yaml.safe_load(stream))
            if bsc is None:
                raise Exception('Could not load from disk.')
            log.info(f'Loaded instance of {bsc.__class__.__name__} from disk: {source_config_file}')
            return bsc

    cls.load_from_file = load_from_file
    return cls
