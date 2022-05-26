from pathlib import Path


def delete_temp_files(dir: str):
    root_path = Path(dir)
    tmp_video_path = root_path.iterdir()
    for file in tmp_video_path:
        if file.suffix != 'py':
            file.unlink(missing_ok=True)
