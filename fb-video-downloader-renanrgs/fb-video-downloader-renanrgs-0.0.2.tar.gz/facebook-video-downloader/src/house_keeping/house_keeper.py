from pathlib import Path


def delete_temp_files():
    path = Path(__file__).parents[2] / 'tmp'
    tmp_video_path = path.iterdir()
    for file in tmp_video_path:
        file.unlink(missing_ok=True)
