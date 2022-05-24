""" process_mask.py

Mask proccessing "binary" file
"""
# Built-in imports
import os

# third parties imports
import xarray as xr

# own package imports
from mfire import Settings, CLI, get_logger
from mfire.utils import JsonFile, MD5, Parallel
import mfire.mask.mask_processor as mpr

# Logging
LOGGER = get_logger(name="process_mask.mod", bind="process_mask")


def main(conf: dict):
    """main : main function

    Args:
        conf (dict): Single mask configuration
        grid_file (str): Path to a netcdf file defining grids
    """
    # Quelques checks à faire au prealable
    do_something = True
    #  Si la conf contient le fichier on l'utilise.
    #  Sinon on suppose qu'on cree le fichier quoiqu'il arrive
    if "file" in conf:
        LOGGER.info("File is in the conf")
        output_file = conf.get("file")
        LOGGER.info(output_file)
        LOGGER.info(os.path.exists(output_file))
        if os.path.exists(output_file):
            LOGGER.info("File already exist")
            if "mask_hash" in conf:
                current_hash = conf.get("mask_hash")
            else:
                handler = MD5(conf["geos"])
                current_hash = handler.hash
            LOGGER.info("Current conf hash is %s", current_hash)
            ds = xr.open_dataset(output_file)
            if ds.attrs.get("md5sum", "") == current_hash:
                do_something = False
            else:
                LOGGER.info("Current hash is different from the one in the file")
            ds.close()
    if do_something:
        LOGGER.info("Launching mask creation")
        mask_handler = mpr.MaskProcessor(conf)
        mask_handler.create_masks()
    else:
        LOGGER.info(
            "Mask already exist and have the same md5sum. Mask creation is skipped."
        )
    LOGGER.info(f"Mask {output_file} has been created")


if __name__ == "__main__":
    # Argument parsing
    args = CLI().parse_args()
    print(args)

    dict_config = JsonFile(Settings().mask_config_filename).load()

    parallel = Parallel(processes=args.nproc)
    for name, conf in dict_config.items():
        parallel.apply(main, args=(conf,), name=name)
    parallel.run(timeout=Settings().timeout)
