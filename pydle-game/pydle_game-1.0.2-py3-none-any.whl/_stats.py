#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""
Pydle game player statistics
"""

import json
from collections import Counter
from pathlib import Path
from typing import List, Optional

from . import app_paths


StatData = List[dict]


class Stats:
    def __init__(self):
        self._datastore = Path(app_paths.app_data_path) / "player_stats.jsonl"
        self._stats: Optional[StatData] = None

    def update(self, game_stats: dict) -> None:
        """Update player stats with new game"""
        with self._datastore.open("a+") as fileobj:
            print(json.dumps(game_stats), file=fileobj)

    def get_stats(self) -> StatData:
        """Read player stats file"""
        if not self._stats:
            _stats = []
            with self._datastore.open("r") as fileobj:
                for line in fileobj.readlines():
                    _stats.append(json.loads(line))
            self._stats = _stats
        return self._stats

    def parse_stats(self, data: Optional[StatData] = None) -> dict:
        """Parse stats file for total info"""
        data = data or self.get_stats()
        return {
            "games": len(data),
            "wins": sum(1 for row in data if row.get("found", False) == True),
            "attempts": Counter([row.get("attempts") for row in data if row.get("found")]),
        }


if __name__ == "__main__":
    print("This is not the py you seek")
