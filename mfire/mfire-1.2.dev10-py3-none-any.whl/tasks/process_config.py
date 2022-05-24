""" process_config.py

Configuration proccessing "binary" file
Processes a "global" configuration file and, given a production date, infers
"version", "data", "mask" and "production" configurations
"""

from mfire import Settings, CLI
from mfire.utils import JsonFile
from mfire.configuration.config_processor import ConfigMetronomeProcessor


if __name__ == "__main__":
    # Arguments parsing
    args = CLI().parse_args()
    print(args)

    # Filenames
    settings = Settings()

    # Running the config processor
    config_processor = ConfigMetronomeProcessor(
        config_filename=settings.config_filename,
        rules=args.rules,
        drafting_datetime=args.draftdate,
    )
    # Retrieving processed configs
    mask_dico, data_dico, prod_dico = config_processor.process_all(nproc=args.nproc)

    # Dumping configs
    JsonFile(settings.mask_config_filename).dump(mask_dico)
    JsonFile(settings.data_config_filename).dump(data_dico)
    JsonFile(settings.prod_config_filename).dump(prod_dico)
    JsonFile(settings.version_config_filename).dump(config_processor.version_config)
