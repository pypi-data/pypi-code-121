from pathlib import Path


__VIDEO_FORMATS = ('.mp4', '.webm')

def delete_temp_files(dir: Path = Path()):
    
    for file in dir.iterdir():
        if file.suffix in __VIDEO_FORMATS:
            file.unlink(missing_ok=True)
