from __future__ import annotations
from pathlib import Path
from .package import Package

system_dir = Path(__file__).parent / "../data/system"
system_package = Package(system_dir)
