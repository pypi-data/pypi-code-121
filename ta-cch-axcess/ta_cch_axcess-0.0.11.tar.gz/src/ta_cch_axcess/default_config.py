from tempfile import TemporaryDirectory
import os
from . import logger


class MODES:
    DEV = "DEV"
    PRD = "PRD"


class CONFIG:
    MODE = "DEV"

    logger.info(f"Configuring for {MODE}")
    if MODE == MODES.DEV:
        os.environ["RPA_SECRET_MANAGER"] = "RPA.Robocorp.Vault.FileSecrets"
        os.environ["RPA_SECRET_FILE"] = r"D:\Users\thoughtful_auto2\Documents\secrets.json"

    class PATHS:
        TEMP = TemporaryDirectory().name
        CCH_PATH = r"C:\Program Files (x86)\WK\ProSystem fx Suite\Smart Client\SaaS\CCH.CommonUIFramework.Shell.exe"
