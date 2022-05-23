# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import asyncio, path
from suanpan.utils import convert


def read(file, *args, **kwargs):
    import cv2  # pylint: disable=import-outside-toplevel

    img = cv2.imread(file, *args, **kwargs)  # pylint: disable-msg=e1101
    if img is None:
        raise Exception(f"Image read failed: {file}")
    return img


def _save(file, image):
    import cv2  # pylint: disable=import-outside-toplevel

    path.safeMkdirsForFile(file)
    success = cv2.imwrite(file, image)  # pylint: disable-msg=e1101
    if not success:
        path.remove(file)
        raise Exception(f"Image save failed: {file}")
    return file


def _saveflat(file, data):
    image = convert.flatAsImage(data)
    return _save(file, image)


def _savegif(file, data):
    import imageio  # pylint: disable=import-outside-toplevel

    image3D = convert.to3D(data)
    path.safeMkdirsForFile(file)
    imageio.mimsave(file, image3D)
    return file


def save(file, data, flag=None):
    mapping = {None: _save, "flat": _saveflat, "animated": _savegif}
    func = mapping.get(flag)
    if not func:
        raise Exception(f"Unknow flag: {flag}")
    return func(file, data)


def saves(filepathPrefix, images):
    counts = len(images)
    n = len(str(counts))
    iterable = (
        (f"{filepathPrefix}_{str(index).zfill(n)}.png", image)
        for index, image in enumerate(images)
    )
    asyncio.starmap(_save, iterable)
    return filepathPrefix


def saveall(filepathPrefix, data):
    image3D = convert.to3D(data)
    layers = len(image3D)
    n = len(str(layers))
    runners = [
        asyncio.run(_save, f"{filepathPrefix}_{str(index).zfill(n)}.png", image)
        for index, image in enumerate(image3D)
    ]
    runners.append(asyncio.run(_saveflat, f"{filepathPrefix}.png", image3D))
    runners.append(asyncio.run(_savegif, f"{filepathPrefix}.gif", image3D))
    asyncio.wait(runners)
    return filepathPrefix


def resize(data, size):
    import cv2  # pylint: disable=import-outside-toplevel

    return cv2.resize(data, size)  # pylint: disable-msg=e1101
