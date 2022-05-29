import subprocess
import sys
from pathlib import Path

from licsber.utils.ufile import fun_check_path_exist
from licsber.utils.utime import cal_time

dry_run = False


def merge_videos(video_list_path: Path, save_path: Path):
    video_list_path = str(video_list_path)
    save_path = str(save_path)
    cmd = ['ffmpeg', '-y', '-nostdin',
           '-f', 'concat', '-safe', '0',
           '-i', video_list_path,
           '-c:v', 'copy', '-c:a', 'flac',
           '-strict', '-2',
           save_path]

    if dry_run:
        print(' '.join(cmd))
        return None

    return subprocess.Popen(cmd)


def process_dir(root_path: Path, save_path: Path = None):
    root_path = root_path.resolve(strict=True)
    print(f"开始合并: {root_path}")
    if save_path is None:
        save_path = root_path / (root_path.name + '.mp4')

    files = [f"file '{i.resolve(strict=True)}'" for i in root_path.glob('*.mp4') if i != save_path]
    files.extend([f"file '{i.resolve(strict=True)}'" for i in root_path.glob('*.webm') if i != save_path])
    if len(files) == 0:
        print(f"目录为空: {root_path}")
        return None

    files.sort()
    video_list_path = root_path / 'video_list.txt'
    video_list_path.write_text('\n'.join(files), encoding='utf-8')

    return merge_videos(video_list_path, save_path)


@cal_time(output=True)
@fun_check_path_exist(clean=True)
def merge_dirs(start_path: str = None):
    global dry_run

    dry_run = '-n' in sys.argv

    root = Path(start_path)
    single_merge = len(list(root.glob('*.mp4'))) != 0
    if single_merge:
        print('合并此文件夹的所有视频.')
        sub = process_dir(root, root.parent / (root.name + '.mp4'))
        if sub:
            sub.wait()

        return

    subs = []
    for d in root.iterdir():
        if not d.is_dir():
            continue

        d = d.resolve(strict=True)
        save_path = d.parent / (d.name + '.mp4')
        sub = process_dir(d, save_path)
        if sub:
            subs.append(sub)

    [i.wait() for i in subs]
