import logging
import multiprocessing
import os
from functools import partial
from multiprocessing.pool import Pool, ThreadPool

from commmons import linear_sample, get_filesize_in_bytes, with_prefix

from vripper.download.gdlwrapper import get_images_from_gallery
from vripper.download.imagedownloader import download_image
from vripper.download.postprogress import PostProgress
from vripper.error import InsufficientFileCountError, ImagePermanentlyUnavailableError, \
    DeprecatedHostError
from vripper.model.vparams import VParams
from vripper.postprocess.imgproc import process_with_constraints, has_enough_pixels, is_valid_image

logger = logging.getLogger("vripper")


def _trim(images, max_filecount):
    if max_filecount and len(images) > max_filecount:
        images_to_download = linear_sample(images, max_filecount)
    else:
        images_to_download = images

    return images_to_download


def _download_multithread(images_to_download, pdir, report_progress, vparams):
    timeout = (vparams.download_connect_timeout, vparams.download_read_timeout,)
    pool = ThreadPool(vparams.dl_threadpool_size)
    partial_func = partial(download_image, pdir=pdir, timeout=timeout)
    rs = pool.imap_unordered(partial_func, images_to_download)

    for image_update in rs:
        report_progress(image_update)

    pool.close()
    pool.join()


def _process_with_pool(paths, vparams, report_progress):
    cc = multiprocessing.cpu_count()
    if vparams.pp_pool_size > cc:
        # Warn the user if they use processing_pool_size > cc.
        logger.warning(f"processing_pool_size={vparams.pp_pool_size} is larger than cpu_count={cc}")
    pool = Pool(vparams.pp_pool_size)
    partial_func = partial(process_with_constraints, vparams=vparams)
    rs = pool.imap_unordered(partial_func, paths)

    for image_update in rs:
        report_progress(image_update)

    pool.close()
    pool.join()


def _raise_for_initial_hitrate(images_to_download, vparams):
    if len(images_to_download) == 0:
        raise ImagePermanentlyUnavailableError("The post has zero images")
    if len(images_to_download) < vparams.min_filecount:
        raise InsufficientFileCountError(f"Need {vparams.min_filecount} images. Found {len(images_to_download)}.")
    _raise_for_deprecated_hosts(images_to_download, vparams)


def _raise_for_deprecated_hosts(images_to_download, vparams):
    deprecated_hosts = [vi.parser_object.name for vi in images_to_download if
                        vi.parser_object is not None and vi.parser_object.is_deprecated]
    hitrate = 1 - len(deprecated_hosts) / len(images_to_download)
    if hitrate < vparams.min_hitrate:
        raise DeprecatedHostError(f"Deprecated host(s): " + " ".join(set(deprecated_hosts)))


def _raise_for_availability(images, vparams):
    # After the download, .is_available is updated
    len_unavailable = [vimage for vimage in images if not vimage.is_available]
    if (1 - vparams.min_hitrate) < len(len_unavailable) / len(images):
        msg = f"At least {len(len_unavailable)} out of {len(images)} images are unavailable"
        raise ImagePermanentlyUnavailableError(msg)


def _postprocess(pathmap, vparams, pprog):
    # Resize the images if applicable
    if vparams.is_postprocessing_enabled:
        if vparams.pp_pool_size > 0:
            _process_with_pool(pathmap.values(), vparams, pprog.report)
        else:
            for path in pathmap.values():
                process_with_constraints(path, vparams=vparams)


def _delete_invalid_files(pathmap, vparams):
    # Delete invalid/large files
    for filename, path in pathmap.items():
        if not os.path.exists(path):
            image_logger.warning("File does not exist")
            continue

        should_delete = False
        image_logger = with_prefix(logger, filename)
        filesize = get_filesize_in_bytes(path)

        if filesize > vparams.max_filesize or filesize < vparams.min_filesize:
            image_logger.debug("Filesize too big or too small")
            should_delete = True
        elif not is_valid_image(path):
            image_logger.warning("Invalid image")
            should_delete = True
        elif not has_enough_pixels(path, vparams.min_dimension):
            image_logger.warning("The resolution is too low")
            should_delete = True

        if should_delete:
            os.remove(path)


def _evaluate_final_hitrate(images, pathmap, vparams):
    final_filecount = len([path for path in pathmap.values() if os.path.exists(path)])
    final_hitrate = final_filecount / len(images)
    if final_hitrate < vparams.min_hitrate:
        msg = f"Hitrate requirements not met; final_hitrate={final_hitrate}"
        raise InsufficientFileCountError(msg)
    return final_filecount


def download_post(vpost, tdir, vparams: VParams, callback):
    pdir = os.path.join(tdir, str(vpost.id))
    os.makedirs(pdir, exist_ok=True)

    if vpost.is_gallery:
        vpost.images = get_images_from_gallery(vpost.url)

    images = _trim(vpost.images, vparams.max_filecount)
    _raise_for_initial_hitrate(images, vparams)

    pprog = PostProgress(vpost, len(images), vparams.is_postprocessing_enabled, callback)
    pprog.report()

    # Download the images
    _download_multithread(images, pdir, pprog.report, vparams)

    # Post-download activities
    pathmap = {vimage.filename: vimage.local_path for vimage in images if vimage.local_path}
    _raise_for_availability(images, vparams)
    _postprocess(pathmap, vparams, pprog)
    _delete_invalid_files(pathmap, vparams)
    return _evaluate_final_hitrate(images, pathmap, vparams)
