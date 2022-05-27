"""A module for API wrappers."""
import json
from pathlib import Path

parent_dir = Path(__file__).parents[0]

engine_metadata = None
with open(parent_dir / "engine_metadata.json", "r") as fp:
    engine_metadata = json.load(fp)
