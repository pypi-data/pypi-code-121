import json


class Usage:
    """
    This object is used in some of the attributes of FileSystem.
    """
    def __init__(self, usage_data: dict):
        self.total: int = usage_data.get('total', 0)
        self.used: int = usage_data.get('used', 0)
        self.used_by_free_blocks: int = usage_data.get('used_by_free_blocks', 0)
        self.free: int = usage_data.get('free', 0)
        self.percent: int = usage_data.get('percent', 0)

    def as_dict(self) -> dict:
        return_dict = json.loads(json.dumps(self, default=self.object_dumper))
        return {k: v for k, v in return_dict.items() if v is not None}

    @staticmethod
    def object_dumper(obj) -> dict:
        try:
            return obj.__dict__
        except:
            pass

    def serialize(self) -> dict:
        return self.as_dict()
