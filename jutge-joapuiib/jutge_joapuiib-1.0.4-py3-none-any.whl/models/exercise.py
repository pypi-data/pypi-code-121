from .unit_test import UnitTest

class Exercise(UnitTest):
    def __init__(self, name, _dict={}):
        super().__init__(name, _dict)

        if not _dict:
            _dict = {}

        self.subpackage = _dict.get("subpackage", "")

    def get_result(self):
        return super().get_result()
