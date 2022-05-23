# coding=utf-8
from __future__ import absolute_import, print_function

import base64
import hashlib
import os
import shutil

from suanpan import asyncio, g


def safeMkdirs(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
    return path


def safeMkdirsForFile(filepath):
    return safeMkdirs(os.path.dirname(os.path.abspath(filepath)))


def mkdirs(path, parent=False):
    mkdirFunction = safeMkdirsForFile if parent else safeMkdirs
    return mkdirFunction(path)


def merge(paths, dist, mode="move"):
    safeMkdirs(dist)
    mergeFunc = getattr(shutil, mode)
    for path in paths:
        if os.path.isfile(path):
            mergeFunc(path, dist)
        else:
            for p in os.listdir(path):
                subpath = os.path.join(path, p)
                mergeFunc(subpath, dist)
            if mode == "move":
                os.rmdir(path)
    return dist


def md5(filepath, block_size=64 * 1024):
    with open(filepath, "rb") as f:
        _md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            _md5.update(data)
    return base64.b64encode(_md5.digest()).decode()


def empty(folder):
    def _safeListDir(folder):
        try:
            return os.listdir(folder)
        except OSError:
            return []

    for path in _safeListDir(folder):
        remove(os.path.join(folder, path))
    return folder


def remove(path, ignore=True):
    removeFunction = removeFile if os.path.isfile(path) else removeFolder
    try:
        return removeFunction(path)
    except Exception as e:  # pylint: disable=broad-except
        if ignore:
            return path
        raise e


def removeFile(filePath):
    os.remove(filePath)
    return filePath


def removeFolder(folderPath):
    shutil.rmtree(folderPath)
    return folderPath


def removeEmptyFolders(folderPath, ignore=True):
    try:
        os.removedirs(folderPath)
        return folderPath
    except Exception as e:  # pylint: disable=broad-except
        if ignore:
            return folderPath
        raise e


def removeEmptyFoldersTo(name, to_path, ignore=True):
    try:
        os.rmdir(name)
        head, tail = os.path.split(name)
        if not tail:
            head, tail = os.path.split(head)
        while head and tail:
            if head == to_path:
                break
            try:
                os.rmdir(head)
            except OSError:
                break
            head, tail = os.path.split(head)

        return name
    except Exception as e:  # pylint: disable=broad-except
        if ignore:
            return name
        raise e


def copy(src, dst, ignore=False):
    if not os.path.exists(src):
        if ignore:
            return dst
        raise FileNotFoundError(src)
    copyFunction = copyFile if os.path.isfile(src) else copyFolder
    try:
        return copyFunction(src, dst)
    except Exception as e:  # pylint: disable=broad-except
        if ignore:
            return dst
        raise e


def copyFile(src, dst):
    mkdirs(dst, parent=True)
    shutil.copyfile(src, dst)
    return dst


def copyFolder(src, dst):
    remove(dst)
    mkdirs(dst, parent=True)
    shutil.copytree(src, dst)
    return dst


def getPathDepth(root, path):
    root = root.rstrip(os.sep)
    path = path.rstrip(os.sep)
    return path[len(root):].count(os.sep)


def listdir(path, depth=1):
    folders, files = [], []
    for root, folders, files in os.walk(path):
        if depth is True or getPathDepth(path, root) < depth:  # pylint: disable=arguments-out-of-order
            folders.extend([os.path.join(root, folder) for folder in folders])
            files.extend([os.path.join(root, file) for file in files])
    return folders, files


def listFiles(path, depth=True):
    return listdir(path, depth=depth)[1]


def listFolders(path, depth=True):
    return listdir(path, depth=depth)[0]


def replaceBasePath(src, dst, *paths):
    src = src.rstrip(os.sep)
    dst = dst.rstrip(os.sep)
    return [path.rstrip(os.sep).replace(src, dst) for path in paths]


def link(src, dst):
    mkdirs(dst, parent=True)
    return os.link(src, dst)


def symlink(src, dst):
    isdir = not os.path.isfile(src)
    mkdirs(dst, parent=True)
    return os.symlink(src, dst, isdir)


# Concurrent Funcs


def cremove(path):
    removeFunction = cremoveFile if os.path.isfile(path) else cremoveFolder
    return removeFunction(path)


def cremoveFile(filePath):  # pylint: disable=unused-argument
    return removeFile(filePath)


def cremoveFolder(folderPath):
    cempty(folderPath)
    return remove(folderPath)


def cempty(folderPath):
    folders, files = listdir(folderPath, depth=True)
    asyncio.map(remove, files, pbar="Removing Files")
    asyncio.map(remove, folders, pbar="Removing Folders")
    return folderPath


def ccopy(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    copyFunction = ccopyFile if os.path.isfile(src) else ccopyFolder
    return copyFunction(src, dst)


def ccopyFile(src, dst):  # pylint: disable=unused-argument
    return copyFile(src, dst)


def ccopyFolder(src, dst):
    folders, files = listdir(src, depth=True)
    newfolders = replaceBasePath(src, dst, *folders)
    newfiles = replaceBasePath(src, dst, *files)
    mkdirs(dst)
    asyncio.map(mkdirs, newfolders, pbar="Making Folders")
    asyncio.starmap(copy, zip(files, newfiles), pbar="Copying Files")
    return dst


def rootDir():
    if g.desktopHome:
        return os.path.join(g.desktopHome, "run", g.userId, g.appId, g.nodeId)
