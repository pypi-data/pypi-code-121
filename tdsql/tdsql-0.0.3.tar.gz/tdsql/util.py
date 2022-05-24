from pathlib import Path


def read(filepath: Path) -> str:
    with open(filepath, "r") as file:
        res = file.read()
    return res


def write(filepath: Path, text: str) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(text)
