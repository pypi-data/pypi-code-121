from importlib import resources
from argparse import Namespace
import json

def load_config() -> Namespace:
    config = json.loads(resources.read_text(__name__, 'config.json'))
    return Namespace(**config)