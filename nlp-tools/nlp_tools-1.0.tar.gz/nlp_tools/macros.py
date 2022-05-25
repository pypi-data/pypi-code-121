import os
from pathlib import Path
from typing import Dict

DATA_PATH = os.path.join(str(Path.home()), '.nlp_tools')

Path(DATA_PATH).mkdir(exist_ok=True, parents=True)



class Config(object):

    def __init__(self):
        self.verbose = False

    def to_dict(self):
        return {
            'verbose': self.verbose
        }


config = Config()

if __name__ == "__main__":
    print("Hello world")
