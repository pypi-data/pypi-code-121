import os

PACKAGE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PACKAGE_DIR, "data")
RES_DIR = os.path.join(PACKAGE_DIR, "res")

# Ensure that the `$PACKAGE/data` dir exists
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

CACHE_DIR = os.path.join(DATA_DIR, "cache")
PLOT_DIR = os.path.join(DATA_DIR, "plots")

# Secondary DB config
_CLEAN_DB_CONFIG_FILENAME = "clean-db.cfg"

# Check if config-file lies in directory of execution
# If not, consider working with the global one
if os.path.exists(_CLEAN_DB_CONFIG_FILENAME):
    CLEAN_DB_CONFIG_FILE = os.path.abspath(_CLEAN_DB_CONFIG_FILENAME)
else:
    CLEAN_DB_CONFIG_FILE = os.path.join(DATA_DIR, _CLEAN_DB_CONFIG_FILENAME)

    # If there is no global file, generate a new one
    if not os.path.isfile(CLEAN_DB_CONFIG_FILE):
        from CleanEmonCore.setup_scripts import generate_config
        generate_config(CLEAN_DB_CONFIG_FILE)


NILM_INFERENCE_APIS_DIR = "/home/george/PycharmProjects/CleanEmon/NILM-Inference-APIs"  # todo: Procedural definition
assert os.path.exists(NILM_INFERENCE_APIS_DIR), (
    f"Please specify the directory of NILM-Inference-APIs at `NILM_INFERENCE_APIS_DIR` in {__file__} and re-run"
)
NILM_INFERENCE_APIS_DIR = os.path.abspath(NILM_INFERENCE_APIS_DIR)

NILM_INPUT_DIR = os.path.join(NILM_INFERENCE_APIS_DIR, "input", "data")
if not os.path.exists(NILM_INPUT_DIR):
    os.makedirs(NILM_INPUT_DIR, exist_ok=True)

NILM_INPUT_FILE_PATH = os.path.join(NILM_INPUT_DIR, "data.csv")
