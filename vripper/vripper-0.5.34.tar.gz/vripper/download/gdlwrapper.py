import logging
import os

import gallery_dl
from gallery_dl.exception import AuthorizationError, NotFoundError
from gallery_dl.extractor.message import Message
from gallery_dl.job import DownloadJob, UrlJob

from vripper.error import ImagePermanentlyUnavailableError
from vripper.model.vimage import VImage
from vripper.model.vparams import VParams


def configure_gallerydl(vparams: VParams, dest: str):
    """
    Configures gdl. Only needs to run once in each process. The configs are shared across threads.
    :param vparams:
    :param dest:
    :return:
    """

    # Set download timeout
    timeout = (vparams.download_connect_timeout, vparams.download_read_timeout,)
    gallery_dl.config.set(("downloader", "http",), "timeout", timeout)

    # Set download path
    gallery_dl.config.set((), "extractor", {"base-directory": dest})

    # Mute internal logs
    gallery_dl.config.set(("output",), "mode", "null")
    logging.getLogger("gallery-dl").setLevel(logging.CRITICAL)
    logging.getLogger("download").setLevel(logging.CRITICAL)


def _get_url_from_msg(msg):
    if msg[0] == Message.Url:
        _, url, kwdict = msg
        return url
    return None


def _get_image_urls(gallery_url):
    urlj = UrlJob(gallery_url)
    urlj.run()

    image_urls = list()
    for msg in urlj.extractor:
        image_url = _get_url_from_msg(msg)
        if image_url:
            image_urls.append(image_url)
    return image_urls


def get_images_from_gallery(gallery_url):
    try:
        image_urls = _get_image_urls(gallery_url)
    except (AuthorizationError, NotFoundError) as e:
        raise ImagePermanentlyUnavailableError(str(e))
    return [
        VImage(index_in_post=i, url=url)
        for i, url in enumerate(image_urls)
    ]


def download_single_image(url, target_path):
    dlj = DownloadJob(url)

    base_dir = gallery_dl.config.get((), "extractor")["base-directory"]
    target_path_rel = target_path.lstrip(base_dir)

    dlj.extractor.directory_fmt = tuple(os.path.dirname(target_path_rel).split(os.path.sep))
    dlj.extractor.filename_fmt = "{filename}.{extension}"
    dlj.run()

    path = os.path.join(os.path.dirname(target_path), dlj.pathfmt.filename)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    os.replace(path, target_path)
