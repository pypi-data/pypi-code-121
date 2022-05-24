""" preprocess_data.py

Preprocessing data 'binary' file
Preprocesses raw model data files (grib files) according to a given "data" configuration
"""
from mfire import CLI, Settings
from mfire.data.data_preprocessor import DataPreprocessor

if __name__ == "__main__":
    # Arguments parsing
    args = CLI().parse_args()
    print(args)

    # Preprocessing
    preprocessor = DataPreprocessor(Settings().data_config_filename, args.rules)
    preprocessor.preprocess(nproc=args.nproc)
