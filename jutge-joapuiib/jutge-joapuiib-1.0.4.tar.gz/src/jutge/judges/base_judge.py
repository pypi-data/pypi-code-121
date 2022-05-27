import os
from ..models.exercise import Exercise
from pprint import pprint

class BaseJudge:
    def __init__(self, base_dir, tests, args):
        self.base_dir = base_dir

        self.exercises = []
        for name, exercise in tests.get("exercises", {}).items():
            self.exercises.append(Exercise(name, exercise))

        self.volumes = args.volume
        self.volumes.extend(tests.get("volumes", []))

        self.verbose = args.verbose


