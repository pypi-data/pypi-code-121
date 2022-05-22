import logging
import os
import shutil

from commmons import create_zip

from vripper.download.gdlwrapper import configure_gallerydl
from vripper.download.postdownloader import download_post
from vripper.download.threadprogress import ThreadProgress
from vripper.enum.downloadmode import DownloadMode
from vripper.enum.outputformat import OutputFormat
from vripper.forum.threadfactory import get_thread
from vripper.model.vparams import VParams

logger = logging.getLogger("vripper")


def get_posts_to_download(posts, mode) -> list:
    if mode == DownloadMode.ALL_POSTS:
        posts_to_download = posts
    elif mode == DownloadMode.ALL_POSTS_WITH_IMAGES:
        posts_to_download = [p for p in posts if len(p.images)]
    elif mode == DownloadMode.FIRST_POST_ONLY:
        posts_to_download = posts[:1]
    else:
        raise NotImplementedError

    return posts_to_download


def download_thread(
        thread_url: str,
        dest: str,
        mode: DownloadMode = DownloadMode.FIRST_POST_ONLY,
        output_format: str = None,
        callback=None,
        **kwargs
):
    if callback:
        raise NotImplementedError

    vparams = VParams(kwargs)
    vthread = get_thread(thread_url)
    dest = os.path.abspath(dest)

    configure_gallerydl(vparams, dest)

    posts_to_download = get_posts_to_download(vthread.posts, mode)

    tp = ThreadProgress(callback, vthread, len(posts_to_download))

    tdir = os.path.join(dest, str(vthread.id))
    os.makedirs(tdir, exist_ok=True)

    filecount = 0
    for post in posts_to_download:
        filecount += download_post(post, tdir=tdir, vparams=vparams, callback=tp.report)

    final_path = tdir
    if output_format == OutputFormat.ZIP:
        zip_path = create_zip(basename=tdir, source_dir=tdir)
        final_path = os.path.join(dest, zip_path)
        logger.info(f"zip created final_path={final_path}")
        shutil.rmtree(tdir)
        logger.info(f"temporary folder deleted tdir={tdir}")

    tp.report()

    return {
        "thread_title": vthread.title,
        "path": final_path,
        "filecount": filecount
    }
