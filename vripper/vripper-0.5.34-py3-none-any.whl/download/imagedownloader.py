import logging
import os

import requests
from commmons import with_prefix
from gallery_dl.exception import NoExtractorError
from requests import ConnectTimeout, ReadTimeout

from vripper.download import gdlwrapper
from vripper.error import ImagePermanentlyUnavailableError

logger = logging.getLogger("vripper")


def download_image(vimage, pdir, timeout):
    image_logger = with_prefix(logger, f"{vimage.filename} {vimage.main_url}")

    try:
        target_path = os.path.join(pdir, vimage.filename)
        _save_to_disk(image_logger, target_path, timeout, vimage)
        vimage.local_path = target_path
        return {"filename": vimage.filename, "status": "downloaded"}
    except (ConnectTimeout, ReadTimeout, requests.exceptions.ConnectionError) as e:
        image_logger.error(str(e))
    except ImagePermanentlyUnavailableError:
        vimage.is_available = False
    except:
        image_logger.exception("")

    return {"filename": vimage.filename, "status": "failed"}


def _save_to_disk(image_logger, target_path, timeout, vimage):
    """
    Downloads the image and returns the resulting local path.
    """
    try:
        gdlwrapper.download_single_image(vimage.main_url, target_path)
        image_logger.debug(f"Downloaded with: gdlwrapper")
    except NoExtractorError:
        underlying_url = vimage.get_underlying_url(timeout)
        with open(target_path, "wb") as fp:
            r = requests.get(underlying_url, headers={"Referer": vimage.main_url}, stream=True, timeout=timeout)
            fp.writelines(r.iter_content(1024))
        image_logger.debug(f"Downloaded with: native")
