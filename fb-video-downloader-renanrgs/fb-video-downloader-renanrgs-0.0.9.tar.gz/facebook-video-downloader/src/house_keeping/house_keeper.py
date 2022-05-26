from pathlib import Path


def delete_temp_files(dir: Path):
    
    for file in dir.iterdir():
        if file.suffix == '.mp4':
            file.unlink(missing_ok=True)
