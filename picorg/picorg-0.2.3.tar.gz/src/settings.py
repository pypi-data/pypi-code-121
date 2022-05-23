import json
from pathlib import Path
from typing import List

from pydantic import BaseModel

SETTINGS_DIR = Path(Path.home(), ".picorg")


class Settings(BaseModel):
    file_path: Path = Path()
    pic_paths: List[Path] = []

    @staticmethod
    def from_file(file_path: Path) -> "Settings":
        if file_path.exists():
            settings = Settings.parse_file(file_path)
            settings.file_path = file_path
            return settings
        file_path.parent.mkdir(exist_ok=True, parents=True)
        settings = Settings()
        settings.file_path = file_path
        settings.save()
        return settings

    def save(self) -> None:
        with open(self.file_path, "w") as f:
            f.write(
                json.dumps(self.dict(exclude={"file_path"}), sort_keys=True, indent=4)
            )


if __name__ == "__main__":
    settings = Settings.from_file(Path(Path.cwd(), ".picorg", "settings.json"))
    print(settings.dict())
    settings.save()
