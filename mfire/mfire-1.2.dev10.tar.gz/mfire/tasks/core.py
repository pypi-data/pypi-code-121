""" core.py

Core "binary" file
Compute risks and texts and exports them to JSON
"""

# Own package imports
from mfire import Settings, CLI
from mfire.production import ProductionManager

# Logging

if __name__ == "__main__":
    # Arguments parsing
    args = CLI().parse_args()
    print(args)
    production_manager = ProductionManager.load(Settings().prod_config_filename)
    production_manager.compute(nproc=args.nproc)
