from typing import Any

class Map:
    def __init__(self):
        self.map = {}
        self.counter = 0

    def incr(self):
        self.counter += 1

    def get(self, key) -> Any:
        return self.map[key]

    def get_key(self, value) -> int:
        for k, v in self.map.items():
            if v == value:
                return k

        return None

    def insert(self, value) -> int:
        index = self.counter
        self.map[index] = value
        self.incr()

        return index

    def remove(self, index: int):
        return self.map.pop(index)
