import json
from pathlib import Path


def diff(root_path: Path):
    old_json = root_path / 'licsber-bak-old.json'
    new_json = root_path / 'licsber-bak.json'

    old_json = json.load(old_json.open())
    new_json = json.load(new_json.open())

    for file in old_json['files']:
        if file not in new_json['files']:
            print(file)


if __name__ == '__main__':
    diff(Path('/Volumes/LicsberC/Vol.01 无解说美食制作视频系列等 工作背景音睡前治愈'))
