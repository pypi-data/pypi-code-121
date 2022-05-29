import os
from pathlib import Path
from typing import Set, Tuple

import cv2
import numpy as np
import tqdm

from licsber.utils.ucli import check_force
from licsber.utils.ufile import fun_check_path_exist
from licsber.utils.utime import cal_time

BLACKLIST_DIR = {'.@__thumb'}
VIDEO_SUFFIX = {'.mp4', '.mkv', '.avi', '.flv', '.hevc', '.wmv', '.mpg', '.mov', '.ts', '.rmvb', '.webm'}
assert '.jpg' not in VIDEO_SUFFIX
COMMON_SUFFIX = {'.jpg', '.nfo', '.ass', '.gif', '.json', '.html', '.iso', '.png', '.txt', '.zip', '.webp'}


def thumb_nail(
        video_path: Path,
        img_num: int = 64,
        map_width: int = 8,
        map_size: Tuple[int, int] = None,
        force: bool = False
) -> bool:
    if not map_size:
        map_size = (2160, 3840, 3)

    save_path = video_path.parent / ('Thumb_' + video_path.name.replace(video_path.suffix, '.jpg'))
    if save_path.exists():
        if save_path.stat().st_size != 8:
            print(f"\t{save_path} 已存在.")
            return True

    save_path.write_text('Licsber.')
    video = cv2.VideoCapture(str(video_path))
    suc, bgr = video.read()
    if not suc:
        return False

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_idx = [i for i in range(0, total_frames, total_frames // img_num + 1)]

    height, width, _ = bgr.shape
    vertical = width < height
    if vertical:
        map_width *= 2

    map_height = img_num // map_width
    resize_height = map_size[0] // map_height
    resize_width = map_size[1] // map_width
    resize_shape = (resize_width, resize_height)

    row, col = 0, 0
    res_map = np.zeros(map_size, dtype=np.uint8)
    with tqdm.tqdm(total=len(frames_idx)) as t:
        t.set_description(f"竖版: {vertical} " + video_path.name)
        for idx in frames_idx:
            video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            suc, bgr = video.read()
            if not suc and not force:
                return False

            if suc:
                bgr = cv2.resize(bgr, resize_shape)
                res_map[row * resize_height:(row + 1) * resize_height,
                col * resize_width:(col + 1) * resize_width] = bgr
            else:
                print(f"{video_path} 读取失败.")

            col += 1
            if col >= map_width:
                col = 0
                row += 1

            t.update()

    cv2.imwrite(str(save_path), res_map)
    return True


@cal_time(output=True)
@fun_check_path_exist(clean=True)
def thumb_from_dir(start_path: str = None, video_suffix: Set[str] = None):
    force = not check_force()
    if not video_suffix:
        video_suffix = VIDEO_SUFFIX

    if os.path.isfile(start_path):
        thumb_nail(Path(start_path), force=force)
        return

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in BLACKLIST_DIR]
        root_path = Path(root)
        files.sort()
        for file in files:
            video_path = root_path / file
            suffix = video_path.suffix.lower()
            if suffix not in video_suffix:
                if suffix not in COMMON_SUFFIX:
                    print(f"{file} 跳过.")

                continue

            suc = thumb_nail(video_path, force=force)
            if not suc:
                print(f"{video_path} 视频错误.")
                if not force:
                    return False

                continue
