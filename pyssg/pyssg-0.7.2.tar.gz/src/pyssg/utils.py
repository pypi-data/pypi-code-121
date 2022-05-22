import os
import sys
import shutil
from hashlib import md5
from logging import Logger, getLogger

log: Logger = getLogger(__name__)


def get_file_list(path: str,
                  exts: list[str],
                  exclude: list[str]=None) -> list[str]:
    log.debug('retrieving file list in path "%s" that contain file'
              ' extensions (%s) except (%s)',
              path, ', '.join(exts),
              ', '.join(exclude if exclude is not None else []))
    out: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude is not None:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]

        for f in files:
            if f.endswith(tuple(exts)):
                stripped_f: str = os.path.join(root, f).replace(path, '')[1:]
                out.append(stripped_f)
                log.debug('added file "%s" without "%s" part: "%s"',
                          f, path, stripped_f)
            else:
                log.debug('ignoring file "%s" as it doesn\'t contain'
                          ' any of the extensions (%s)', f, ', '.join(exts))

    return out


def get_dir_structure(path: str,
                      exclude: list[str]=None) -> list[str]:
    log.debug('retrieving dir structure in path "%s" except (%s)',
              path, ', '.join(exclude if exclude is not None else []))
    out: list[str] = []
    for root, dirs, files in os.walk(path):
        if exclude is not None:
            log.debug('removing excludes from list')
            dirs[:] = [d for d in dirs if d not in exclude]

        for d in dirs:
            if root in out:
                out.remove(root)
                log.debug('removed dir "%s" as it already is in the list', root)
            joined_dir: str = os.path.join(root, d)
            out.append(joined_dir)
            log.debug('added dir "%s" to the list', joined_dir)

    log.debug('removing "%s" from all dirs in list', path)
    return [o.replace(path, '')[1:] for o in out]


def create_dir(path: str, p: bool=False, silent=False) -> None:
    try:
        if p:
            os.makedirs(path)
        else:
            os.mkdir(path)
        if not silent: log.info('created directory "%s"', path)
    except FileExistsError:
        if not silent: log.info('directory "%s" already exists, ignoring', path)


def copy_file(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        log.info('copied file "%s" to "%s"', src, dst)
    else:
        log.info('file "%s" already exists, ignoring', dst)


# as seen in SO: https://stackoverflow.com/a/1131238
def get_checksum(path: str) -> str:
    log.debug('calculating md5 checksum for "%s"', path)
    file_hash = md5()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            file_hash.update(chunk)

    return file_hash.hexdigest()


def get_expanded_path(path: str) -> None:
    log.debug('expanding path "%s"', path)
    expanded_path: str = os.path.normpath(os.path.expandvars(path))
    if '$' in expanded_path:
        log.error('"$" character found in expanded path "%s";'
                  ' could be due to non-existant env var.', expanded_path)
        sys.exit(1)
    log.debug('expanded path "%s" to "%s"', path, expanded_path)

    return expanded_path
