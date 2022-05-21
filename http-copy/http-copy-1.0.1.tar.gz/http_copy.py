import os
import argparse
import pathlib
import fnmatch
from typing import Union

import tqdm
import requests


def upload_file(local_path, remote_url, params=None):
    with open(local_path, "rb") as f:
        return requests.post(
            f"{remote_url}?{params if params is not None else ''}",
            data=f
        )


def load_ignores(path):
    with open(path, "r") as f:
        return list(filter(lambda x: x and not x.startswith("#"), 
                           map(lambda x: x.strip(), f)))


def upload_dir(
        local_dir: Union[pathlib.Path, str],
        remote_url, 
        ignores=None, 
        disable_tqdm=False, 
        params=None
):
    if isinstance(local_dir, str):
        local_dir = pathlib.Path(local_dir)

    assert local_dir.is_dir()

    ignores = ignores or []
    filepaths = list(filter(lambda x: not x.is_dir(), 
                            local_dir.rglob("*")))
    
    # apply ".*ignore"
    for ignore in ignores:
        filepaths = [p for p in filepaths 
                     if not fnmatch.fnmatch(p.name, ignore)]
    
    total_size = sum(filepath.stat().st_size for filepath in filepaths)
    progress_bar = tqdm.tqdm(
        total=total_size, 
        unit="B", 
        unit_scale=True,
        disable=disable_tqdm
    )
    
    for filepath in filepaths:
        relpath = filepath.relative_to(local_dir)
        progress_bar.set_description(f"uploading '{relpath}'")
        url = os.path.join(remote_url, relpath)
        resp = upload_file(filepath, url, params=params)
        assert resp.status_code / 100 == 2
        progress_bar.update(filepath.stat().st_size)


def main():
    parser = argparse.ArgumentParser(
        "Upload a file or all files in a directory recursively through HTTP. "
        "Supports ignore-like file."
    )
    parser.add_argument("local_path_or_dir")
    parser.add_argument("remote_url")
    parser.add_argument("--params", help="Additional URL params")
    parser.add_argument("--ignore-file")
    parser.add_argument("--disable-tqdm", action="store_true", default=False)
    args = parser.parse_args()

    local_path_or_dir = pathlib.Path(args.local_path_or_dir)
    assert local_path_or_dir.exists()

    if local_path_or_dir.is_dir():
        ignores = None
        if args.ignore_file is not None:
            ignores = load_ignores(args.ignore_file)

        upload_dir(
            local_dir=local_path_or_dir,
            remote_url=args.remote_url,
            ignores=ignores,
            disable_tqdm=bool(args.disable_tqdm),
            params=args.params
        )
    else:
        upload_file(
            local_dir=local_path_or_dir,
            remote_url=args.remote_url,
            params=args.params
        )


if __name__ == "__main__":
    main()