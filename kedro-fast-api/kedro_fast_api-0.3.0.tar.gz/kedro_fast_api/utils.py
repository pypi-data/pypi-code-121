from pathlib import Path

def project_path(file_name: str):
    return Path(__file__).parent / f"./{file_name}"