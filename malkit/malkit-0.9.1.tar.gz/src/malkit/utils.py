import functools
import shutil
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from ._parallel import execute_parallel
from ._typing import FilePath

__all__ = [
    "categorize_folders",
    "split_labels",
    "build_srcs_dsts",
    "convert_bytes_to_binary",
    "convert_bytes_to_binary_parallel",
]


def categorize_folders(root: FilePath, labels: pd.DataFrame, *, suffix: Optional[str] = None) -> None:
    """Categorize samples and move them into class name folders."""

    root = Path(root)
    sample_names = [str(item) for item in labels.iloc[:, 0]]
    target_names = [str(item) for item in labels.iloc[:, 1]]

    for klass in set(target_names):
        cat_dir = root / klass
        if cat_dir.is_dir():
            return
        cat_dir.mkdir(parents=True, exist_ok=True)

    for sample_name, target_name in zip(sample_names, target_names):
        src = root / sample_name
        if suffix is not None:
            src = src.with_suffix(suffix)
        shutil.move(src, root / target_name)


def split_labels(
    labels: pd.DataFrame,
    *,
    test_size: Optional[float] = None,
    train_size: Optional[float] = None,
    random_state: Optional[int] = None,
    shuffle: bool = True,
    stratified: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split labels into two parts."""

    from sklearn.model_selection import train_test_split

    stratify = None
    if shuffle and stratified:
        stratify = labels.iloc[:, 1].to_numpy()

    indices = np.arange(len(labels))
    idx1, idx2 = train_test_split(
        indices,
        test_size=test_size,
        train_size=train_size,
        random_state=random_state,
        shuffle=shuffle,
        stratify=stratify,
    )
    return labels.iloc[idx1], labels.iloc[idx2]


def _build_srcs_dsts(
    src_dir: Path, dst_dir: Path, *, skip_exist: bool = True, suffix: Optional[str] = None
) -> Tuple[List[Path], List[Path]]:
    srcs = []
    dsts = []
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in src_dir.iterdir():
        if suffix is None:
            name = src.name
        else:
            name = src.with_suffix(suffix).name
        dst = dst_dir / name
        if skip_exist and dst.exists():
            continue
        srcs.append(src)
        dsts.append(dst)
    return srcs, dsts


def _build_srcs_dsts_cat(
    src_dir: Path, dst_dir: Path, *, skip_exist: bool = True, suffix: Optional[str] = None
) -> Tuple[List[Path], List[Path]]:
    srcs = []
    dsts = []
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_cat_dir in src_dir.iterdir():
        dst_cat_dir = dst_dir / src_cat_dir.name
        dst_cat_dir.mkdir(parents=True, exist_ok=True)
        for src in src_cat_dir.iterdir():
            if suffix is None:
                name = src.name
            else:
                name = src.with_suffix(suffix).name
            dst = dst_cat_dir / name
            if skip_exist and dst.exists():
                continue
            srcs.append(src)
            dsts.append(dst)
    return srcs, dsts


def build_srcs_dsts(
    src_dir: FilePath, dst_dir: FilePath, *, cat: bool = True, skip_exist: bool = True, suffix: Optional[str] = None
) -> Tuple[List[Path], List[Path]]:
    """Build source paths and destination paths."""

    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    if cat:
        return _build_srcs_dsts_cat(src_dir, dst_dir, suffix=suffix, skip_exist=skip_exist)
    else:
        return _build_srcs_dsts(src_dir, dst_dir, suffix=suffix, skip_exist=skip_exist)


def convert_bytes_to_binary(bytes_file: FilePath, binary_file: FilePath, *, qq: str = "00") -> None:
    """Convert bytes file to binary file."""

    with open(bytes_file, "r", encoding="ascii") as src, open(binary_file, "wb") as dst:
        for line in src:
            i = line.find(" ")
            if i < 0:
                raise ValueError(f"invalid bytes file {bytes_file!r}")
            data = line[i + 1 :].replace("??", qq)
            dst.write(bytes.fromhex(data))


def convert_bytes_to_binary_parallel(
    bytes_files: Iterable[FilePath],
    binary_files: Iterable[FilePath],
    *,
    qq: str = "00",
    n_jobs: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Convert bytes file to binary file in parallel."""

    function = functools.partial(convert_bytes_to_binary, qq=qq)
    execute_parallel(function, bytes_files, binary_files, n_jobs=n_jobs, **kwargs)
