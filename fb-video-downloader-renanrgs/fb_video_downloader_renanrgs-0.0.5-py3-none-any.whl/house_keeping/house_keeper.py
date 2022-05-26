from pathlib import Path


def delete_temp_files(dir: str):
    root_path = Path(dir)
    tmp_video_path = root_path.iterdir()
    for file in tmp_video_path:
        file.unlink(missing_ok=True)

def delete_file(file: str):
    path = Path(file)
    path.unlink(missing_ok=True)